"""Mock provider: returns pre-baked heterogeneous proposals so the full
divergence -> map -> human-decision loop can be exercised with zero API keys.

The mock simulates five *cognitively different* stances (architect / cost /
security / product / red_team) with deterministic, self-consistent answers
for the three demo scenarios in docs/scenarios.md:

  A. Tech stack selection  ("I need to build a CRM. I only know Java Spring.")
  B. Business decision    ("Sell English report subscriptions. Only thought of Stripe.")
  C. Hiring decision      ("I need to hire a full-stack engineer.")

The mock answers follow the *shape* of real answers: each stance defends its
angle, disagrees with the others on real dimensions, and the red_team attacks
the user's anchored choice. This guarantees the demo NEVER depends on a live
API or network.
"""

from typing import Any, Dict, List, Optional

from .base import BaseProvider


def _detect_scenario(user_text: str) -> str:
    """Detect which demo scenario the input matches (A/B/C), default A."""
    lower = user_text.lower()
    if any(k in lower for k in ["crm", "java spring", "spring boot", "tech stack"]):
        return "A"
    if any(k in lower for k in ["subscription", "stripe", "report", "payment"]):
        return "B"
    if any(k in lower for k in ["hire", "full-stack", "full stack", "recruit", "team"]):
        return "C"
    return "A"


# ---------------------------------------------------------------------------
# Scenario A: tech stack (CRM / Java Spring anchor)
# ---------------------------------------------------------------------------
_SCENARIO_A_STANCES: Dict[str, str] = {
    "architect": (
        "OPTION: open-source-crm-base\n"
        "CANONICAL: open-source-crm-base\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: Mature open-source CRM bases exist (e.g. twenty, Fathom CRM, "
        "erxes) with contacts, pipeline, permissions already solved. Building "
        "a CRM from scratch is reinventing the wheel.\n"
        "ALT: A Go/TypeScript rewrite of your own CRM is a near-variant of the "
        "Java Spring anchor — same build-from-scratch risk, different language."
    ),
    "cost": (
        "OPTION: buy-saas-crm\n"
        "CANONICAL: buy-saas-crm\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: For most CRM needs, buying SaaS (HubSpot free tier, Zoho, "
        "Twenty Cloud) is cheaper than building. Total cost of a 6-month "
        "build >> a year of SaaS.\n"
        "SUPPORTS: open-source-crm-base\n"
        "ALT: A Go/TypeScript rewrite is a near-variant of the Java Spring anchor."
    ),
    "security": (
        "SUPPORTS: open-source-crm-base\n"
        "REASON: Self-hosted open-source CRM keeps customer data on your own "
        "infra (data residency, compliance). SaaS means third-party data "
        "handling.\n"
        "ALT: A Go/TypeScript rewrite is a near-variant of the Java Spring anchor."
    ),
    "product": (
        "OPTION: no-code-crm\n"
        "CANONICAL: no-code-crm\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: For a small team, no-code/low-code CRM builders (Airtable, "
        "NocoDB) ship in days, not months. You get the CRM behavior without "
        "owning the code.\n"
        "ALT: A Go/TypeScript rewrite is a near-variant of the Java Spring anchor."
    ),
    "red_team": (
        "ATTACK: anchored_stack\n"
        "REASON: 'I only know Java Spring' is a classic anchoring bias. The "
        "stack choice is orthogonal to the CRM problem — you are solving "
        "'contacts + pipeline + permissions', which open-source CRMs already "
        "solve. Building from scratch in ANY language is the risky path.\n"
        "SUPPORTS: open-source-crm-base"
    ),
}

