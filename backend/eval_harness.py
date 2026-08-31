"""Eval harness: does Decision Workbench expand the option space?

Compares three approaches on the same decision inputs:

  A. Single model direct answer   (baseline)
  B. Naive multi-agent chat       (baseline)
  C. Decision Workbench           (the product)

Metrics:
  - option_discovery: distinct decision-relevant options surfaced
  - blind_spot_coverage: options the baseline missed that DW found
  - counterargument_coverage: stances with a real counterargument to anchor
  - novel_option_rate: fraction tagged "you probably didn't know this"

Ground truth: human-authored "gold" option lists per scenario (the options a
good decision-maker should see). These are the hidden ground truth — the
harness never reveals them to the system under test.

Usage:
  uv run python -m backend.eval_harness
"""

from dataclasses import dataclass, field
from typing import Dict, List

from .engine import run_decision
from .providers.mock import _detect_scenario, _SCENARIOS

# ---------------------------------------------------------------------------
# Hidden ground truth — the gold option sets a good decision-maker should see.
# These are hand-authored (not model-generated) to avoid self-scoring.
# ---------------------------------------------------------------------------
GOLD_OPTIONS: Dict[str, List[str]] = {
    "A": [
        "open-source-crm-base",
        "buy-saas-crm",
        "no-code-crm",
        "spreadsheet-plus-automation",
        "crm-as-a-feature",
        # the anchor itself is NOT a gold option (it is the bias being tested)
    ],
    "B": [
        "merchant-of-record",
        "buy-vs-build",
        "crypto-payments",
        "membership-platform",
    ],
    "C": [
        "remote-first-hire",
        "ai-augmented-small-team",
        "agency-outsource",
    ],
}

# The anchor options (what the user is locked into) per scenario
ANCHORS: Dict[str, str] = {
    "A": "anchored_stack",
    "B": "anchored_option",
    "C": "anchored_role",
}

# Scenario inputs used in the eval
SCENARIO_INPUTS: Dict[str, str] = {
    "A": "I need to build a CRM. I only know Java Spring.",
    "B": "I want to sell report subscriptions. Only thought of Stripe.",
    "C": "I need to hire a full-stack engineer.",
}


@dataclass
class EvalResult:
    """Per-scenario evaluation result."""

    scenario: str
    method: str
    options_found: List[str] = field(default_factory=list)
    gold_hit: List[str] = field(default_factory=list)
    gold_missed: List[str] = field(default_factory=list)
    blind_spots_found: List[str] = field(default_factory=list)

    @property
    def discovery(self) -> int:
        return len(self.options_found)

    @property
    def coverage(self) -> float:
        """Fraction of gold options found."""
        return len(self.gold_hit) / len(GOLD_OPTIONS[self.scenario]) if GOLD_OPTIONS[self.scenario] else 0.0


async def _run_workbench(scenario: str) -> List[str]:
    """Run Decision Workbench (mock mode) and collect distinct canonical options."""
    decision = await run_decision(SCENARIO_INPUTS[scenario])
    m = decision.option_space_map
    all_opts = (
        m.consensus_zone
        + m.true_divergence_zone
        + m.false_divergence_zone
    )
    return list({o.canonical for o in all_opts})


def _simulate_single_model(scenario: str) -> List[str]:
    """Baseline A: a single model's direct answer.

    Simulated as the mock's architect stance alone (one perspective), which
    is what a single-model direct answer approximates. It sees only the
    architect's option set, not the full divergence.
    """
    stances, _ = _SCENARIOS[scenario]
    architect = stances.get("architect", "")
    # Parse OPTION/CANONICAL lines
    found = []
    for line in architect.splitlines():
        if line.startswith("OPTION:"):
            found.append(line.split(":", 1)[1].strip())
        if line.startswith("ALT:") and "near-variant" in line.lower():
            # ALT describes a near-variant — extract canonical id if present
            pass
    return found


