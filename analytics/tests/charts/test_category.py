"""
Unit tests for CategoryChart.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from analytics.charts.category import CategoryChart
from analytics.exceptions import ChartError


def test_category_chart_init():
    """Test CategoryChart initialization."""
    data = {"Category1": [1.0, 2.0, 3.0], "Category2": [4.0, 5.0, 6.0]}
    categories = ["Metric1", "Metric2", "Metric3"]

    chart = CategoryChart(data, categories)
    assert chart.data == data
    assert chart.categories == categories


def test_category_chart_render_svg(tmp_path):
    """Test CategoryChart rendering to SVG."""
    data = {"Category1": [1.0, 2.0], "Category2": [3.0, 4.0]}
    categories = ["A", "B"]
    chart = CategoryChart(data, categories)

    output_path = tmp_path / "category_chart.svg"
    chart.render(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_category_chart_render_png(tmp_path):
    """Test CategoryChart rendering to PNG."""
    data = {"Category1": [1.0, 2.0], "Category2": [3.0, 4.0]}
    categories = ["A", "B"]
    chart = CategoryChart(data, categories)

    output_path = tmp_path / "category_chart.png"
    chart.render(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_category_chart_invalid_extension(tmp_path):
    """Test CategoryChart with invalid file extension."""
    data = {"Category1": [1.0], "Category2": [2.0]}
    categories = ["A"]
    chart = CategoryChart(data, categories)

    output_path = tmp_path / "chart.jpg"
    with pytest.raises(ChartError):
        chart.render(output_path)


def test_category_chart_invalid_directory(tmp_path):
    """Test CategoryChart with non-existent output directory."""
    data = {"Category1": [1.0], "Category2": [2.0]}
    categories = ["A"]
    chart = CategoryChart(data, categories)

    output_path = tmp_path / "nonexistent" / "chart.svg"
    with pytest.raises(ChartError):
        chart.render(output_path)


def test_category_chart_read_only_directory(tmp_path):
    """Test CategoryChart with read-only output directory."""
    data = {"Category1": [1.0], "Category2": [2.0]}
    categories = ["A"]
    chart = CategoryChart(data, categories)

    # Create a read-only directory
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)

    output_path = readonly_dir / "chart.svg"

    try:
        with pytest.raises(ChartError):
            chart.render(output_path)
    finally:
        # Restore permissions for cleanup
        readonly_dir.chmod(0o755)


def test_category_chart_empty_data(tmp_path):
    """Test CategoryChart with empty data."""
    data = {}
    categories = []
    chart = CategoryChart(data, categories)

    output_path = tmp_path / "chart.svg"
    # Should render without error even with empty data
    chart.render(output_path)
    assert output_path.exists()


def test_category_chart_multiple_categories(tmp_path):
    """Test CategoryChart with multiple categories."""
    data = {
        "Core": [10.0, 20.0, 30.0],
        "Utils": [15.0, 25.0, 35.0],
        "Testing": [5.0, 10.0, 15.0],
        "Docs": [2.0, 4.0, 6.0]
    }
    categories = ["Q1", "Q2", "Q3"]
    chart = CategoryChart(data, categories)

    output_path = tmp_path / "chart.png"
    chart.render(output_path)
    assert output_path.exists()
