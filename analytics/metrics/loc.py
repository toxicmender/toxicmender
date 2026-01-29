from analytics.metrics.base import Metric
from analytics.models.repo import RepoStats
from analytics.models.metrics import MetricResult
from typing import List


class LOCMetric(Metric):
    """Computes Lines of Code metric for repositories."""
    name = "loc"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute LOC metric.

        Returns:
            MetricResult with 'total_loc' as list of LOC values per repository
        """
        values = {
            "total_loc": [repo.loc for repo in repos]
        }
        return self._create_result(repos, values)
