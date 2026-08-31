"""End-to-end golden path test for the decision engine (mock mode).

The full flow: input -> bias flags -> stance divergence -> probing ->
option-space map (consensus / true / false divergence) -> constraint
backfill -> human decision. The system never picks a winner.
"""

import pytest

from backend.engine import (
    apply_constraints,
    record_human_decision,
    run_decision,
)
from backend.models import ConstraintRequest, HumanDecisionRequest


@pytest.mark.asyncio
async def test_golden_path_scenario_a():
    decision = await run_decision(
        "I need to build a CRM. I only know Java Spring."
    )

    # Bias detected
    assert any(f["kind"] == "anchored_stack" for f in decision.bias_flags)

    # Stance divergence: 5 stances responded
    assert len(decision.stance_divergence) == 5
    stances = {d["stance"] for d in decision.stance_divergence}
    assert stances == {"architect", "cost", "security", "product", "red_team"}

    # Probing: 3 answers
    assert len(decision.probing_answers) == 3

    # Option-space map: consensus contains the open-source CRM base
    consensus = decision.option_space_map.consensus_zone
    assert len(consensus) >= 1
    canonicals = [o.canonical for o in consensus]
    assert "open-source-crm-base" in canonicals

    # True divergence has the buy-SaaS option tagged "didn't know"
    true_div = decision.option_space_map.true_divergence_zone
    buy = [o for o in true_div if o.canonical == "buy-saas-crm"]
    assert buy and buy[0].novelty == "you_probably_didnt_know"

    # No winner picked
    assert decision.human_decision["status"] == "pending"


@pytest.mark.asyncio
async def test_constraint_backfill_reorders():
    decision = await run_decision("I need to build a CRM. I only know Java Spring.")
    req = ConstraintRequest(decision_id=decision.decision_id, constraints=["budget", "deadline"])
    updated = apply_constraints(req)
    assert updated is not None
    scored = updated.constraint_evaluation
    assert scored is not None
    scores = [o.get("weighted_score") for o in scored]
    assert all(s is not None for s in scores)
    # sorted descending
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_human_decision_recorded_no_winner():
    decision = await run_decision("I need to build a CRM. I only know Java Spring.")
    req = HumanDecisionRequest(
        decision_id=decision.decision_id,
        chosen_option="open-source-crm-base",
        rationale="We need data residency.",
    )
    updated = record_human_decision(req)
    assert updated is not None
    assert updated.human_decision["status"] == "decided"
    assert updated.human_decision["chosen_option"] == "open-source-crm-base"
