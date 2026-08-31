"""Locked-in / anchoring bias detection.

The product's first move: detect when the decision-maker has already anchored
on a stack, an option, or a role — and surface that bias explicitly BEFORE
diverging options. Surfacing the anchor is what makes the "you probably
didn't know this" tags meaningful.
"""

import re
from typing import Dict, List


def detect_bias(user_input: str) -> List[Dict[str, str]]:
    """Detect locked-in bias signals in the user's decision framing.

    Returns a list of bias flags:
      - kind: anchored_stack | anchored_option | anchored_role | single_option_bias
      - label: human-readable description of the detected anchor
    """
    flags: List[Dict[str, str]] = []
    lower = user_input.lower()

    # Anchored stack: "I only know Java Spring" / "we use Spring Boot"
    stack_patterns = [
        r"only know[s]? [a-z+#.\s-]+(spring|java|go|react|vue|python|node|php)",
        r"only (use|have|do) [a-z+#.\s-]+(spring|java|go|react|vue|python|node|php)",
        r"stuck with [a-z+#.\s-]+(spring|java|go|react|vue|python|node|php)",
        r"we (use|have|are on) (spring|java|go|react|vue|python|node|php)",
    ]
    for pat in stack_patterns:
        m = re.search(pat, lower)
        if m:
            flags.append(
                {
                    "kind": "anchored_stack",
                    "label": f"Anchored on stack: {m.group(0)}",
                    "detail": (
                        "The stack was chosen by familiarity, not by the "
                        "problem. The decision may be solving the wrong question."
                    ),
                }
            )
            break

    # Anchored option: "only thought of Stripe" / "I'll use X"
    if re.search(r"only (thought|think) of [a-z\s]+", lower) or re.search(
        r"(decided|will use|going with|want to use) [a-z\s]+", lower
    ):
        flags.append(
            {
                "kind": "anchored_option",
                "label": "Anchored on a single option",
                "detail": (
                    "A single option is treated as the only possibility. The "
                    "option space has not been explored."
                ),
            }
        )

    # Anchored role: "I need to hire a full-stack" / "we need a dev"
    if re.search(r"need to hire|need a (full-stack|full stack|developer|engineer)", lower):
        flags.append(
            {
                "kind": "anchored_role",
                "label": "Anchored on a role, not an outcome",
                "detail": (
                    "The problem is framed as headcount. The real question is "
                    "the fastest reliable way to ship, which may not be a hire."
                ),
            }
        )

    # Single-option bias: the input contains exactly one concrete option word
    option_words = [
        "stripe",
        "java",
        "spring",
        "react",
        "postgresql",
        "postgres",
        "mysql",
        "docker",
        "kubernetes",
        "aws",
        "azure",
    ]
    found = [w for w in option_words if w in lower]
    if len(found) == 1 and not flags:
        flags.append(
            {
                "kind": "single_option_bias",
                "label": f"Single option mentioned: {found[0]}",
                "detail": "No alternatives considered in the framing.",
            }
        )

    return flags
