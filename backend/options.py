"""Option extraction, canonical dedup, zone classification, novelty tagging.

This is the product's core: turning raw stance proposals into an OPTION-SPACE
MAP with three zones:

  - consensus_zone:      options supported by >= 2 stances (safe to adopt)
  - true_divergence_zone: options that genuinely differ on material dimensions
  - false_divergence_zone: apparent differences that do not matter (near-variants)

Each option is tagged with novelty:
  - you_probably_didnt_know  (the cognitive-expansion payoff)
  - you_already_knew         (the anchor and its near-variants)

The system deliberately does NOT pick a winner. The map is the deliverable.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


def parse_option_block(block: str) -> Dict[str, str]:
    """Parse a KEY: value option block into a dict (keys normalized to lower)."""
    result: Dict[str, str] = {}
    for line in block.strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip().lower()] = val.strip()
    return result


def extract_options(text: str) -> List[Dict[str, str]]:
    """Extract OPTION / SUPPORTS / ATTACK blocks from a stance response.

    Returns a list of dicts with keys: option, canonical, novelty, reason,
    plus optional supports/target/alt. Blocks that only carry SUPPORTS/ATTACK
    (no OPTION) are returned too so their support/attack signal survives.
    """
    options: List[Dict[str, str]] = []
    # Split on any of OPTION:/SUPPORTS:/ATTACK: markers
    current: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^(OPTION|SUPPORTS|ATTACK):", stripped):
            if current:
                parsed = parse_option_block("\n".join(current))
                if parsed.get("option") or parsed.get("supports") or parsed.get("attack"):
                    options.append(parsed)
                current = []
        current.append(line)
    if current:
        parsed = parse_option_block("\n".join(current))
        if parsed.get("option") or parsed.get("supports") or parsed.get("attack"):
            options.append(parsed)
    return options


def classify_zones(
    options: List[Dict[str, str]],
    anchor_canonical: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Classify options into consensus / true-divergence / false-divergence.

    Args:
        options: List of option dicts (each with canonical, novelty, supports...).
        anchor_canonical: The user's anchored option canonical id (if any).

    Returns:
        (consensus, true_divergence, false_divergence) lists, each a dict with
        the option fields plus a support_count.
    """
    # Aggregate support per canonical
    support: Dict[str, int] = {}
    by_canonical: Dict[str, Dict[str, Any]] = {}
    for opt in options:
        canon = opt.get("canonical") or opt.get("option") or "unknown"
        # A SUPPORTS-only block (no option of its own) is not an independent
        # option — it only contributes a support vote below. Skip making an
        # empty shell entry for it.
        has_own_option = bool(opt.get("option"))
        # A stance's main proposal
        if has_own_option:
            if canon not in by_canonical:
                by_canonical[canon] = dict(opt)
                by_canonical[canon]["support_count"] = 0
                by_canonical[canon]["near_variant_of"] = None
            by_canonical[canon]["support_count"] += 1
            support[canon] = by_canonical[canon]["support_count"]
        # Explicit support of another option
        if opt.get("supports"):
            s = opt["supports"]
            if s not in by_canonical:
                by_canonical[s] = {
                    "option": s,
                    "canonical": s,
                    "novelty": "you_probably_didnt_know",
                    "reason": "Supported by another stance.",
                    "support_count": 0,
                    "near_variant_of": None,
                }
            by_canonical[s]["support_count"] += 1
            support[s] = by_canonical[s]["support_count"]
            # A SUPPORTS-only block has no option of its own; its support is
            # already counted. Ensure the block's own entry (if it became one
            # via canonical fallback) is not an empty shell.
            if canon == s and "reason" not in by_canonical[s]:
                by_canonical[s]["reason"] = opt.get("reason", "")
        # Near-variant marking (from ALT lines or explicit near_variant_of)
        if has_own_option and opt.get("alt") and "near-variant" in opt["alt"].lower():
            if canon not in by_canonical:
                by_canonical[canon] = dict(opt)
                by_canonical[canon]["support_count"] = 0
                by_canonical[canon]["near_variant_of"] = None
            by_canonical[canon]["near_variant_of"] = anchor_canonical or "anchor"

    consensus: List[Dict[str, Any]] = []
    true_div: List[Dict[str, Any]] = []
    false_div: List[Dict[str, Any]] = []

    for canon, opt in by_canonical.items():
        count = opt.get("support_count", 0)
        near = opt.get("near_variant_of")
        if count >= 2:
            consensus.append(opt)
        elif near:
            false_div.append(opt)
        else:
            true_div.append(opt)

    # Sort: consensus by support desc, true-div by novelty (didn't_know first),
    # false-div by support desc.
    consensus.sort(key=lambda o: -o.get("support_count", 0))
    true_div.sort(
        key=lambda o: (o.get("novelty", "") != "you_probably_didnt_know", o.get("support_count", 0))
    )
    false_div.sort(key=lambda o: -o.get("support_count", 0))

    return consensus, true_div, false_div


def tag_novelty(options: List[Dict[str, str]], anchor_canonical: Optional[str] = None) -> None:
    """Fill in novelty tags where missing.

    Rules:
      - explicit novelty is kept
      - near-variants of the anchor are 'you_already_knew'
      - the anchor itself is always 'you_already_knew'
      - everything else defaults to 'you_probably_didnt_know'
    """
    for opt in options:
        canon = opt.get("canonical") or opt.get("option") or "unknown"
        if opt.get("novelty"):
            continue
        if anchor_canonical and canon == anchor_canonical:
            opt["novelty"] = "you_already_knew"
        elif opt.get("near_variant_of"):
            opt["novelty"] = "you_already_knew"
        else:
            opt["novelty"] = "you_probably_didnt_know"
