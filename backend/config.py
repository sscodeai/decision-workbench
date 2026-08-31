"""Configuration for Decision Workbench.

The product philosophy: decision power = size of the option space, not the
ability to pick. The system never picks a winner — it expands options, reveals
blind spots, and hands the decision back to a human.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------
# Which provider backend to use. Defaults to the built-in mock so the full
# loop runs with zero API keys. Set PROVIDER=openrouter for real models.
PROVIDER = os.getenv("PROVIDER", "mock")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = os.getenv(
    "OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"
)
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

# ---------------------------------------------------------------------------
# Stance profiles — each forces a different angle so proposals genuinely
# diverge. Heterogeneous cognition is the point (same-model role-play does
# NOT produce real divergence — see Representational Collapse, arXiv 2604.03809).
# ---------------------------------------------------------------------------
STANCES = [
    "architect",
    "cost",
    "security",
    "product",
    "red_team",
]

# ---------------------------------------------------------------------------
# The three probing questions that force the option space open.
# ---------------------------------------------------------------------------
PROBING_QUESTIONS = [
    {
        "id": "excluded_option",
        "question": "Why did you NOT consider X?",
        "instruction": "List options the decision-maker likely excluded without a real reason, and say why each deserves a look.",
    },
    {
        "id": "non_mainstream",
        "question": "Give one non-mainstream option with a real reason",
        "instruction": "Propose ONE unconventional option that has a genuine justification, even if it is outside the mainstream.",
    },
    {
        "id": "weakest_point",
        "question": "What is the weakest point of your preferred option?",
        "instruction": "Attack the decision-maker's anchored/preferred option: where is it most likely to fail, and what would beat it?",
    },
]
