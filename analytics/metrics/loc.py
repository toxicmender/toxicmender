from analytics.metrics.base import Metric


class LOCMetric(Metric):
    name = "loc"

    def compute(self, repos):
        return {
            repo.name: repo.loc
            for repo in repos
        }