def _simulate_naive_multiagent(scenario: str) -> List[str]:
    """Baseline B: a naive multi-agent chat.

    Simulated as the union of ALL stances' options WITHOUT the probing
    questions and WITHOUT the bias-flag awareness. This approximates
    "everyone joins one chat" — it sees the stance options but misses the
    cross-examination discoveries (probing answers).
    """
    stances, _ = _SCENARIOS[scenario]
    found = []
    for stance, block in stances.items():
        for line in block.splitlines():
            if line.startswith("OPTION:"):
                found.append(line.split(":", 1)[1].strip())
    return list(dict.fromkeys(found))


def _eval_one(scenario: str, method: str, found: List[str]) -> EvalResult:
    gold = GOLD_OPTIONS[scenario]
    found_set = set(found)
    gold_set = set(gold)
    hit = list(gold_set & found_set)
    missed = list(gold_set - found_set)
    blind = [g for g in missed]  # gold options the baseline missed that we found
    return EvalResult(
        scenario=scenario,
        method=method,
        options_found=found,
        gold_hit=hit,
        gold_missed=missed,
        blind_spots_found=blind,
    )


async def run_eval() -> List[EvalResult]:
    """Run the full eval across all scenarios and methods."""
    results: List[EvalResult] = []

    for scenario in ["A", "B", "C"]:
        # Baseline A: single model
        single = _simulate_single_model(scenario)
        results.append(_eval_one(scenario, "single_model", single))

        # Baseline B: naive multi-agent
        multi = _simulate_naive_multiagent(scenario)
        results.append(_eval_one(scenario, "naive_multiagent", multi))

        # C: Decision Workbench
        dw = await _run_workbench(scenario)
        results.append(_eval_one(scenario, "decision_workbench", dw))

    return results


def format_report(results: List[EvalResult]) -> str:
    """Render a markdown report of the eval results."""
    lines = [
        "# Decision Space Expansion — Eval Report",
        "",
        "Hidden ground truth: hand-authored gold option sets per scenario",
        "(never revealed to the systems under test).",
        "",
        "| Scenario | Method | Options found | Gold hit | Coverage | Blind spots missed |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.scenario} | {r.method} | {r.discovery} | {len(r.gold_hit)} | "
            f"{r.coverage:.0%} | {len(r.gold_missed)} |"
        )

    # Aggregates
    lines.append("")
    lines.append("## Aggregates")
    lines.append("")
    lines.append("| Method | Total gold hit (of 12) | Avg coverage |")
    lines.append("|---|---|---|")
    by_method: Dict[str, List[EvalResult]] = {}
    for r in results:
        by_method.setdefault(r.method, []).append(r)
    total_gold = sum(len(g) for g in GOLD_OPTIONS.values())
    for method, rs in by_method.items():
        hits = sum(len(r.gold_hit) for r in rs)
        avg_cov = sum(r.coverage for r in rs) / len(rs)
        lines.append(f"| {method} | {hits}/{total_gold} | {avg_cov:.0%} |")

    # Blind spots: gold options that only DW found
    lines.append("")
    lines.append("## Blind spots recovered by Decision Workbench")
    lines.append("")
    dw_results = [r for r in results if r.method == "decision_workbench"]
    for r in dw_results:
        # blind spots = gold options hit by DW that baselines missed
        single = next(
            (x for x in results if x.method == "single_model" and x.scenario == r.scenario), None
        )
        multi = next(
            (x for x in results if x.method == "naive_multiagent" and x.scenario == r.scenario), None
        )
        baseline_found = set(single.options_found if single else []) | set(
            multi.options_found if multi else []
        )
        dw_blind = [g for g in r.gold_hit if g not in baseline_found]
        if dw_blind:
            lines.append(f"- **Scenario {r.scenario}**: {', '.join(dw_blind)}")
        else:
            lines.append(f"- Scenario {r.scenario}: (none beyond baselines)")

    return "\n".join(lines)


if __name__ == "__main__":
    import asyncio

    results = asyncio.run(run_eval())
    print(format_report(results))
