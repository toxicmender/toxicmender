from analytics.charts.base import Chart
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict

class LanguageChart(Chart):
    def __init__(self, data: Dict[str, float]):
        self.data = data

    def render(self, output: Path) -> None:
        if output.suffix not in {".svg", ".png"}:
            raise ValueError("Chart must be SVG or PNG")

        plt.figure(figsize=(6,6))
        plt.pie(self.data.values(), labels=self.data.keys(), autopct="%1.1f%%")
        plt.title("Language Distribution")
        plt.savefig(output)
        plt.close()
        self._validate_path(output)