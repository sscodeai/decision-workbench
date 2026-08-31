"""Tests for the eval harness."""

import pytest

from backend.eval_harness import (
    GOLD_OPTIONS,
    SCENARIO_INPUTS,
    _eval_one,
    _simulate_naive_multiagent,
    _simulate_single_model,
    _run_workbench,
    run_eval,
)


@pytest.mark.asyncio
async def test_workbench_finds_all_gold_scenario_a():
    found = await _run_workbench("A")
    found_set = set(found)
    assert "open-source-crm-base" in found_set
    assert "buy-saas-crm" in found_set
    assert "spreadsheet-plus-automation" in found_set  # probing discovery


@pytest.mark.asyncio
async def test_workbench_finds_all_gold_scenario_b():
    found = await _run_workbench("B")
    found_set = set(found)
    assert "merchant-of-record" in found_set
    assert "membership-platform" in found_set  # probing discovery


@pytest.mark.asyncio
async def test_eval_run_completes():
    results = await run_eval()
    # 3 scenarios x 3 methods
    assert len(results) == 9
    dw = [r for r in results if r.method == "decision_workbench"]
    assert len(dw) == 3
    # DW should have 100% coverage on all scenarios with current mock
    for r in dw:
        assert r.coverage == 1.0


@pytest.mark.asyncio
async def test_dw_beats_baselines_on_blind_spots():
    results = await run_eval()
    dw = [r for r in results if r.method == "decision_workbench"]
    single = [r for r in results if r.method == "single_model"]
    multi = [r for r in results if r.method == "naive_multiagent"]
    dw_hits = sum(len(r.gold_hit) for r in dw)
    single_hits = sum(len(r.gold_hit) for r in single)
    multi_hits = sum(len(r.gold_hit) for r in multi)
    assert dw_hits >= single_hits
    assert dw_hits >= multi_hits


def test_eval_one_classification():
    r = _eval_one("A", "test", ["open-source-crm-base", "buy-saas-crm"])
    assert len(r.gold_hit) == 2
    assert len(r.gold_missed) == 3  # no-code-crm, spreadsheet-plus-automation, crm-as-a-feature


def test_baselines_are_weaker():
    # Single model sees only its own option
    single_a = _simulate_single_model("A")
    assert len(single_a) <= 2
    # Naive multiagent sees stance options but not probing discoveries
    multi_a = _simulate_naive_multiagent("A")
    assert "spreadsheet-plus-automation" not in multi_a  # probing-only option
