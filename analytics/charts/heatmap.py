"""
Heatmap visualization for metric correlation matrix.
"""
from analytics.charts.base import Chart
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List


class HeatmapChart(Chart):
    """Renders correlation heatmap for multiple metrics."""

    def __init__(self, data: Dict[str, List[float]], metric_names: List[str]):
        """
        Initialize heatmap chart.

        Args:
            data: Dictionary mapping metric names to lists of values
            metric_names: List of metric labels for axis
        """
        self.data = data
        self.metric_names = metric_names

    def render(self, output: Path) -> None:
        """
        Render correlation heatmap.

        Args:
            output: Output path for the chart (SVG or PNG)

        Raises:
            ChartError: If output path is invalid or not writable
        """
        self._validate_path(output)

        # Build correlation matrix from data
        values = [self.data[name] for name in self.metric_names]
        correlation_matrix = np.corrcoef(values)

        # Handle single metric case - corrcoef returns scalar
        if correlation_matrix.ndim == 0:
            correlation_matrix = np.array([[correlation_matrix]])

        fig, ax = plt.subplots(figsize=(10, 8))

        # Create heatmap
        im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

        # Set ticks and labels
        ax.set_xticks(range(len(self.metric_names)))
        ax.set_yticks(range(len(self.metric_names)))
        ax.set_xticklabels(self.metric_names, rotation=45, ha='right')
        ax.set_yticklabels(self.metric_names)

        # Add correlation values as text
        for i in range(len(self.metric_names)):
            for j in range(len(self.metric_names)):
                text = ax.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=9)

        ax.set_title("Metric Correlation Heatmap")
        fig.colorbar(im, ax=ax, label="Correlation")

        plt.tight_layout()
        plt.savefig(output, dpi=300, format=output.suffix[1:])
        plt.close()
