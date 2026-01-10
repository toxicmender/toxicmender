import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from analytics.pipeline.visualize import Visualizer
from analytics.charts.language import LanguageChart


def test_visualizer_init():
    """Test Visualizer initialization."""
    mock_chart = MagicMock()
    charts = [(mock_chart, Path("output.png"))]

    visualizer = Visualizer(charts)
    assert visualizer.charts == charts


def test_visualizer_run_single_chart(tmp_path):
    """Test Visualizer runs single chart."""
    mock_chart = MagicMock()
    output_path = tmp_path / "chart.png"
    charts = [(mock_chart, output_path)]

    visualizer = Visualizer(charts)
    visualizer.run()

    mock_chart.render.assert_called_once_with(output_path)


def test_visualizer_run_multiple_charts(tmp_path):
    """Test Visualizer runs multiple charts."""
    mock_chart1 = MagicMock()
    mock_chart2 = MagicMock()
    mock_chart3 = MagicMock()

    path1 = tmp_path / "chart1.png"
    path2 = tmp_path / "chart2.png"
    path3 = tmp_path / "chart3.png"

    charts = [
        (mock_chart1, path1),
        (mock_chart2, path2),
        (mock_chart3, path3)
    ]

    visualizer = Visualizer(charts)
    visualizer.run()

    mock_chart1.render.assert_called_once_with(path1)
    mock_chart2.render.assert_called_once_with(path2)
    mock_chart3.render.assert_called_once_with(path3)


def test_visualizer_run_empty():
    """Test Visualizer with no charts."""
    visualizer = Visualizer([])
    # Should not raise any errors
    visualizer.run()


def test_visualizer_real_chart(tmp_path):
    """Test Visualizer with real LanguageChart."""
    chart = LanguageChart({"Python": 60, "JavaScript": 40})
    output = tmp_path / "languages.svg"

    visualizer = Visualizer([(chart, output)])
    visualizer.run()

    assert output.exists()


def test_visualizer_preserves_order(tmp_path):
    """Test Visualizer renders charts in order."""
    call_order = []

    def make_chart(name):
        mock = MagicMock()
        mock.render.side_effect = lambda p: call_order.append(name)
        return mock

    charts = [
        (make_chart("first"), tmp_path / "1.png"),
        (make_chart("second"), tmp_path / "2.png"),
        (make_chart("third"), tmp_path / "3.png")
    ]

    visualizer = Visualizer(charts)
    visualizer.run()

    assert call_order == ["first", "second", "third"]


def test_visualizer_chart_error_propagates(tmp_path):
    """Test that chart render errors propagate."""
    mock_chart = MagicMock()
    mock_chart.render.side_effect = RuntimeError("Render failed")

    visualizer = Visualizer([(mock_chart, tmp_path / "chart.png")])

    with pytest.raises(RuntimeError):
        visualizer.run()


def test_visualizer_different_formats(tmp_path):
    """Test Visualizer with different output formats."""
    mock_chart1 = MagicMock()
    mock_chart2 = MagicMock()

    charts = [
        (mock_chart1, tmp_path / "chart.png"),
        (mock_chart2, tmp_path / "chart.svg")
    ]

    visualizer = Visualizer(charts)
    visualizer.run()

    mock_chart1.render.assert_called_once()
    mock_chart2.render.assert_called_once()
