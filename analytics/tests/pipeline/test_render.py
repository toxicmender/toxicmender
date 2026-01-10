"""
Unit tests for ResultRenderer.
"""
import pytest
import json
import csv
from pathlib import Path
from analytics.pipeline.render import ResultRenderer


def test_result_renderer_init(tmp_path):
    """Test ResultRenderer initialization."""
    output_dir = tmp_path / "output"
    renderer = ResultRenderer(output_dir)

    assert renderer.output_dir == output_dir
    assert output_dir.exists()


def test_result_renderer_render_json(tmp_path):
    """Test rendering results as JSON."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "metrics": {"loc": 1000, "commits": 50},
        "scores": {"quality": 85.5}
    }

    output_path = renderer.render(test_results, format='json')

    assert output_path.exists()
    assert output_path.name == 'results.json'

    with open(output_path) as f:
        rendered = json.load(f)
    assert rendered["metrics"]["loc"] == 1000


def test_result_renderer_render_json_explicit(tmp_path):
    """Test rendering with explicit .json format."""
    renderer = ResultRenderer(tmp_path)
    test_results = {"key": "value"}

    output_path = renderer.render(test_results, format='.json')
    assert output_path.exists()


def test_result_renderer_render_csv(tmp_path):
    """Test rendering results as CSV."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "metrics": {
            "name": "Test Metric",
            "values": {"repo1": 100.0, "repo2": 200.0}
        }
    }

    output_path = renderer.render(test_results, format='csv')

    assert output_path.exists()
    assert output_path.name == 'results.csv'

    with open(output_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) > 0


def test_result_renderer_render_text(tmp_path):
    """Test rendering results as text."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "summary": {
            "total_repos": 10,
            "avg_score": 85.5
        },
        "details": ["item1", "item2"]
    }

    output_path = renderer.render(test_results, format='txt')

    assert output_path.exists()
    assert output_path.name == 'results.txt'

    content = output_path.read_text()
    assert "summary" in content
    assert "total_repos" in content


def test_result_renderer_invalid_format(tmp_path):
    """Test rendering with invalid format."""
    renderer = ResultRenderer(tmp_path)
    test_results = {"key": "value"}

    with pytest.raises(ValueError):
        renderer.render(test_results, format='pdf')


def test_result_renderer_format_with_dot(tmp_path):
    """Test format specification with leading dot."""
    renderer = ResultRenderer(tmp_path)
    test_results = {"key": "value"}

    output_path = renderer.render(test_results, format='.json')
    assert output_path.exists()


def test_result_renderer_empty_results(tmp_path):
    """Test rendering empty results."""
    renderer = ResultRenderer(tmp_path)
    test_results = {}

    # Should not raise error
    output_path = renderer.render(test_results, format='json')
    assert output_path.exists()


def test_result_renderer_nested_structure(tmp_path):
    """Test rendering deeply nested results."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "analysis": {
            "repos": [
                {
                    "name": "repo1",
                    "metrics": {
                        "loc": 5000,
                        "commits": 100,
                        "efficiency": 50.0
                    }
                }
            ]
        }
    }

    output_path = renderer.render(test_results, format='json')

    with open(output_path) as f:
        rendered = json.load(f)
    assert rendered["analysis"]["repos"][0]["metrics"]["loc"] == 5000


def test_result_renderer_multiple_formats(tmp_path):
    """Test rendering to multiple formats."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "metrics": {
            "name": "Test",
            "values": {"repo1": 100.0}
        }
    }

    json_path = renderer.render(test_results, format='json')
    csv_path = renderer.render(test_results, format='csv')
    txt_path = renderer.render(test_results, format='txt')

    assert json_path.exists()
    assert csv_path.exists()
    assert txt_path.exists()


def test_result_renderer_csv_with_lists(tmp_path):
    """Test CSV rendering with list data."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "items": [
            {"name": "item1", "value": 100},
            {"name": "item2", "value": 200}
        ]
    }

    output_path = renderer.render(test_results, format='csv')
    assert output_path.exists()


def test_result_renderer_text_formatting(tmp_path):
    """Test text format produces readable output."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "section1": {
            "subsection": "value",
            "list": ["item1", "item2"]
        }
    }

    output_path = renderer.render(test_results, format='txt')
    content = output_path.read_text()

    # Should have structured formatting
    assert "=" in content  # Header separator
    assert "section1" in content
    assert "subsection" in content


def test_result_renderer_large_results(tmp_path):
    """Test rendering large result sets."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "repos": [
            {
                "name": f"repo_{i}",
                "metrics": {
                    "loc": 1000 + i * 100,
                    "commits": 50 + i,
                    "stars": 100 + i * 10
                }
            }
            for i in range(1000)
        ]
    }

    output_path = renderer.render(test_results, format='json')

    with open(output_path) as f:
        rendered = json.load(f)
    assert len(rendered["repos"]) == 1000


def test_result_renderer_creates_output_directory(tmp_path):
    """Test that renderer creates output directory if needed."""
    output_dir = tmp_path / "deep" / "nested" / "output"
    renderer = ResultRenderer(output_dir)

    assert output_dir.exists()

    test_results = {"key": "value"}
    output_path = renderer.render(test_results, format='json')
    assert output_path.parent == output_dir


def test_result_renderer_metric_result_format(tmp_path):
    """Test rendering MetricResult format."""
    renderer = ResultRenderer(tmp_path)
    test_results = {
        "metrics": {
            "efficiency": {
                "name": "efficiency",
                "values": {
                    "repo1": 150.5,
                    "repo2": 200.3,
                    "repo3": 120.8
                }
            }
        }
    }

    csv_path = renderer.render(test_results, format='csv')

    # CSV should flatten the metric values
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) > 0
    # Should have metric data rows
    assert any('efficiency' in row.get('metric', '') for row in rows)
