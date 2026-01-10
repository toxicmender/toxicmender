"""
Consistency metric - measures the consistency of commits over time.
Evaluates commit frequency patterns and distribution.
"""
from analytics.metrics.base import Metric
from analytics.models.metrics import MetricResult
from typing import List
from analytics.models.repo import RepoStats


class ConsistencyMetric(Metric):
    """Computes consistency metric based on commit patterns."""

    name = "consistency"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute consistency metric.
        Simple implementation: normalized by repository age proxy (commits count).

        Args:
            repos: List of repository statistics

        Returns:
            MetricResult with consistency scores
        """
        values = {}

        for repo in repos:
            # Consistency as variance reduction metric
            # Higher commits with reasonable LOC ratio indicates stable patterns
            if repo.commits > 0:
                loc_per_commit = repo.loc / repo.commits
                # Penalize extreme ratios, reward balanced commit distribution
                consistency_score = min(loc_per_commit, 100) / 100.0
            else:
                consistency_score = 0.0

            values[repo.name] = consistency_score

        return MetricResult(
            name=self.name,
            values=values
        )
