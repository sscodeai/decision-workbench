"""Tests for constraint backfill + weighted evaluation."""

from backend.constraints import CONSTRAINT_DIMENSIONS, weighted_evaluate


def test_no_constraints_returns_neutral():
    options = [{"canonical": "a"}, {"canonical": "b"}]
    result = weighted_evaluate(options, [])
    for opt in result:
        assert opt["weighted_score"] is None


def test_weighted_evaluate_scores_and_sorts():
    options = [
        {"canonical": "open-source-crm-base"},
        {"canonical": "buy-saas-crm"},
    ]
    result = weighted_evaluate(options, ["budget", "deadline"])
    scores = [o["weighted_score"] for o in result]
    assert all(s is not None for s in scores)
    # sorted descending
    assert scores == sorted(scores, reverse=True)
    assert result[0]["fit_breakdown"]["budget"] is not None


def test_constraint_dimensions_exist():
    ids = [d["id"] for d in CONSTRAINT_DIMENSIONS]
    assert "budget" in ids and "team" in ids and "deadline" in ids and "compliance" in ids
