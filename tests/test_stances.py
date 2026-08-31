"""Tests for stance prompts."""

from backend.config import STANCES
from backend.stances import stance_prompts


def test_all_configured_stances_have_prompts():
    prompts = stance_prompts()
    for s in STANCES:
        assert s in prompts, f"stance {s} missing prompt"


def test_red_team_attacks():
    prompts = stance_prompts()
    assert "ATTACK" in prompts["red_team"]


def test_each_prompt_forces_option_format():
    prompts = stance_prompts()
    for stance, prompt in prompts.items():
        if stance != "red_team":
            assert "OPTION:" in prompt, f"{stance} prompt missing OPTION format"
