"""
Code Review Quality Metric.
Measures review thoroughness, coverage, and reviewer diversity.
"""
from analytics.metrics.base import Metric
from analytics.models.repo import RepoStats
from analytics.models.metrics import MetricResult
from typing import List


class CodeReviewMetric(Metric):
    """Analyzes code review quality and patterns across repositories."""

    name = "code_review"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute code review quality metrics for repositories.

        Metrics computed:
        - review_thoroughness: Comments per PR (higher indicates detailed reviews)
        - review_coverage: Percentage of PRs with at least one review
        - reviewer_diversity: Ratio of unique reviewers to total PRs
        - merge_efficiency: Average merge time in hours (lower is better when reasonable)

        Args:
            repos: List of repository statistics

        Returns:
            MetricResult with code review quality dimensions
        """
        review_thoroughness: List[float] = []
        review_coverage: List[float] = []
        reviewer_diversity: List[float] = []
        merge_efficiency: List[float] = []

        for repo in repos:
            if repo.pr_metrics:
                pm = repo.pr_metrics

                # Review thoroughness: comments per PR
                if pm.pr_count > 0:
                    thoroughness = pm.pr_comments_count / pm.pr_count
                else:
                    thoroughness = 0.0
                review_thoroughness.append(thoroughness)

                # Review coverage: % of PRs with reviews
                if pm.pr_count > 0:
                    # Estimate PRs with reviews (assuming avg > 0 means some PRs had reviews)
                    if pm.pr_review_count > 0:
                        coverage = min(1.0, pm.pr_review_count / pm.pr_count)
                    else:
                        coverage = 0.0
                else:
                    coverage = 0.0
                review_coverage.append(coverage)

                # Reviewer diversity: unique reviewers per PR
                if pm.pr_count > 0:
                    diversity = pm.unique_reviewers / pm.pr_count
                else:
                    diversity = 0.0
                reviewer_diversity.append(diversity)

                # Merge efficiency: avg merge time in hours
                # Use 0 for repos with no merge time data
                merge_time = pm.avg_pr_merge_time_hours if pm.avg_pr_merge_time_hours else 0.0
                merge_efficiency.append(merge_time)
            else:
                # No PR data available
                review_thoroughness.append(0.0)
                review_coverage.append(0.0)
                reviewer_diversity.append(0.0)
                merge_efficiency.append(0.0)

        return self._create_result(
            repos,
            {
                "review_thoroughness": review_thoroughness,
                "review_coverage": review_coverage,
                "reviewer_diversity": reviewer_diversity,
                "merge_efficiency": merge_efficiency
            }
        )
