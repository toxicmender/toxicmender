"""
Breadth metric - measures the diversity of programming languages in a repository.
Higher breadth indicates more diverse language usage.
"""
from analytics.metrics.base import Metric
from analytics.models.metrics import MetricResult
from typing import List
from analytics.models.repo import RepoStats


class BreadthMetric(Metric):
    """Computes language breadth/diversity metric."""

    name = "breadth"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute breadth metric - number of distinct languages per repository.

        Args:
            repos: List of repository statistics

        Returns:
            MetricResult with breadth values for each repository
        """
        values = {
            repo.name: len(repo.languages)
            for repo in repos
        }

        return MetricResult(
            name=self.name,
            values={k: float(v) for k, v in values.items()}
        )
