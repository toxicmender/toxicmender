from abc import ABC, abstractmethod
from typing import List
from analytics.models.repo import RepoStats
from analytics.models.metrics import MetricResult

class Metric(ABC):
    name: str

    @abstractmethod
    def compute(self, repos: List[RepoStats]) -> MetricResult:
        pass
