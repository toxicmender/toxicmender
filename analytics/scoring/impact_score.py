class ImpactScore:
    def __init__(self, weights):
        self.weights = weights

    def score(self, normalized_metrics):
        return {
            repo: sum(
                normalized_metrics[m][repo] * w
                for m, w in self.weights.items()
            )
            for repo in next(iter(normalized_metrics.values()))
        }
# Example usage:
# weights = {'metric1': 0.5, 'metric2': 0.5}
# impact_scorer = ImpactScore(weights)
# normalized_metrics = {'metric1': {'repo1': 0.8, 'repo2': 0.6}, 'metric2': {'repo1': 0.7, 'repo2': 0.9}}
# scores = impact_scorer.score(normalized_metrics)
# The ImpactScore class calculates a weighted impact score for repositories based on normalized metrics.
