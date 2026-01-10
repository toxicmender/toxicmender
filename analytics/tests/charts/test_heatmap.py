"""
Unit tests for HeatmapChart.
"""
import pytest
from pathlib import Path
from analytics.charts.heatmap import HeatmapChart
from analytics.exceptions import ChartError


def test_heatmap_chart_init():
    """Test HeatmapChart initialization."""
    data = {
        "Metric1": [1.0, 2.0, 3.0],
        "Metric2": [4.0, 5.0, 6.0],
        "Metric3": [7.0, 8.0, 9.0]
    }
    metric_names = ["Metric1", "Metric2", "Metric3"]
    chart = HeatmapChart(data, metric_names)

    assert chart.data == data
    assert chart.metric_names == metric_names


def test_heatmap_chart_render_svg(tmp_path):
    """Test HeatmapChart rendering to SVG."""
    data = {
        "Efficiency": [10.0, 20.0, 15.0],
        "Impact": [5.0, 25.0, 18.0],
        "Scale": [8.0, 22.0, 12.0]
    }
    metric_names = ["Efficiency", "Impact", "Scale"]
    chart = HeatmapChart(data, metric_names)

    output_path = tmp_path / "heatmap.svg"
    chart.render(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_heatmap_chart_render_png(tmp_path):
    """Test HeatmapChart rendering to PNG."""
    data = {
        "Metric1": [1.0, 2.0],
        "Metric2": [3.0, 4.0]
    }
    metric_names = ["Metric1", "Metric2"]
    chart = HeatmapChart(data, metric_names)

    output_path = tmp_path / "heatmap.png"
    chart.render(output_path)

    assert output_path.exists()


def test_heatmap_chart_invalid_extension(tmp_path):
    """Test HeatmapChart with invalid file extension."""
    data = {"M1": [1.0, 2.0]}
    metric_names = ["M1"]
    chart = HeatmapChart(data, metric_names)

    output_path = tmp_path / "chart.gif"
    with pytest.raises(ChartError):
        chart.render(output_path)


def test_heatmap_chart_single_metric(tmp_path):
    """Test HeatmapChart with single metric."""
    data = {"OnlyMetric": [5.0, 10.0, 15.0]}
    metric_names = ["OnlyMetric"]
    chart = HeatmapChart(data, metric_names)

    output_path = tmp_path / "chart.svg"
    chart.render(output_path)
    assert output_path.exists()


def test_heatmap_chart_high_correlation(tmp_path):
    """Test HeatmapChart with highly correlated metrics."""
    # Create metrics with strong correlation
    data = {
        "Metric1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "Metric2": [2.0, 4.0, 6.0, 8.0, 10.0],  # Perfect correlation with Metric1
        "Metric3": [5.0, 4.0, 3.0, 2.0, 1.0]    # Inverse correlation
    }
    metric_names = list(data.keys())
    chart = HeatmapChart(data, metric_names)

    output_path = tmp_path / "heatmap.png"
    chart.render(output_path)
    assert output_path.exists()


def test_heatmap_chart_many_metrics(tmp_path):
    """Test HeatmapChart with many metrics."""
    data = {f"Metric{i}": [float(j) for j in range(10)] for i in range(10)}
    metric_names = list(data.keys())
    chart = HeatmapChart(data, metric_names)

    output_path = tmp_path / "heatmap.svg"
    chart.render(output_path)
    assert output_path.exists()


def test_heatmap_chart_zero_variance(tmp_path):
    """Test HeatmapChart with zero-variance metrics."""
    data = {
        "Constant1": [5.0, 5.0, 5.0],
        "Constant2": [10.0, 10.0, 10.0]
    }
    metric_names = list(data.keys())
    chart = HeatmapChart(data, metric_names)

    output_path = tmp_path / "heatmap.png"
    chart.render(output_path)
    assert output_path.exists()