_SCENARIO_A_PROBING: Dict[str, str] = {
    "excluded_option": (
        "OPTION: crm-as-a-feature\n"
        "CANONICAL: crm-as-a-feature\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: You likely excluded 'embedding an existing CRM as a feature' "
        "because you assumed it must be built standalone. For many products, "
        "a CRM is a feature (integrate an open-source core), not a product."
    ),
    "non_mainstream": (
        "OPTION: spreadsheet-plus-automation\n"
        "CANONICAL: spreadsheet-plus-automation\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: For under ~10 users, a spreadsheet + automation (Airtable, "
        "n8n) IS a CRM. Non-mainstream but with a real reason: near-zero "
        "cost, instant start, no maintenance."
    ),
    "weakest_point": (
        "TARGET: anchored_stack\n"
        "REASON: Your Java Spring CRM from scratch has the weakest points: "
        "6+ months to feature parity with open source, ongoing maintenance "
        "forever, and the stack choice was made by familiarity, not by "
        "requirements."
    ),
}

# ---------------------------------------------------------------------------
# Scenario B: business (report subscriptions / Stripe anchor)
# ---------------------------------------------------------------------------
_SCENARIO_B_STANCES: Dict[str, str] = {
    "architect": (
        "OPTION: merchant-of-record\n"
        "CANONICAL: merchant-of-record\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: Lemon Squeezy / Paddle are merchants of record — they handle "
        "global sales tax, VAT, and invoicing for you. Stripe alone requires "
        "your own entity + tax compliance per country.\n"
        "ALT: Stripe + Stripe Tax is a near-variant of the Stripe anchor."
    ),
    "cost": (
        "SUPPORTS: merchant-of-record\n"
        "REASON: Merchant-of-record fee (5% + $0.50) is cheaper than the "
        "accounting/tax-entity overhead of going direct with Stripe at small "
        "volume.\n"
        "ALT: A self-hosted payment stack is a near-variant of the Stripe anchor."
    ),
    "security": (
        "OPTION: crypto-payments\n"
        "CANONICAL: crypto-payments\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: For a global digital report audience, crypto (USDC/Lightning) "
        "removes chargeback and cross-border friction entirely. Privacy "
        "preserving, no KYC for the seller in most cases.\n"
        "SUPPORTS: merchant-of-record"
    ),
    "product": (
        "OPTION: buy-vs-build\n"
        "CANONICAL: buy-vs-build\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: You may not need payment code at all — a membership platform "
        "(Gumroad, Ghost memberships, Paddle) can deliver subscriptions + "
        "payments + member area out of the box.\n"
        "ALT: Stripe is a near-variant of the Stripe anchor."
    ),
    "red_team": (
        "ATTACK: anchored_option\n"
        "REASON: 'Only thought of Stripe' means you never asked who handles "
        "tax. For selling to overseas customers, Stripe's US-entity + per-"
        "country tax problem can stop you before you start. Merchant-of-record "
        "exists precisely to solve this.\n"
        "SUPPORTS: merchant-of-record"
    ),
}

_SCENARIO_B_PROBING: Dict[str, str] = {
    "excluded_option": (
        "OPTION: membership-platform\n"
        "CANONICAL: buy-vs-build\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: You excluded 'use a membership platform' because you assumed "
        "payment must be integrated by you. Ghost/Gumroad/Paddle deliver the "
        "whole subscription loop."
    ),
    "non_mainstream": (
        "OPTION: crypto-payments\n"
        "CANONICAL: crypto-payments\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: Non-mainstream but real: a global digital audience can pay "
        "in USDC with zero chargebacks and no cross-border fees."
    ),
    "weakest_point": (
        "TARGET: anchored_option\n"
        "REASON: Stripe alone has the weakest point: you own tax compliance "
        "in every country you sell to. That is a legal/accounting burden, not "
        "an engineering one."
    ),
}

