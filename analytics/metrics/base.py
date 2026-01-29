from abc import ABC, abstractmethod
from typing import List, Dict, Union
from analytics.models.repo import RepoStats
from analytics.models.metrics import MetricResult

class Metric(ABC):
    """Base class for all metrics with standardized output format."""
    name: str

    @abstractmethod
    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute metric for given repositories.

        Returns:
            MetricResult with values as Dict[str, List[int] | List[float]]
            where keys are metric dimensions and values are lists aligned with repos
        """
        pass

    def _create_result(self, repos: List[RepoStats], values: Dict[str, Union[List[int], List[float]]]) -> MetricResult:
        """Helper to create standardized MetricResult."""
        return MetricResult(
            name=self.name,
            values=values,
            repo_names=[repo.name for repo in repos]
        )
