"""
Tests for PR Review Metric.
"""
import pytest
from analytics.metrics.pr_review import PRReviewMetric
from analytics.models.repo import RepoStats, PRMetrics


@pytest.fixture
def sample_repos_with_prs():
    """Create sample repositories with PR metrics."""
    return [
        RepoStats(
            name="active-pr-repo",
            loc=10000,
            commits=100,
            stars=50,
            forks=10,
            languages={"Python": 8000, "JavaScript": 2000},
            pr_metrics=PRMetrics(
                pr_count=20,
                pr_merged_count=18,
                pr_closed_count=2,
                avg_pr_merge_time_hours=24.5,
                pr_review_count=45,
                avg_reviews_per_pr=2.25,
                pr_comments_count=120,
                unique_reviewers=8
            )
        ),
        RepoStats(
            name="moderate-pr-repo",
            loc=5000,
            commits=50,
            stars=10,
            forks=2,
            languages={"Java": 5000},
            pr_metrics=PRMetrics(
                pr_count=10,
                pr_merged_count=7,
                pr_closed_count=3,
                avg_pr_merge_time_hours=48.0,
                pr_review_count=15,
                avg_reviews_per_pr=1.5,
                pr_comments_count=30,
                unique_reviewers=3
            )
        ),
        RepoStats(
            name="no-pr-repo",
            loc=2000,
            commits=20,
            stars=5,
            forks=1,
            languages={"Ruby": 2000},
            pr_metrics=None
        )
    ]


def test_pr_review_metric_initialization():
    """Test PRReviewMetric initialization."""
    metric = PRReviewMetric()
    assert metric.name == "pr_review"


def test_pr_velocity_computation(sample_repos_with_prs):
    """Test PR velocity calculation."""
    metric = PRReviewMetric()
    result = metric.compute(sample_repos_with_prs)

    pr_velocity = result.values["pr_velocity"]
    assert pr_velocity[0] == 18  # active-pr-repo
    assert pr_velocity[1] == 7   # moderate-pr-repo
    assert pr_velocity[2] == 0   # no-pr-repo


def test_pr_quality_computation(sample_repos_with_prs):
    """Test PR quality (merge rate) calculation."""
    metric = PRReviewMetric()
    result = metric.compute(sample_repos_with_prs)

    pr_quality = result.values["pr_quality"]
    assert pr_quality[0] == 18 / 20  # 90% merge rate
    assert pr_quality[1] == 7 / 10   # 70% merge rate
    assert pr_quality[2] == 0.0      # No PRs


def test_review_engagement_computation(sample_repos_with_prs):
    """Test review engagement calculation."""
    metric = PRReviewMetric()
    result = metric.compute(sample_repos_with_prs)

    review_engagement = result.values["review_engagement"]
    assert review_engagement[0] == 2.25
    assert review_engagement[1] == 1.5
    assert review_engagement[2] == 0.0


def test_collaboration_computation(sample_repos_with_prs):
    """Test collaboration score calculation."""
    metric = PRReviewMetric()
    result = metric.compute(sample_repos_with_prs)

    collaboration = result.values["collaboration"]
    assert collaboration[0] == 8
    assert collaboration[1] == 3
    assert collaboration[2] == 0


def test_empty_repo_list():
    """Test with empty repository list."""
    metric = PRReviewMetric()
    result = metric.compute([])

    assert result.values["pr_velocity"] == []
    assert result.values["pr_quality"] == []
    assert result.values["review_engagement"] == []
    assert result.values["collaboration"] == []


def test_all_repos_no_prs():
    """Test with repos that have no PR data."""
    repos = [
        RepoStats(
            name="repo1",
            loc=1000,
            commits=10,
            stars=0,
            forks=0,
            languages={"Python": 1000},
            pr_metrics=None
        ),
        RepoStats(
            name="repo2",
            loc=2000,
            commits=20,
            stars=0,
            forks=0,
            languages={"Java": 2000},
            pr_metrics=None
        )
    ]

    metric = PRReviewMetric()
    result = metric.compute(repos)

    assert all(v == 0 or v == 0.0 for v in result.values["pr_velocity"])
    assert all(v == 0.0 for v in result.values["pr_quality"])
    assert all(v == 0.0 for v in result.values["review_engagement"])
    assert all(v == 0 for v in result.values["collaboration"])


def test_result_structure(sample_repos_with_prs):
    """Test the structure of the returned MetricResult."""
    metric = PRReviewMetric()
    result = metric.compute(sample_repos_with_prs)

    assert result.name == "pr_review"
    assert "pr_velocity" in result.values
    assert "pr_quality" in result.values
    assert "review_engagement" in result.values
    assert "collaboration" in result.values
    assert len(result.repo_names) == 3
    assert result.repo_names == ["active-pr-repo", "moderate-pr-repo", "no-pr-repo"]


def test_zero_pr_count_edge_case():
    """Test edge case where pr_count is 0 but pr_metrics exists."""
    repos = [
        RepoStats(
            name="zero-pr-repo",
            loc=1000,
            commits=10,
            stars=0,
            forks=0,
            languages={"Python": 1000},
            pr_metrics=PRMetrics(
                pr_count=0,
                pr_merged_count=0,
                pr_closed_count=0,
                avg_pr_merge_time_hours=None,
                pr_review_count=0,
                avg_reviews_per_pr=0.0,
                pr_comments_count=0,
                unique_reviewers=0
            )
        )
    ]

    metric = PRReviewMetric()
    result = metric.compute(repos)

    assert result.values["pr_velocity"][0] == 0
    assert result.values["pr_quality"][0] == 0.0
    assert result.values["review_engagement"][0] == 0.0
    assert result.values["collaboration"][0] == 0
