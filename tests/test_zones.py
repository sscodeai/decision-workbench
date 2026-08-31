"""Tests for option extraction, zone classification, novelty tagging."""

from backend.options import (
    classify_zones,
    extract_options,
    parse_option_block,
    tag_novelty,
)


def test_parse_option_block():
    block = (
        "OPTION: buy-saas-crm\n"
        "CANONICAL: buy-saas-crm\n"
        "NOVELTY: you_probably_didnt_know\n"
        "REASON: cheaper than building"
    )
    parsed = parse_option_block(block)
    assert parsed["option"] == "buy-saas-crm"
    assert parsed["novelty"] == "you_probably_didnt_know"


def test_extract_options_from_stance_response():
    text = (
        "OPTION: open-source-crm-base\n"
        "CANONICAL: open-source-crm-base\n"
        "REASON: mature bases exist\n"
        "\n"
        "OPTION: buy-saas-crm\n"
        "CANONICAL: buy-saas-crm\n"
        "REASON: cheaper\n"
    )
    options = extract_options(text)
    assert len(options) == 2
    assert options[0]["option"] == "open-source-crm-base"


def test_zone_classification_consensus_and_divergence():
    options = [
        {
            "option": "open-source-crm-base",
            "canonical": "open-source-crm-base",
            "novelty": "you_probably_didnt_know",
        },
        {
            "option": "open-source-crm-base",
            "canonical": "open-source-crm-base",
            "novelty": "you_probably_didnt_know",
            "supports": "open-source-crm-base",
        },
        {
            "option": "buy-saas-crm",
            "canonical": "buy-saas-crm",
            "novelty": "you_probably_didnt_know",
        },
        {
            "option": "go-rewrite",
            "canonical": "go-rewrite",
            "novelty": "you_already_knew",
            "alt": "A Go rewrite is a near-variant of the Java Spring anchor",
        },
    ]
    consensus, true_div, false_div = classify_zones(
        options, anchor_canonical="anchored_stack"
    )
    assert len(consensus) == 1
    assert consensus[0]["canonical"] == "open-source-crm-base"
    assert consensus[0]["support_count"] >= 2
    assert len(true_div) >= 1
    assert any(o["canonical"] == "buy-saas-crm" for o in true_div)
    assert any(o["canonical"] == "go-rewrite" for o in false_div)


def test_novelty_tagging_fills_gaps():
    options = [
        {"option": "x", "canonical": "x", "reason": "r"},
        {"option": "anchor", "canonical": "anchor", "reason": "r"},
    ]
    tag_novelty(options, anchor_canonical="anchor")
    assert options[0]["novelty"] == "you_probably_didnt_know"
    assert options[1]["novelty"] == "you_already_knew"
