"""Constraint backfill + weighted evaluation.

After the option-space map is shown, the human checks their REAL constraints
(budget / team / deadline / compliance). The system re-scores each option
against the selected constraints — but it STILL does not pick a winner. It
presents the weighted evaluation and the decision remains the human's.
"""

from typing import Any, Dict, List, Optional

# Constraint dimensions with human-readable labels
CONSTRAINT_DIMENSIONS = [
    {"id": "budget", "label": "Budget is tight"},
    {"id": "team", "label": "Small / existing team skills"},
    {"id": "deadline", "label": "Tight deadline (ship fast)"},
    {"id": "compliance", "label": "Compliance / data residency matters"},
]

# Per-option fit scores (0.0 - 1.0) per constraint dimension.
# These are meant to be model-generated in production; the built-in defaults
# provide a sensible, deterministic baseline for the mock/demo path.
# Keyed by canonical option id.
_DEFAULT_FIT: Dict[str, Dict[str, float]] = {
    "open-source-crm-base": {
        "budget": 0.8,
        "team": 0.5,
        "deadline": 0.4,
        "compliance": 0.9,
    },
    "buy-saas-crm": {
        "budget": 0.6,
        "team": 0.9,
        "deadline": 0.9,
        "compliance": 0.4,
    },
    "no-code-crm": {
        "budget": 0.7,
        "team": 0.8,
        "deadline": 0.95,
        "compliance": 0.5,
    },
    "spreadsheet-plus-automation": {
        "budget": 0.95,
        "team": 0.9,
        "deadline": 0.95,
        "compliance": 0.3,
    },
    "anchored_stack": {
        "budget": 0.3,
        "team": 0.9,
        "deadline": 0.2,
        "compliance": 0.6,
    },
    "merchant-of-record": {
        "budget": 0.7,
        "team": 0.8,
        "deadline": 0.7,
        "compliance": 0.95,
    },
    "crypto-payments": {
        "budget": 0.8,
        "team": 0.4,
        "deadline": 0.6,
        "compliance": 0.3,
    },
    "buy-vs-build": {
        "budget": 0.75,
        "team": 0.85,
        "deadline": 0.8,
        "compliance": 0.6,
    },
    "remote-first-hire": {
        "budget": 0.8,
        "team": 0.6,
        "deadline": 0.5,
        "compliance": 0.7,
    },
    "ai-augmented-small-team": {
        "budget": 0.9,
        "team": 0.7,
        "deadline": 0.85,
        "compliance": 0.6,
    },
    "agency-outsource": {
        "budget": 0.5,
        "team": 0.9,
        "deadline": 0.9,
        "compliance": 0.7,
    },
}


def weighted_evaluate(
    options: List[Dict[str, Any]],
    selected_constraints: List[str],
    weights: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Score each option against the selected constraints.

    Args:
        options: The option-space map options (each has 'canonical').
        selected_constraints: Constraint dimension ids the user checked.
        weights: Optional per-dimension weights (default all 1.0).

    Returns:
        The options with a 'weighted_score' and 'fit_breakdown' added,
        sorted by score descending. The decision is still the human's.
    """
    if not selected_constraints:
        for opt in options:
            opt["weighted_score"] = None
            opt["fit_breakdown"] = {}
        return options

    w = weights or {c: 1.0 for c in selected_constraints}
    for opt in options:
        canon = opt.get("canonical") or opt.get("option") or "unknown"
        fits = _DEFAULT_FIT.get(canon, {})
        breakdown = {c: fits.get(c, 0.5) for c in selected_constraints}
        total = sum(breakdown[c] * w.get(c, 1.0) for c in selected_constraints)
        weight_sum = sum(w.get(c, 1.0) for c in selected_constraints)
        opt["fit_breakdown"] = breakdown
        opt["weighted_score"] = round(total / weight_sum, 2) if weight_sum else 0.0

    options.sort(key=lambda o: o.get("weighted_score") or 0.0, reverse=True)
    return options
