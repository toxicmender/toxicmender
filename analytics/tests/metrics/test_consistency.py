"""
Unit tests for ConsistencyMetric.
"""
import pytest
from analytics.metrics.consistency import ConsistencyMetric
from analytics.models.repo import RepoStats


def test_consistency_metric_name():
    """Test ConsistencyMetric name attribute."""
    metric = ConsistencyMetric()
    assert metric.name == "consistency"


def test_consistency_metric_balanced_repo(sample_repo):
    """Test consistency with balanced LOC/commits ratio."""
    metric = ConsistencyMetric()
    result = metric.compute([sample_repo])

    assert result.name == "consistency"
    assert "test-repo" in result.values
    # sample_repo: 1500 LOC / 10 commits = 150 LOC per commit
    # Consistency should be 150/100 = 1.5, capped at 1.0
    assert 0.0 <= result.values["test-repo"] <= 1.0


def test_consistency_metric_high_loc_per_commit():
    """Test consistency with high LOC per commit."""
    repo = RepoStats(
        name="efficient-repo",
        loc=5000,
        commits=10,  # 500 LOC per commit, capped at 100
        stars=50,
        languages={"Python": 5000}
    )
    metric = ConsistencyMetric()
    result = metric.compute([repo])

    # Should be capped at 1.0
    assert result.values["efficient-repo"] <= 1.0


def test_consistency_metric_low_loc_per_commit():
    """Test consistency with low LOC per commit."""
    repo = RepoStats(
        name="incremental-repo",
        loc=100,
        commits=50,  # 2 LOC per commit
        stars=5,
        languages={"Python": 100}
    )
    metric = ConsistencyMetric()
    result = metric.compute([repo])

    # Should be 2/100 = 0.02
    assert 0.0 <= result.values["incremental-repo"] < 1.0


def test_consistency_metric_zero_commits():
    """Test consistency with zero commits."""
    repo = RepoStats(
        name="no-commits-repo",
        loc=1000,
        commits=0,
        stars=0,
        languages={"Python": 1000}
    )
    metric = ConsistencyMetric()
    result = metric.compute([repo])

    # Should return 0.0 for zero commits
    assert result.values["no-commits-repo"] == 0.0


def test_consistency_metric_multiple_repos():
    """Test consistency metric with multiple repositories."""
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
            commits=50,
            stars=10,
            languages={"Python": 2000}
        ),
        RepoStats(
            name="repo3",
            loc=500,
            commits=100,
            stars=5,
            languages={"Python": 500}
        )
    ]
    metric = ConsistencyMetric()
    result = metric.compute(repos)

    assert len(result.values) == 3
    # All values should be in valid range
    for value in result.values.values():
        assert 0.0 <= value <= 1.0


def test_consistency_metric_empty_list():
    """Test consistency metric with empty repository list."""
    metric = ConsistencyMetric()
    result = metric.compute([])

    assert result.name == "consistency"
    assert result.values == {}


def test_consistency_metric_single_commit():
    """Test consistency with single commit."""
    repo = RepoStats(
        name="single-commit",
        loc=500,
        commits=1,
        stars=0,
        languages={"Python": 500}
    )
    metric = ConsistencyMetric()
    result = metric.compute([repo])

    # 500/100 = 5, capped at 1.0
    assert result.values["single-commit"] <= 1.0


def test_consistency_metric_returns_floats():
    """Test that consistency metric returns float values."""
    repo = RepoStats(
        name="test-repo",
        loc=1000,
        commits=10,
        stars=5,
        languages={"Python": 1000}
    )
    metric = ConsistencyMetric()
    result = metric.compute([repo])

    assert isinstance(result.values["test-repo"], float)
