class Analyzer:
    def __init__(self, metrics):
        self.metrics = metrics

    def run(self, repos):
        return {
            metric.name: metric.compute(repos)
            for metric in self.metrics
        }
# Example usage:
# metrics = [MetricA(), MetricB()]
# analyzer = Analyzer(metrics)
# results = analyzer.run(repos)
# The Analyzer class runs a set of metrics on a list of repositories and returns the computed results.
