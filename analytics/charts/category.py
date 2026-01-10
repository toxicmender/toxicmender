"""
Category-based chart for visualizing metric distributions across repository categories.
"""
from analytics.charts.base import Chart
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict, List


class CategoryChart(Chart):
    """Renders metrics distributed by repository category."""

    def __init__(self, data: Dict[str, List[float]], categories: List[str]):
        """
        Initialize category chart.

        Args:
            data: Dictionary mapping category names to lists of values
            categories: List of category labels
        """
        self.data = data
        self.categories = categories

    def render(self, output: Path) -> None:
        """
        Render category-based bar chart.

        Args:
            output: Output path for the chart (SVG or PNG)

        Raises:
            ChartError: If output path is invalid or not writable
        """
        self._validate_path(output)

        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data for grouped bar chart
        x_pos = range(len(self.categories))
        width = 0.8 / len(self.data)

        for idx, (category, values) in enumerate(self.data.items()):
            offsets = [i * width + idx * width for i in x_pos]
            ax.bar(offsets, values, width, label=category)

        ax.set_xlabel("Category")
        ax.set_ylabel("Metric Value")
        ax.set_title("Metrics by Category")
        ax.set_xticks([i * width * len(self.data) + width * len(self.data) / 2
                       for i in x_pos])
        ax.set_xticklabels(self.categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output, dpi=300, format=output.suffix[1:])
        plt.close()
