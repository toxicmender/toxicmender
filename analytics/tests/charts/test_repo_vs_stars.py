"""
Unit tests for RepoVsStarsChart.
"""
import pytest
from pathlib import Path
from analytics.charts.repo_vs_stars import RepoVsStarsChart
from analytics.exceptions import ChartError


def test_repo_vs_stars_chart_init():
    """Test RepoVsStarsChart initialization."""
    data = {
        "repo1": (150.0, 100),
        "repo2": (200.0, 250),
        "repo3": (120.0, 50)
    }
    chart = RepoVsStarsChart(data)
    assert chart.data == data
    assert chart.x_label == "Metric Value"


def test_repo_vs_stars_chart_custom_label():
    """Test RepoVsStarsChart with custom x-label."""
    data = {"repo1": (100.0, 50)}
    chart = RepoVsStarsChart(data, x_label="LOC")
    assert chart.x_label == "LOC"


def test_repo_vs_stars_chart_render_svg(tmp_path):
    """Test RepoVsStarsChart rendering to SVG."""
    data = {
        "ProjectA": (150.5, 100),
        "ProjectB": (200.3, 250),
        "ProjectC": (120.8, 75)
    }
    chart = RepoVsStarsChart(data, x_label="LOC per Commit")

    output_path = tmp_path / "scatter.svg"
    chart.render(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_repo_vs_stars_chart_render_png(tmp_path):
    """Test RepoVsStarsChart rendering to PNG."""
    data = {
        "repo1": (100.0, 50),
        "repo2": (250.0, 300)
    }
    chart = RepoVsStarsChart(data)

    output_path = tmp_path / "scatter.png"
    chart.render(output_path)

    assert output_path.exists()


def test_repo_vs_stars_chart_invalid_extension(tmp_path):
    """Test RepoVsStarsChart with invalid file extension."""
    data = {"repo1": (100.0, 50)}
    chart = RepoVsStarsChart(data)

    output_path = tmp_path / "chart.jpg"
    with pytest.raises(ChartError):
        chart.render(output_path)


def test_repo_vs_stars_chart_single_repo(tmp_path):
    """Test RepoVsStarsChart with single repository."""
    data = {"OnlyRepo": (175.5, 200)}
    chart = RepoVsStarsChart(data)

    output_path = tmp_path / "chart.svg"
    chart.render(output_path)
    assert output_path.exists()


def test_repo_vs_stars_chart_zero_stars(tmp_path):
    """Test RepoVsStarsChart with repositories having no stars."""
    data = {
        "PopularRepo": (100.0, 1000),
        "UnpopularRepo": (50.0, 0),
        "ModerateRepo": (150.0, 100)
    }
    chart = RepoVsStarsChart(data, x_label="Code Efficiency")

    output_path = tmp_path / "chart.png"
    chart.render(output_path)
    assert output_path.exists()


def test_repo_vs_stars_chart_many_repos(tmp_path):
    """Test RepoVsStarsChart with many repositories."""
    data = {
        f"repo_{i}": (float(100 + i * 10), 50 + i * 5)
        for i in range(30)
    }
    chart = RepoVsStarsChart(data, x_label="Commits")

    output_path = tmp_path / "chart.svg"
    chart.render(output_path)
    assert output_path.exists()


def test_repo_vs_stars_chart_large_star_counts(tmp_path):
    """Test RepoVsStarsChart with very large star counts."""
    data = {
        "VeryPopular": (1500.0, 50000),
        "Popular": (1200.0, 10000),
        "Moderate": (500.0, 100)
    }
    chart = RepoVsStarsChart(data, x_label="LOC")

    output_path = tmp_path / "chart.png"
    chart.render(output_path)
    assert output_path.exists()
