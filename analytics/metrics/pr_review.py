"""
Pull Request Review Metric.
Measures PR velocity, review engagement, quality, and collaboration.
"""
from analytics.metrics.base import Metric
from analytics.models.repo import RepoStats
from analytics.models.metrics import MetricResult
from typing import List


class PRReviewMetric(Metric):
    """Analyzes pull request and review patterns across repositories."""

    name = "pr_review"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute PR review metrics for repositories.

        Metrics computed:
        - pr_velocity: Total PRs merged (higher is better)
        - pr_quality: Merge rate (merged / total PRs)
        - review_engagement: Average reviews per PR
        - collaboration: Unique reviewers count

        Args:
            repos: List of repository statistics

        Returns:
            MetricResult with PR review dimensions
        """
        pr_velocity: List[int] = []
        pr_quality: List[float] = []
        review_engagement: List[float] = []
        collaboration: List[int] = []

        for repo in repos:
            if repo.pr_metrics:
                pm = repo.pr_metrics

                # PR velocity: number of merged PRs
                pr_velocity.append(pm.pr_merged_count)

                # PR quality: merge rate
                if pm.pr_count > 0:
                    quality = pm.pr_merged_count / pm.pr_count
                else:
                    quality = 0.0
                pr_quality.append(quality)

                # Review engagement: avg reviews per PR
                review_engagement.append(pm.avg_reviews_per_pr)

                # Collaboration: unique reviewers
                collaboration.append(pm.unique_reviewers)
            else:
                # No PR data available
                pr_velocity.append(0)
                pr_quality.append(0.0)
                review_engagement.append(0.0)
                collaboration.append(0)

        return self._create_result(
            repos,
            {
                "pr_velocity": pr_velocity,
                "pr_quality": pr_quality,
                "review_engagement": review_engagement,
                "collaboration": collaboration
            }
        )
