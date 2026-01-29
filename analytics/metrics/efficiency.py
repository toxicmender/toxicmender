from analytics.metrics.base import Metric
from analytics.models.metrics import MetricResult
from analytics.exceptions import MetricError
from analytics.models.repo import RepoStats
from typing import List

class EfficiencyMetric(Metric):
    """Computes efficiency as LOC per commit."""
    name = "efficiency"

    def compute(self, repos: List[RepoStats]) -> MetricResult:
        """
        Compute efficiency metric (LOC per commit).

        Returns:
            MetricResult with 'loc_per_commit' as list of efficiency values
        """
        loc_per_commit = []

        for repo in repos:
            if repo.commits <= 0:
                raise MetricError(f"{repo.name}: commits must be > 0")
            loc_per_commit.append(repo.loc / repo.commits)

        values = {
            "loc_per_commit": loc_per_commit
        }
        return self._create_result(repos, values)
# Example usage:
if __name__ == "__main__":
    repo1 = RepoStats(name="Repo1", loc=10000, commits=50)
    repo2 = RepoStats(name="Repo2", loc=20000, commits=100)

    efficiency_metric = EfficiencyMetric()
    result = efficiency_metric.compute([repo1, repo2])

    print(result.json(indent=4))