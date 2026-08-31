"""Tests for bias detection."""

from backend.bias import detect_bias


def test_anchored_stack_detected():
    flags = detect_bias("I need to build a CRM. I only know Java Spring.")
    kinds = [f["kind"] for f in flags]
    assert "anchored_stack" in kinds


def test_anchored_option_detected():
    flags = detect_bias("I want to sell subscriptions. Only thought of Stripe.")
    kinds = [f["kind"] for f in flags]
    assert "anchored_option" in kinds


def test_anchored_role_detected():
    flags = detect_bias("I need to hire a full-stack engineer.")
    kinds = [f["kind"] for f in flags]
    assert "anchored_role" in kinds


def test_single_option_bias_when_no_other_flag():
    flags = detect_bias("We should use Postgres for this project.")
    kinds = [f["kind"] for f in flags]
    assert "single_option_bias" in kinds


def test_no_flags_on_open_framing():
    flags = detect_bias("What are my options for a CRM system?")
    assert flags == []
