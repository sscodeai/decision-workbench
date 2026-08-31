"""Tests for probing questions."""

from backend.config import PROBING_QUESTIONS
from backend.probing import build_probing_prompt, probing_questions


def test_three_probing_questions():
    probes = probing_questions()
    assert len(probes) == 3
    ids = {p["id"] for p in probes}
    assert ids == {"excluded_option", "non_mainstream", "weakest_point"}


def test_probing_prompt_contains_question():
    probe = PROBING_QUESTIONS[0]
    prompt = build_probing_prompt(probe, "I want to build a CRM")
    assert probe["question"] in prompt
    assert "I want to build a CRM" in prompt
