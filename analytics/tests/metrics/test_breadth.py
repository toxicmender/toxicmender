"""
Unit tests for BreadthMetric.
"""
import pytest
from analytics.metrics.breadth import BreadthMetric
from analytics.models.repo import RepoStats


def test_breadth_metric_name():
    """Test BreadthMetric name attribute."""
    metric = BreadthMetric()
    assert metric.name == "breadth"


def test_breadth_metric_single_language(sample_repo):
    """Test breadth calculation with single language."""
    metric = BreadthMetric()
    result = metric.compute([sample_repo])

    assert result.name == "breadth"
    assert "test-repo" in result.values
    assert result.values["test-repo"] == 1.0


def test_breadth_metric_multiple_languages():
    """Test breadth calculation with multiple languages."""
    repo = RepoStats(
        name="multi-lang-repo",
        loc=5000,
        commits=50,
        stars=100,
        languages={"Python": 2000, "JavaScript": 2000, "Go": 1000}
    )
    metric = BreadthMetric()
    result = metric.compute([repo])

    assert result.values["multi-lang-repo"] == 3.0


def test_breadth_metric_no_languages():
    """Test breadth calculation with no languages."""
    # Note: Using minimal valid values since PositiveInt requires > 0
    # Empty languages dict is still valid for testing breadth = 0
    repo = RepoStats(
        name="empty-repo",
        loc=1,
        commits=1,
        stars=0,
        languages={}
    )
    metric = BreadthMetric()
    result = metric.compute([repo])

    assert result.values["empty-repo"] == 0.0


def test_breadth_metric_multiple_repos():
    """Test breadth calculation with multiple repositories."""
    repos = [
        RepoStats(
            name="repo1",
            loc=1000,
            commits=10,
            stars=5,
            languages={"Python": 1000}
        ),
        RepoStats(
            name="repo2",
            loc=2000,
            commits=20,
            stars=10,
            languages={"Python": 1000, "JavaScript": 1000}
        ),
        RepoStats(
            name="repo3",
            loc=3000,
            commits=30,
            stars=15,
            languages={"Python": 1000, "JavaScript": 1000, "Go": 1000}
        )
    ]
    metric = BreadthMetric()
    result = metric.compute(repos)

    assert len(result.values) == 3
    assert result.values["repo1"] == 1.0
    assert result.values["repo2"] == 2.0
    assert result.values["repo3"] == 3.0


def test_breadth_metric_many_languages():
    """Test breadth metric with many distinct languages."""
    languages = {f"Lang{i}": 100 for i in range(20)}
    repo = RepoStats(
        name="polyglot-repo",
        loc=2000,
        commits=50,
        stars=100,
        languages=languages
    )
    metric = BreadthMetric()
    result = metric.compute([repo])

    assert result.values["polyglot-repo"] == 20.0


def test_breadth_metric_empty_list():
    """Test breadth metric with empty repository list."""
    metric = BreadthMetric()
    result = metric.compute([])

    assert result.name == "breadth"
    assert result.values == {}


def test_breadth_metric_returns_floats():
    """Test that breadth metric returns float values."""
    repo = RepoStats(
        name="test-repo",
        loc=1000,
        commits=10,
        stars=5,
        languages={"Python": 500, "Go": 500}
    )
    metric = BreadthMetric()
    result = metric.compute([repo])

    assert isinstance(result.values["test-repo"], float)
