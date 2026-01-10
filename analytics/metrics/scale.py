"""
Scale metric - measures the size and scope of a repository.
Combines LOC, commits, and language diversity.
"""
from analytics.metrics.base import Metric
from analytics.models.metrics import MetricResult
from typing import List
from analytics.models.repo import RepoStats
import math


class ScaleMetric(Metric):
    """Computes scale metric measuring repository size and scope."""

    name = "scale"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute scale metric combining LOC, commits, and language count.

        Args:
            repos: List of repository statistics

        Returns:
            MetricResult with scale scores
        """
        values = {}

        for repo in repos:
            # Scale score combines multiple factors
            # Normalize LOC on log scale (typical repos 1K-100K LOC)
            loc_score = math.log1p(repo.loc / 1000)

            # Normalize commits on log scale
            commit_score = math.log1p(repo.commits / 50)

            # Language diversity contributes to scale perception
            language_score = math.log1p(len(repo.languages))

            # Combined scale with equal weighting
            scale_score = (loc_score + commit_score + language_score) / 3
            values[repo.name] = scale_score

        return MetricResult(
            name=self.name,
            values=values
        )
