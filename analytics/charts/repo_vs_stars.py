"""
Repository vs Stars scatter plot visualization.
"""
from analytics.charts.base import Chart
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict, Tuple


class RepoVsStarsChart(Chart):
    """Renders scatter plot comparing repository characteristics with star counts."""

    def __init__(self, data: Dict[str, Tuple[float, int]], x_label: str = "Metric Value"):
        """
        Initialize repo vs stars chart.

        Args:
            data: Dictionary mapping repo names to (metric_value, stars) tuples
            x_label: Label for x-axis metric
        """
        self.data = data
        self.x_label = x_label

    def render(self, output: Path) -> None:
        """
        Render scatter plot of metrics vs stars.

        Args:
            output: Output path for the chart (SVG or PNG)

        Raises:
            ChartError: If output path is invalid or not writable
        """
        self._validate_path(output)

        repos = list(self.data.keys())
        x_values = [v[0] for v in self.data.values()]
        y_values = [v[1] for v in self.data.values()]

        fig, ax = plt.subplots(figsize=(12, 8))

        scatter = ax.scatter(x_values, y_values, s=100, alpha=0.6, c=y_values, cmap='viridis')

        # Add repository labels to points
        for i, repo in enumerate(repos):
            ax.annotate(repo, (x_values[i], y_values[i]),
                       fontsize=8, alpha=0.7,
                       xytext=(5, 5), textcoords='offset points')

        ax.set_xlabel(self.x_label)
        ax.set_ylabel("GitHub Stars")
        ax.set_title("Repository Metrics vs Stars")
        ax.grid(True, alpha=0.3)

        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label("Stars")

        plt.tight_layout()
        plt.savefig(output, dpi=300, format=output.suffix[1:])
        plt.close()
