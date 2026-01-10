"""
Efficiency metric visualization chart.
Displays lines of code per commit efficiency across repositories.
"""
from analytics.charts.base import Chart
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict


class EfficiencyChart(Chart):
    """Renders efficiency metrics (e.g., LOC per commit) for repositories."""

    def __init__(self, data: Dict[str, float]):
        """
        Initialize efficiency chart.

        Args:
            data: Dictionary mapping repository names to efficiency values
        """
        self.data = data

    def render(self, output: Path) -> None:
        """
        Render efficiency line/scatter plot.

        Args:
            output: Output path for the chart (SVG or PNG)

        Raises:
            ChartError: If output path is invalid or not writable
        """
        self._validate_path(output)

        repos = list(self.data.keys())
        efficiency_values = list(self.data.values())

        fig, ax = plt.subplots(figsize=(12, 6))

        # Create bar chart with color gradient
        # Handle single value or identical values case
        min_val = min(efficiency_values)
        max_val = max(efficiency_values)
        if max_val - min_val == 0:
            # All values are the same, use single color
            colors = plt.cm.viridis([0.5] * len(efficiency_values))
        else:
            colors = plt.cm.viridis(
                [(v - min_val) / (max_val - min_val) for v in efficiency_values]
            )

        ax.bar(repos, efficiency_values, color=colors)
        ax.set_xlabel("Repository")
        ax.set_ylabel("LOC per Commit (Efficiency)")
        ax.set_title("Code Efficiency Metrics")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output, dpi=300, format=output.suffix[1:])
        plt.close()
