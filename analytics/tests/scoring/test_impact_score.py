import pytest
from analytics.scoring.impact_score import ImpactScore


def test_impact_score_basic():
    """Test basic impact scoring with normalized metrics."""
    weights = {"metric1": 0.6, "metric2": 0.4}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 0.8, "repo_b": 0.6},
        "metric2": {"repo_a": 0.7, "repo_b": 0.9}
    }

    scores = scorer.score(normalized_metrics)

    assert "repo_a" in scores
    assert "repo_b" in scores
    # repo_a: 0.8 * 0.6 + 0.7 * 0.4 = 0.48 + 0.28 = 0.76
    assert scores["repo_a"] == pytest.approx(0.76, abs=0.01)
    # repo_b: 0.6 * 0.6 + 0.9 * 0.4 = 0.36 + 0.36 = 0.72
    assert scores["repo_b"] == pytest.approx(0.72, abs=0.01)


def test_impact_score_single_metric():
    """Test impact scoring with a single metric."""
    weights = {"metric1": 1.0}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 0.9, "repo_b": 0.3}
    }

    scores = scorer.score(normalized_metrics)

    assert scores["repo_a"] == pytest.approx(0.9, abs=0.01)
    assert scores["repo_b"] == pytest.approx(0.3, abs=0.01)


def test_impact_score_equal_weights():
    """Test impact scoring with equal weights."""
    weights = {"metric1": 0.5, "metric2": 0.5}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 1.0, "repo_b": 0.0},
        "metric2": {"repo_a": 0.0, "repo_b": 1.0}
    }

    scores = scorer.score(normalized_metrics)

    # Both repos should have same score due to equal weights
    assert scores["repo_a"] == pytest.approx(0.5, abs=0.01)
    assert scores["repo_b"] == pytest.approx(0.5, abs=0.01)


def test_impact_score_multiple_repos():
    """Test impact scoring with multiple repositories."""
    weights = {"metric1": 0.4, "metric2": 0.3, "metric3": 0.3}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 0.9, "repo_b": 0.7, "repo_c": 0.5},
        "metric2": {"repo_a": 0.8, "repo_b": 0.6, "repo_c": 0.4},
        "metric3": {"repo_a": 0.7, "repo_b": 0.5, "repo_c": 0.3}
    }

    scores = scorer.score(normalized_metrics)

    assert len(scores) == 3
    assert scores["repo_a"] > scores["repo_b"] > scores["repo_c"]


def test_impact_score_zero_values():
    """Test impact scoring with zero values."""
    weights = {"metric1": 0.5, "metric2": 0.5}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 0.0, "repo_b": 0.0},
        "metric2": {"repo_a": 0.0, "repo_b": 0.0}
    }

    scores = scorer.score(normalized_metrics)

    assert scores["repo_a"] == 0.0
    assert scores["repo_b"] == 0.0


def test_impact_score_max_values():
    """Test impact scoring with maximum values."""
    weights = {"metric1": 0.5, "metric2": 0.5}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 1.0, "repo_b": 1.0},
        "metric2": {"repo_a": 1.0, "repo_b": 1.0}
    }

    scores = scorer.score(normalized_metrics)

    assert scores["repo_a"] == pytest.approx(1.0, abs=0.01)
    assert scores["repo_b"] == pytest.approx(1.0, abs=0.01)


def test_impact_score_three_metrics():
    """Test impact scoring with three metrics."""
    weights = {"metric1": 0.5, "metric2": 0.3, "metric3": 0.2}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 0.8},
        "metric2": {"repo_a": 0.6},
        "metric3": {"repo_a": 0.4}
    }

    scores = scorer.score(normalized_metrics)

    # 0.8 * 0.5 + 0.6 * 0.3 + 0.4 * 0.2 = 0.4 + 0.18 + 0.08 = 0.66
    assert scores["repo_a"] == pytest.approx(0.66, abs=0.01)


def test_impact_score_asymmetric_weights():
    """Test impact scoring with asymmetric weights."""
    weights = {"metric1": 0.8, "metric2": 0.2}
    scorer = ImpactScore(weights)

    normalized_metrics = {
        "metric1": {"repo_a": 0.5},
        "metric2": {"repo_a": 1.0}
    }

    scores = scorer.score(normalized_metrics)

    # 0.5 * 0.8 + 1.0 * 0.2 = 0.4 + 0.2 = 0.6
    assert scores["repo_a"] == pytest.approx(0.6, abs=0.01)
