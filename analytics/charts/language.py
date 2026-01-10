import matplotlib.pyplot as plt

from analytics.charts.base import Chart

class LanguageChart(Chart):
    def __init__(self, data):
        self.data = data

    def render(self, path):
        plt.figure(figsize=(6,6))
        plt.pie(
            self.data.values(),
            labels=self.data.keys(),
            autopct="%1.1f%%"
        )
        plt.title("Language Distribution")
        plt.savefig(path)
        plt.close()
