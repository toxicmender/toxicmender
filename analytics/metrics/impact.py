"""
Impact metric - measures repository influence and reach.
Combines stars, forks, and engagement metrics.
"""
from analytics.metrics.base import Metric
from analytics.models.metrics import MetricResult
from typing import List
from analytics.models.repo import RepoStats
import math


class ImpactMetric(Metric):
    """Computes impact metric based on repository engagement."""

    name = "impact"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute impact metric using stars and forks.

        Args:
            repos: List of repository statistics

        Returns:
            MetricResult with impact scores
        """
        values = {}

        for repo in repos:
            # Impact formula: logarithmic scale of (stars * fork_influence)
            # Forks weighted less than stars as they're less indicative of quality
            impact_score = math.log1p(repo.stars + repo.forks * 0.5)
            values[repo.name] = impact_score

        return MetricResult(
            name=self.name,
            values=values
        )
