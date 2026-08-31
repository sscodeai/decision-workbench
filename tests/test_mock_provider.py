"""Tests for the mock provider."""

import pytest

from backend.providers import get_provider


@pytest.mark.asyncio
async def test_mock_provider_default():
    provider = get_provider("mock")
    assert provider is not None
    assert provider.name == "mock"


@pytest.mark.asyncio
async def test_mock_scenario_a_returns_stance_options():
    provider = get_provider("mock")
    resp = await provider.query(
        "mock/architect",
        [{"role": "user", "content": "I need to build a CRM. I only know Java Spring."}],
    )
    assert resp is not None
    assert "open-source-crm-base" in resp["content"]


@pytest.mark.asyncio
async def test_mock_scenario_a_red_team_attacks_anchor():
    provider = get_provider("mock")
    resp = await provider.query(
        "mock/red_team",
        [{"role": "user", "content": "I need to build a CRM. I only know Java Spring."}],
    )
    assert resp is not None
    assert "ATTACK" in resp["content"]


@pytest.mark.asyncio
async def test_mock_scenario_b_detection():
    provider = get_provider("mock")
    resp = await provider.query(
        "mock/cost",
        [{"role": "user", "content": "I want to sell report subscriptions. Only thought of Stripe."}],
    )
    assert resp is not None
    assert "merchant-of-record" in resp["content"]


@pytest.mark.asyncio
async def test_mock_unknown_model_returns_none():
    provider = get_provider("mock")
    resp = await provider.query("mock/nonexistent", [{"role": "user", "content": "hi"}])
    assert resp is None
