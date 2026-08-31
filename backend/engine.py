"""The decision engine: bias -> stance divergence -> probing -> option-space
map -> (constraints) -> human decision.

This is the full pipeline that implements the product philosophy:
  - expand the option space (divergence)
  - surface blind spots (novelty tags, probing questions)
  - structure the map (consensus / true divergence / false divergence)
  - hand the decision back to a human (NEVER auto-pick a winner)
"""

import asyncio
import re
import uuid
from typing import Any, Dict, List, Optional

from . import constraints as constraints_mod
from . import options as options_mod
from .bias import detect_bias
from .config import STANCES
from .models import ConstraintRequest, DecideResponse, HumanDecisionRequest
from .probing import build_probing_prompt, probing_questions
from .providers import get_provider
from .stances import stance_prompts


def _extract_anchor(user_input: str) -> Optional[str]:
    """Extract a canonical anchor id from the user's input for novelty tagging."""
    lower = user_input.lower()
    if "spring" in lower or "java" in lower:
        return "anchored_stack"
    if "stripe" in lower:
        return "anchored_option"
    if "hire" in lower or "full-stack" in lower or "full stack" in lower:
        return "anchored_role"
    return None


def _detect_scenario(user_input: str) -> str:
    """Detect which demo scenario the input matches (A/B/C), default A."""
    lower = user_input.lower()
    if any(k in lower for k in ["crm", "java spring", "spring boot", "tech stack"]):
        return "A"
    if any(k in lower for k in ["subscription", "stripe", "report", "payment"]):
        return "B"
    if any(k in lower for k in ["hire", "full-stack", "full stack", "recruit", "team"]):
        return "C"
    return "A"


class DecisionStore:
    """In-memory store keyed by decision_id (MVP scope)."""

    def __init__(self) -> None:
        self._decisions: Dict[str, DecideResponse] = {}

    def put(self, decision: DecideResponse) -> None:
        self._decisions[decision.decision_id] = decision

    def get(self, decision_id: str) -> Optional[DecideResponse]:
        return self._decisions.get(decision_id)


store = DecisionStore()


async def run_decision(user_input: str) -> DecideResponse:
    """Run the full decision pipeline and return the response."""
    provider = get_provider()

    decision_id = uuid.uuid4().hex[:12]
    scenario = _detect_scenario(user_input)
    anchor = _extract_anchor(user_input)
    bias_flags = detect_bias(user_input)

    # --- Stage: stance divergence (parallel) -------------------------------
    stance_prompts_map = stance_prompts()
    divergence: List[Dict[str, Any]] = []

    async def _ask_stance(stance: str) -> None:
        system = stance_prompts_map.get(stance, "")
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f"The decision being made:\n{user_input}\n\n"
                    "Give your option for this decision."
                ),
            },
        ]
        model = f"mock/{stance}" if provider.name == "mock" else provider.list_models()[0]
        resp = await provider.query(model, messages)
        content = resp.get("content", "") if resp else ""
        divergence.append({"stance": stance, "response": content})

    await asyncio.gather(*[_ask_stance(s) for s in STANCES])

    # --- Stage: probing questions (parallel) -------------------------------
    probes = probing_questions()
    probing_answers: List[Dict[str, str]] = []

    async def _ask_probe(probe: Dict[str, str]) -> None:
        messages = [
            {"role": "user", "content": build_probing_prompt(probe, user_input)}
        ]
        model = "mock/red_team" if provider.name == "mock" else provider.list_models()[0]
        resp = await provider.query(model, messages)
        content = resp.get("content", "") if resp else ""
        probing_answers.append({"question": probe["question"], "answer": content})

    await asyncio.gather(*[_ask_probe(p) for p in probes])

    # --- Option extraction + zone classification ---------------------------
    all_blocks: List[Dict[str, str]] = []
    for item in divergence:
        all_blocks.extend(options_mod.extract_options(item["response"]))
    for ans in probing_answers:
        all_blocks.extend(options_mod.extract_options(ans["answer"]))

    # Tag novelty before classification (mock answers already carry it, but
    # real providers may not — the rules fill the gaps).
    options_mod.tag_novelty(all_blocks, anchor_canonical=anchor)
    consensus, true_div, false_div = options_mod.classify_zones(all_blocks, anchor_canonical=anchor)

    option_space_map = {
        "consensus_zone": consensus,
        "true_divergence_zone": true_div,
        "false_divergence_zone": false_div,
    }

    response = DecideResponse(
        decision_id=decision_id,
        input=user_input,
        scenario=scenario,
        bias_flags=bias_flags,
        stance_divergence=divergence,
        probing_questions=probes,
        probing_answers=probing_answers,
        option_space_map=option_space_map,
        constraint_evaluation=None,
        human_decision={
            "status": "pending",
            "message": "The decision is yours. Review the map, weigh the trade-offs, then decide.",
        },
    )
    store.put(response)
    return response


def apply_constraints(req: ConstraintRequest) -> Optional[DecideResponse]:
    """Re-score the option map against the selected constraints."""
    decision = store.get(req.decision_id)
    if decision is None:
        return None

    all_options = (
        decision.option_space_map.consensus_zone
        + decision.option_space_map.true_divergence_zone
        + decision.option_space_map.false_divergence_zone
    )
    # Pydantic models -> dicts for the scorer (it uses .get()).
    as_dicts = [o.model_dump() for o in all_options]
    scored = constraints_mod.weighted_evaluate(as_dicts, req.constraints)
    decision.constraint_evaluation = scored
    return decision


def record_human_decision(req: HumanDecisionRequest) -> Optional[DecideResponse]:
    """Record the human's final choice. The system never picks a winner."""
    decision = store.get(req.decision_id)
    if decision is None:
        return None

    decision.human_decision = {
        "status": "decided",
        "chosen_option": req.chosen_option,
        "rationale": req.rationale,
        "message": "Recorded. The decision is yours.",
    }
    return decision
