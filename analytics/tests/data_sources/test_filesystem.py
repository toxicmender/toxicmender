"""
Unit tests for FilesystemDataSource.
"""
import pytest
import json
import csv
from pathlib import Path
from analytics.data_sources.filesystem import FilesystemDataSource
from analytics.exceptions import DataSourceError


def test_filesystem_data_source_init(tmp_path):
    """Test FilesystemDataSource initialization."""
    json_file = tmp_path / "data.json"
    json_file.write_text("{}")

    source = FilesystemDataSource(json_file)
    assert source.file_path == json_file


def test_filesystem_data_source_missing_file(tmp_path):
    """Test FilesystemDataSource with missing file."""
    missing_file = tmp_path / "missing.json"
    with pytest.raises(DataSourceError):
        FilesystemDataSource(missing_file)


def test_filesystem_data_source_unsupported_format(tmp_path):
    """Test FilesystemDataSource with unsupported format."""
    unsupported_file = tmp_path / "data.pdf"
    unsupported_file.touch()

    with pytest.raises(DataSourceError):
        FilesystemDataSource(unsupported_file)


def test_filesystem_data_source_fetch_json(tmp_path):
    """Test fetching JSON file."""
    json_file = tmp_path / "repos.json"
    test_data = [
        {"name": "repo1", "stars": 100},
        {"name": "repo2", "stars": 50}
    ]
    json_file.write_text(json.dumps(test_data))

    source = FilesystemDataSource(json_file)
    result = source.fetch()

    assert len(result) == 2
    assert result[0]["name"] == "repo1"
    assert result[1]["stars"] == 50


def test_filesystem_data_source_fetch_csv(tmp_path):
    """Test fetching CSV file."""
    csv_file = tmp_path / "repos.csv"

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'stars'])
        writer.writeheader()
        writer.writerow({'name': 'repo1', 'stars': '100'})
        writer.writerow({'name': 'repo2', 'stars': '50'})

    source = FilesystemDataSource(csv_file)
    result = source.fetch()

    assert len(result) == 2
    assert result[0]['name'] == 'repo1'
    assert result[1]['stars'] == '50'


def test_filesystem_data_source_fetch_yaml(tmp_path):
    """Test fetching YAML file."""
    yaml_file = tmp_path / "config.yml"
    yaml_content = """
repos:
  - name: repo1
    stars: 100
  - name: repo2
    stars: 50
"""
    yaml_file.write_text(yaml_content)

    source = FilesystemDataSource(yaml_file)
    result = source.fetch()

    assert "repos" in result
    assert len(result["repos"]) == 2


def test_filesystem_data_source_json_invalid(tmp_path):
    """Test fetching invalid JSON."""
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{ invalid json")

    source = FilesystemDataSource(json_file)
    with pytest.raises(DataSourceError):
        source.fetch()


def test_filesystem_data_source_empty_json(tmp_path):
    """Test fetching empty JSON file."""
    json_file = tmp_path / "empty.json"
    json_file.write_text("[]")

    source = FilesystemDataSource(json_file)
    result = source.fetch()

    assert result == []


def test_filesystem_data_source_json_object(tmp_path):
    """Test fetching JSON object (not array)."""
    json_file = tmp_path / "object.json"
    test_data = {"name": "single_repo", "stars": 100}
    json_file.write_text(json.dumps(test_data))

    source = FilesystemDataSource(json_file)
    result = source.fetch()

    assert result["name"] == "single_repo"
    assert result["stars"] == 100


def test_filesystem_data_source_csv_empty(tmp_path):
    """Test fetching empty CSV file."""
    csv_file = tmp_path / "empty.csv"

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'stars'])
        writer.writeheader()

    source = FilesystemDataSource(csv_file)
    result = source.fetch()

    assert result == []


def test_filesystem_data_source_yaml_extension(tmp_path):
    """Test both .yml and .yaml extensions."""
    yaml_file = tmp_path / "config.yaml"
    yaml_content = "key: value"
    yaml_file.write_text(yaml_content)

    source = FilesystemDataSource(yaml_file)
    result = source.fetch()

    assert result["key"] == "value"


def test_filesystem_data_source_large_json(tmp_path):
    """Test fetching large JSON file."""
    json_file = tmp_path / "large.json"
    large_data = [{"name": f"repo_{i}", "stars": i * 100} for i in range(1000)]
    json_file.write_text(json.dumps(large_data))

    source = FilesystemDataSource(json_file)
    result = source.fetch()

    assert len(result) == 1000
    assert result[500]["stars"] == 50000


def test_filesystem_data_source_csv_multiple_fields(tmp_path):
    """Test CSV with multiple fields."""
    csv_file = tmp_path / "repos.csv"

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'stars', 'forks', 'loc', 'commits'])
        writer.writeheader()
        writer.writerow({'name': 'repo1', 'stars': '100', 'forks': '10', 'loc': '5000', 'commits': '50'})

    source = FilesystemDataSource(csv_file)
    result = source.fetch()

    assert len(result) == 1
    assert result[0]['loc'] == '5000'
    assert result[0]['commits'] == '50'


def test_filesystem_data_source_nested_json(tmp_path):
    """Test fetching nested JSON structure."""
    json_file = tmp_path / "nested.json"
    test_data = {
        "summary": {
            "total": 2,
            "avg_stars": 75
        },
        "repos": [
            {
                "name": "repo1",
                "metrics": {"stars": 100, "forks": 10}
            }
        ]
    }
    json_file.write_text(json.dumps(test_data))

    source = FilesystemDataSource(json_file)
    result = source.fetch()

    assert result["summary"]["total"] == 2
    assert result["repos"][0]["metrics"]["forks"] == 10