# ---------------------------------------------------------------------------
# Scenario C: hiring (full-stack anchor)
# ---------------------------------------------------------------------------
_SCENARIO_C_STANCES: Dict[str, str] = {
    "architect": (
        "OPTION: remote-first-hire\n"
        "CANONICAL: remote-first-hire\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: A remote-first hire (or overseas contractor) widens the "
        "talent pool 10x and cuts cost 30-50% vs local full-time.\n"
        "ALT: A local full-time hire is a near-variant of the full-stack anchor."
    ),
    "cost": (
        "OPTION: ai-augmented-small-team\n"
        "CANONICAL: ai-augmented-small-team\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: For a 3-month MVP, one AI-augmented senior + a part-time "
        "contractor often beats a full-time hire at half the cost.\n"
        "ALT: A local full-time hire is a near-variant of the full-stack anchor."
    ),
    "security": (
        "SUPPORTS: ai-augmented-small-team\n"
        "REASON: Smaller team + AI tooling = smaller attack surface, fewer "
        "access grants, easier audit than a growing headcount.\n"
        "ALT: A local full-time hire is a near-variant of the full-stack anchor."
    ),
    "product": (
        "OPTION: agency-outsource\n"
        "CANONICAL: agency-outsource\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: For a bounded scope, a specialist agency delivers the MVP "
        "with a fixed price and deadline — no hiring risk, no retention cost.\n"
        "ALT: A local full-time hire is a near-variant of the full-stack anchor."
    ),
    "red_team": (
        "ATTACK: anchored_role\n"
        "REASON: 'I need to hire a full-stack engineer' assumes the problem is "
        "headcount. For an MVP, the real question is 'what's the fastest "
        "reliable way to ship' — which may be AI-augmented solo + contractor, "
        "not a hire.\n"
        "SUPPORTS: ai-augmented-small-team"
    ),
}

_SCENARIO_C_PROBING: Dict[str, str] = {
    "excluded_option": (
        "OPTION: agency-outsource\n"
        "CANONICAL: agency-outsource\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: You excluded 'outsource the whole thing' because you assumed "
        "headcount is the answer. Fixed-scope agency work removes hiring risk."
    ),
    "non_mainstream": (
        "OPTION: ai-augmented-small-team\n"
        "CANONICAL: ai-augmented-small-team\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: Non-mainstream but real in 2026: a 1-person AI-augmented "
        "team ships an MVP that used to need 3 people."
    ),
    "weakest_point": (
        "TARGET: anchored_role\n"
        "REASON: 'Hire a full-stack' has the weakest point: a full-time hire "
        "is slow (weeks to onboard), expensive (salary + benefits), and "
        "risky (retention) for a 3-month MVP window."
    ),
}

# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
_SCENARIOS = {
    "A": (_SCENARIO_A_STANCES, _SCENARIO_A_PROBING),
    "B": (_SCENARIO_B_STANCES, _SCENARIO_B_PROBING),
    "C": (_SCENARIO_C_STANCES, _SCENARIO_C_PROBING),
}


class MockProvider(BaseProvider):
    """Deterministic provider returning canned heterogeneous stance answers."""

    name = "mock"
    models = [
        "mock/architect",
        "mock/cost",
        "mock/security",
        "mock/product",
        "mock/red_team",
    ]

    def _parse_block(self, text: str) -> Dict[str, str]:
        """Parse KEY: value lines from a mock answer block."""
        result: Dict[str, str] = {}
        for line in text.strip().splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip()] = val.strip()
        return result

    async def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 60.0,
    ) -> Optional[Dict[str, Any]]:
        if model not in self.models:
            return None

        user_text = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_text = m.get("content", "")
                break

        scenario = _detect_scenario(user_text)
        stances, probing = _SCENARIOS[scenario]

        # Decide what this call is asking for: a stance proposal, or a
        # probing-question answer. For probing, match the question id from
        # the prompt (excluded_option / non_mainstream / weakest_point).
        lower = user_text.lower()
        probing_id = None
        if "excluded_option" in lower or "why did you not consider" in lower:
            probing_id = "excluded_option"
        elif "non_mainstream" in lower or "non-mainstream" in lower:
            probing_id = "non_mainstream"
        elif "weakest_point" in lower or "weakest point" in lower:
            probing_id = "weakest_point"

        stance = model.split("/")[-1]  # architect | cost | security | product | red_team

        if probing_id:
            content = probing.get(probing_id, probing.get("excluded_option", ""))
        else:
            content = stances.get(stance, "")

        return {"content": content}

    def list_models(self) -> List[str]:
        return self.models
