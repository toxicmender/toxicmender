"""
Language distribution pie chart visualization.
"""
from analytics.charts.base import Chart
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict


class LanguageChart(Chart):
    """Renders language distribution as a pie chart."""

    def __init__(self, data: Dict[str, float]):
        """
        Initialize language chart.

        Args:
            data: Dictionary mapping language names to their total LOC
        """
        self.data = data

    def render(self, output: Path) -> None:
        """
        Render language distribution pie chart.

        Args:
            output: Output path for the chart (SVG or PNG)

        Raises:
            ChartError: If output path is invalid or not writable
        """
        self._validate_path(output)

        fig, ax = plt.subplots(figsize=(10, 8))

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            self.data.values(),
            labels=self.data.keys(),
            autopct="%1.1f%%",
            startangle=90,
            textprops={'fontsize': 10}
        )

        # Improve readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title("Language Distribution by Lines of Code", fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output, dpi=300, format=output.suffix[1:])
        plt.close()