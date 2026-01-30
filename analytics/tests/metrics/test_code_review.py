"""
Tests for Code Review Metric.
"""
import pytest
from analytics.metrics.code_review import CodeReviewMetric
from analytics.models.repo import RepoStats, PRMetrics


@pytest.fixture
def sample_repos_with_reviews():
    """Create sample repositories with code review metrics."""
    return [
        RepoStats(
            name="high-quality-reviews",
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
                pr_review_count=60,  # 3 reviews per PR on average
                avg_reviews_per_pr=3.0,
                pr_comments_count=200,  # 10 comments per PR
                unique_reviewers=12
            )
        ),
        RepoStats(
            name="moderate-reviews",
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
                pr_review_count=10,  # 1 review per PR
                avg_reviews_per_pr=1.0,
                pr_comments_count=30,  # 3 comments per PR
                unique_reviewers=5
            )
        ),
        RepoStats(
            name="no-review-data",
            loc=2000,
            commits=20,
            stars=5,
            forks=1,
            languages={"Ruby": 2000},
            pr_metrics=None
        )
    ]


def test_code_review_metric_initialization():
    """Test CodeReviewMetric initialization."""
    metric = CodeReviewMetric()
    assert metric.name == "code_review"


def test_review_thoroughness_computation(sample_repos_with_reviews):
    """Test review thoroughness (comments per PR) calculation."""
    metric = CodeReviewMetric()
    result = metric.compute(sample_repos_with_reviews)

    thoroughness = result.values["review_thoroughness"]
    assert thoroughness[0] == 200 / 20  # 10 comments per PR
    assert thoroughness[1] == 30 / 10   # 3 comments per PR
    assert thoroughness[2] == 0.0       # No data


def test_review_coverage_computation(sample_repos_with_reviews):
    """Test review coverage calculation."""
    metric = CodeReviewMetric()
    result = metric.compute(sample_repos_with_reviews)

    coverage = result.values["review_coverage"]
    # Coverage = min(1.0, review_count / pr_count)
    assert coverage[0] == 1.0  # 60/20 = 3.0, capped at 1.0
    assert coverage[1] == 1.0  # 10/10 = 1.0
    assert coverage[2] == 0.0  # No data


def test_reviewer_diversity_computation(sample_repos_with_reviews):
    """Test reviewer diversity calculation."""
    metric = CodeReviewMetric()
    result = metric.compute(sample_repos_with_reviews)

    diversity = result.values["reviewer_diversity"]
    assert diversity[0] == 12 / 20  # 0.6 reviewers per PR
    assert diversity[1] == 5 / 10   # 0.5 reviewers per PR
    assert diversity[2] == 0.0      # No data


def test_merge_efficiency_computation(sample_repos_with_reviews):
    """Test merge efficiency (time) calculation."""
    metric = CodeReviewMetric()
    result = metric.compute(sample_repos_with_reviews)

    efficiency = result.values["merge_efficiency"]
    assert efficiency[0] == 24.5
    assert efficiency[1] == 48.0
    assert efficiency[2] == 0.0


def test_empty_repo_list():
    """Test with empty repository list."""
    metric = CodeReviewMetric()
    result = metric.compute([])

    assert result.values["review_thoroughness"] == []
    assert result.values["review_coverage"] == []
    assert result.values["reviewer_diversity"] == []
    assert result.values["merge_efficiency"] == []


def test_all_repos_no_reviews():
    """Test with repos that have no review data."""
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

    metric = CodeReviewMetric()
    result = metric.compute(repos)

    assert all(v == 0.0 for v in result.values["review_thoroughness"])
    assert all(v == 0.0 for v in result.values["review_coverage"])
    assert all(v == 0.0 for v in result.values["reviewer_diversity"])
    assert all(v == 0.0 for v in result.values["merge_efficiency"])


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

    metric = CodeReviewMetric()
    result = metric.compute(repos)

    # All should be 0.0 when pr_count is 0
    assert result.values["review_thoroughness"][0] == 0.0
    assert result.values["review_coverage"][0] == 0.0
    assert result.values["reviewer_diversity"][0] == 0.0
    assert result.values["merge_efficiency"][0] == 0.0


def test_no_merge_time_data():
    """Test when merge time data is None."""
    repos = [
        RepoStats(
            name="no-merge-time",
            loc=1000,
            commits=10,
            stars=0,
            forks=0,
            languages={"Python": 1000},
            pr_metrics=PRMetrics(
                pr_count=5,
                pr_merged_count=3,
                pr_closed_count=2,
                avg_pr_merge_time_hours=None,  # No merge time data
                pr_review_count=10,
                avg_reviews_per_pr=2.0,
                pr_comments_count=20,
                unique_reviewers=4
            )
        )
    ]

    metric = CodeReviewMetric()
    result = metric.compute(repos)

    # Should default to 0.0 when merge time is None
    assert result.values["merge_efficiency"][0] == 0.0


def test_result_structure(sample_repos_with_reviews):
    """Test the structure of the returned MetricResult."""
    metric = CodeReviewMetric()
    result = metric.compute(sample_repos_with_reviews)

    assert result.name == "code_review"
    assert "review_thoroughness" in result.values
    assert "review_coverage" in result.values
    assert "reviewer_diversity" in result.values
    assert "merge_efficiency" in result.values
    assert len(result.repo_names) == 3
    assert result.repo_names == ["high-quality-reviews", "moderate-reviews", "no-review-data"]


def test_coverage_capping():
    """Test that coverage is capped at 1.0."""
    repos = [
        RepoStats(
            name="high-review-count",
            loc=1000,
            commits=10,
            stars=0,
            forks=0,
            languages={"Python": 1000},
            pr_metrics=PRMetrics(
                pr_count=10,
                pr_merged_count=8,
                pr_closed_count=2,
                avg_pr_merge_time_hours=24.0,
                pr_review_count=50,  # 5 reviews per PR
                avg_reviews_per_pr=5.0,
                pr_comments_count=100,
                unique_reviewers=8
            )
        )
    ]

    metric = CodeReviewMetric()
    result = metric.compute(repos)

    # Should be capped at 1.0 even though 50/10 = 5.0
    assert result.values["review_coverage"][0] == 1.0
