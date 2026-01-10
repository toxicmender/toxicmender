class Visualizer:
    def __init__(self, charts):
        self.charts = charts

    def run(self):
        for chart, path in self.charts:
            chart.render(path)
# Example usage:
# charts = [(LanguageChart(data), "language_distribution.png")]
# visualizer = Visualizer(charts)
# visualizer.run()
# The Visualizer class takes a list of chart objects and their output paths, rendering each chart to the specified path.