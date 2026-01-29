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
            MetricResult with 'impact_score' as list of engagement scores
        """
        impact_scores = []

        for repo in repos:
            # Impact formula: logarithmic scale of (stars * fork_influence)
            # Forks weighted less than stars as they're less indicative of quality
            impact_score = math.log1p(repo.stars + repo.forks * 0.5)
            impact_scores.append(impact_score)

        values = {
            "impact_score": impact_scores
        }
        return self._create_result(repos, values)
