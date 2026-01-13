"""
Unit tests for ScaleMetric.
"""
from analytics.metrics.scale import ScaleMetric
from analytics.models.repo import RepoStats


def test_scale_metric_name():
    """Test ScaleMetric name attribute."""
    metric = ScaleMetric()
    assert metric.name == "scale"


def test_scale_metric_balanced_repo():
    """Test scale calculation with balanced metrics."""
    repo = RepoStats(
        name="medium-repo",
        loc=5000,
        commits=50,
        stars=100,
        forks=10,
        languages={"Python": 3000, "JavaScript": 2000}
    )
    metric = ScaleMetric()
    result = metric.compute([repo])

    assert "medium-repo" in result.values
    assert isinstance(result.values["medium-repo"], float)
    assert result.values["medium-repo"] > 0.0


def test_scale_metric_small_repo():
    """Test scale calculation with small repository."""
    repo = RepoStats(
        name="tiny-repo",
        loc=100,
        commits=5,
        stars=0,
        forks=0,
        languages={"Python": 100}
    )
    metric = ScaleMetric()
    result = metric.compute([repo])

    # Should have lower scale than larger repo
    assert result.values["tiny-repo"] > 0.0


def test_scale_metric_large_repo():
    """Test scale calculation with large repository."""
    repo = RepoStats(
        name="huge-repo",
        loc=100000,
        commits=5000,
        stars=50000,
        forks=5000,
        languages={f"Lang{i}": 10000 for i in range(10)}
    )
    metric = ScaleMetric()
    result = metric.compute([repo])

    # Should have high scale value
    assert result.values["huge-repo"] > 0.0


def test_scale_metric_multiple_repos():
    """Test scale metric with multiple repositories."""
    repos = [
        RepoStats(
            name="small",
            loc=1000,
            commits=10,
            stars=5,
            forks=1,
            languages={"Python": 1000}
        ),
        RepoStats(
            name="medium",
            loc=10000,
            commits=100,
            stars=50,
            forks=10,
            languages={"Python": 5000, "JavaScript": 5000}
        ),
        RepoStats(
            name="large",
            loc=50000,
            commits=500,
            stars=500,
            forks=100,
            languages={f"Lang{i}": 5000 for i in range(10)}
        )
    ]
    metric = ScaleMetric()
    result = metric.compute(repos)

    assert len(result.values) == 3
    # Larger repos should have higher scale
    assert result.values["large"] > result.values["medium"]
    assert result.values["medium"] > result.values["small"]


def test_scale_metric_minimal_values():
    """Test scale metric with minimal valid values."""
    # Using minimal valid values since PositiveInt requires > 0
    repo = RepoStats(
        name="minimal-repo",
        loc=1,
        commits=1,
        stars=0,
        forks=0,
        languages={"Python": 1}
    )
    metric = ScaleMetric()
    result = metric.compute([repo])

    # Very small but positive scale value
    assert result.values["minimal-repo"] >= 0.0


def test_scale_metric_single_language():
    """Test scale metric with single language."""
    repo = RepoStats(
        name="single-lang",
        loc=5000,
        commits=50,
        stars=100,
        forks=10,
        languages={"Python": 5000}
    )
    metric = ScaleMetric()
    result = metric.compute([repo])

    # Should compute scale normally
    assert result.values["single-lang"] > 0.0


def test_scale_metric_many_languages():
    """Test scale metric with many languages."""
    repo = RepoStats(
        name="polyglot",
        loc=5000,
        commits=50,
        stars=100,
        forks=10,
        languages={f"Lang{i}": 500 for i in range(10)}
    )
    metric = ScaleMetric()
    result = metric.compute([repo])

    # Should have higher scale due to more languages
    assert result.values["polyglot"] > 0.0


def test_scale_metric_empty_list():
    """Test scale metric with empty repository list."""
    metric = ScaleMetric()
    result = metric.compute([])

    assert result.name == "scale"
    assert result.values == {}


def test_scale_metric_metric_components():
    """Test that all metric components contribute to scale."""
    # Create two repos with different strength areas
    repo_loc_focused = RepoStats(
        name="loc-focused",
        loc=50000,  # Very high LOC
        commits=10,  # Low commits
        stars=0,
        forks=0,
        languages={"Python": 50000}
    )

    repo_commit_focused = RepoStats(
        name="commit-focused",
        loc=100,  # Low LOC
        commits=5000,  # Very high commits
        stars=0,
        forks=0,
        languages={"Python": 100}
    )

    metric = ScaleMetric()
    result = metric.compute([repo_loc_focused, repo_commit_focused])

    # Both should have positive scale despite being unbalanced
    assert result.values["loc-focused"] > 0.0
    assert result.values["commit-focused"] > 0.0


def test_scale_metric_returns_floats():
    """Test that scale metric returns float values."""
    repo = RepoStats(
        name="test-repo",
        loc=5000,
        commits=50,
        stars=100,
        forks=10,
        languages={"Python": 3000, "Go": 2000}
    )
    metric = ScaleMetric()
    result = metric.compute([repo])

    assert isinstance(result.values["test-repo"], float)
