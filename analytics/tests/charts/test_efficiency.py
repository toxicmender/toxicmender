"""
Unit tests for EfficiencyChart.
"""
import pytest
from analytics.charts.efficiency import EfficiencyChart
from analytics.exceptions import ChartError


def test_efficiency_chart_init():
    """Test EfficiencyChart initialization."""
    data = {"repo1": 150.0, "repo2": 200.0, "repo3": 120.0}
    chart = EfficiencyChart(data)
    assert chart.data == data


def test_efficiency_chart_render_svg(tmp_path):
    """Test EfficiencyChart rendering to SVG."""
    data = {"ProjectA": 150.5, "ProjectB": 200.3, "ProjectC": 120.8}
    chart = EfficiencyChart(data)

    output_path = tmp_path / "efficiency.svg"
    chart.render(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_efficiency_chart_render_png(tmp_path):
    """Test EfficiencyChart rendering to PNG."""
    data = {"repo1": 100.0, "repo2": 250.0}
    chart = EfficiencyChart(data)

    output_path = tmp_path / "efficiency.png"
    chart.render(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_efficiency_chart_invalid_extension(tmp_path):
    """Test EfficiencyChart with invalid file extension."""
    data = {"repo1": 150.0}
    chart = EfficiencyChart(data)

    output_path = tmp_path / "chart.pdf"
    with pytest.raises(ChartError):
        chart.render(output_path)


def test_efficiency_chart_single_repo(tmp_path):
    """Test EfficiencyChart with single repository."""
    data = {"OnlyRepo": 175.5}
    chart = EfficiencyChart(data)

    output_path = tmp_path / "chart.svg"
    chart.render(output_path)
    assert output_path.exists()


def test_efficiency_chart_large_values(tmp_path):
    """Test EfficiencyChart with large efficiency values."""
    data = {
        "HighEfficiency": 5000.0,
        "MediumEfficiency": 1000.0,
        "LowEfficiency": 50.0
    }
    chart = EfficiencyChart(data)

    output_path = tmp_path / "chart.png"
    chart.render(output_path)
    assert output_path.exists()


def test_efficiency_chart_zero_values(tmp_path):
    """Test EfficiencyChart with zero efficiency values."""
    data = {
        "Repo1": 100.0,
        "Repo2": 0.0,
        "Repo3": 50.0
    }
    chart = EfficiencyChart(data)

    output_path = tmp_path / "chart.svg"
    chart.render(output_path)
    assert output_path.exists()


def test_efficiency_chart_many_repos(tmp_path):
    """Test EfficiencyChart with many repositories."""
    data = {f"repo_{i}": float(100 + i * 10) for i in range(20)}
    chart = EfficiencyChart(data)

    output_path = tmp_path / "chart.png"
    chart.render(output_path)
    assert output_path.exists()
