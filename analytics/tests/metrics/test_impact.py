"""
Unit tests for ImpactMetric.
"""
import math
from analytics.metrics.impact import ImpactMetric
from analytics.models.repo import RepoStats


def test_impact_metric_name():
    """Test ImpactMetric name attribute."""
    metric = ImpactMetric()
    assert metric.name == "impact"


def test_impact_metric_with_stars():
    """Test impact calculation with stars only."""
    repo = RepoStats(
        name="popular-repo",
        loc=1000,
        commits=10,
        stars=100,
        forks=0,
        languages={"Python": 1000}
    )
    metric = ImpactMetric()
    result = metric.compute([repo])

    assert "popular-repo" in result
    # log1p(100 + 0*0.5) = log1p(100) ≈ 4.615
    expected = math.log1p(100)
    assert abs(result.get_value_by_repo("popular-repo", "impact_score") - expected) < 0.001


def test_impact_metric_with_forks():
    """Test impact calculation with stars and forks."""
    repo = RepoStats(
        name="forked-repo",
        loc=2000,
        commits=20,
        stars=50,
        forks=20,
        languages={"Python": 2000}
    )
    metric = ImpactMetric()
    result = metric.compute([repo])

    # log1p(50 + 20*0.5) = log1p(60)
    expected = math.log1p(50 + 20 * 0.5)
    assert abs(result.get_value_by_repo("forked-repo", "impact_score") - expected) < 0.001


def test_impact_metric_no_engagement():
    """Test impact calculation with no stars or forks."""
    repo = RepoStats(
        name="unpopular-repo",
        loc=500,
        commits=5,
        stars=0,
        forks=0,
        languages={"Python": 500}
    )
    metric = ImpactMetric()
    result = metric.compute([repo])

    # log1p(0 + 0*0.5) = log1p(0) = 0
    assert result.get_value_by_repo("unpopular-repo", "impact_score") == 0.0


def test_impact_metric_multiple_repos():
    """Test impact metric with multiple repositories."""
    repos = [
        RepoStats(
            name="repo1",
            loc=1000,
            commits=10,
            stars=100,
            forks=10,
            languages={"Python": 1000}
        ),
        RepoStats(
            name="repo2",
            loc=2000,
            commits=20,
            stars=500,
            forks=50,
            languages={"Python": 2000}
        ),
        RepoStats(
            name="repo3",
            loc=500,
            commits=5,
            stars=0,
            forks=0,
            languages={"Python": 500}
        )
    ]
    metric = ImpactMetric()
    result = metric.compute(repos)

    assert len(result.repo_names) == 3
    # Repo2 should have highest impact
    assert result.get_value_by_repo("repo2", "impact_score") > result.get_value_by_repo("repo1", "impact_score")
    assert result.get_value_by_repo("repo1", "impact_score") > result.get_value_by_repo("repo3", "impact_score")


def test_impact_metric_forks_weighted_less():
    """Test that forks contribute less than stars to impact."""
    repo_many_stars = RepoStats(
        name="many-stars",
        loc=1000,
        commits=10,
        stars=100,
        forks=0,
        languages={"Python": 1000}
    )
    repo_many_forks = RepoStats(
        name="many-forks",
        loc=1000,
        commits=10,
        stars=0,
        forks=100,
        languages={"Python": 1000}
    )

    metric = ImpactMetric()
    result = metric.compute([repo_many_stars, repo_many_forks])

    # More stars should yield higher impact than same number of forks
    assert result.get_value_by_repo("many-stars", "impact_score") > result.get_value_by_repo("many-forks", "impact_score")


def test_impact_metric_empty_list():
    """Test impact metric with empty repository list."""
    metric = ImpactMetric()
    result = metric.compute([])

    assert result.name == "impact"
    assert len(result.repo_names) == 0
    assert result.values["impact_score"] == []


def test_impact_metric_large_numbers():
    """Test impact metric with very large star/fork counts."""
    repo = RepoStats(
        name="mega-popular",
        loc=10000,
        commits=100,
        stars=100000,
        forks=10000,
        languages={"Python": 10000}
    )
    metric = ImpactMetric()
    result = metric.compute([repo])

    # log1p(100000 + 10000*0.5) = log1p(105000)
    expected = math.log1p(100000 + 10000 * 0.5)
    assert abs(result.get_value_by_repo("mega-popular", "impact_score") - expected) < 0.001


def test_impact_metric_returns_floats():
    """Test that impact metric returns float values."""
    repo = RepoStats(
        name="test-repo",
        loc=1000,
        commits=10,
        stars=50,
        forks=5,
        languages={"Python": 1000}
    )
    metric = ImpactMetric()
    result = metric.compute([repo])

    assert isinstance(result.get_value_by_repo("test-repo", "impact_score"), float)
