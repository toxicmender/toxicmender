"""
Unit tests for DataCollector.
"""
import pytest
from unittest.mock import MagicMock
from analytics.pipeline.collect import DataCollector
from analytics.exceptions import DataSourceError


def test_data_collector_init():
    """Test DataCollector initialization."""
    mock_sources = [MagicMock(), MagicMock()]
    collector = DataCollector(mock_sources)
    assert collector.sources == mock_sources


def test_data_collector_single_source():
    """Test collecting from single data source."""
    mock_source = MagicMock()
    mock_source.fetch.return_value = [
        {"name": "repo1", "loc": 1000, "commits": 10, "stars": 50, "languages": {"Python": 1000}}
    ]

    collector = DataCollector([mock_source])
    result = collector.collect()

    assert len(result) == 1
    assert result[0].name == "repo1"
    assert result[0].loc == 1000


def test_data_collector_multiple_sources():
    """Test collecting from multiple data sources."""
    mock_source1 = MagicMock()
    mock_source1.fetch.return_value = [
        {"name": "repo1", "loc": 1000, "commits": 10, "stars": 50, "languages": {"Python": 1000}}
    ]

    mock_source2 = MagicMock()
    mock_source2.fetch.return_value = [
        {"name": "repo2", "loc": 2000, "commits": 20, "stars": 100, "languages": {"Go": 2000}}
    ]

    collector = DataCollector([mock_source1, mock_source2])
    result = collector.collect()

    assert len(result) == 2
    assert result[0].name == "repo1"
    assert result[1].name == "repo2"


def test_data_collector_deduplication():
    """Test that duplicate repositories are deduplicated."""
    mock_source1 = MagicMock()
    mock_source1.fetch.return_value = [
        {"name": "repo1", "loc": 1000, "commits": 10, "stars": 50, "languages": {"Python": 1000}}
    ]

    mock_source2 = MagicMock()
    mock_source2.fetch.return_value = [
        {"name": "repo1", "loc": 1000, "commits": 10, "stars": 50, "languages": {"Python": 1000}}
    ]

    collector = DataCollector([mock_source1, mock_source2])
    result = collector.collect()

    # Should only have one repo (deduplicated)
    assert len(result) == 1
    assert result[0].name == "repo1"


def test_data_collector_source_failure():
    """Test collector when one source fails."""
    mock_source1 = MagicMock()
    mock_source1.fetch.side_effect = Exception("Network error")

    mock_source2 = MagicMock()
    mock_source2.fetch.return_value = [
        {"name": "repo1", "loc": 1000, "commits": 10, "stars": 50, "languages": {"Python": 1000}}
    ]

    collector = DataCollector([mock_source1, mock_source2])
    result = collector.collect()

    # Should succeed with data from source2
    assert len(result) == 1
    assert result[0].name == "repo1"


def test_data_collector_all_sources_fail():
    """Test collector when all sources fail."""
    mock_source1 = MagicMock()
    mock_source1.fetch.side_effect = Exception("Error 1")

    mock_source2 = MagicMock()
    mock_source2.fetch.side_effect = Exception("Error 2")

    collector = DataCollector([mock_source1, mock_source2])

    with pytest.raises(DataSourceError):
        collector.collect()


def test_data_collector_empty_sources():
    """Test collector with empty sources list."""
    collector = DataCollector([])

    with pytest.raises(DataSourceError):
        collector.collect()


def test_data_collector_source_returns_empty():
    """Test collector when source returns empty list."""
    mock_source = MagicMock()
    mock_source.fetch.return_value = []

    collector = DataCollector([mock_source])

    with pytest.raises(DataSourceError):
        collector.collect()


def test_data_collector_parse_variants():
    """Test parsing different field name variants."""
    mock_source = MagicMock()
    mock_source.fetch.return_value = [
        {
            "repo_name": "repo1",
            "lines_of_code": 1000,
            "commit_count": 10,
            "stargazers_count": 50,
            "forks_count": 5,
            "languages": {"Python": 1000}
        }
    ]

    collector = DataCollector([mock_source])
    result = collector.collect()

    assert result[0].name == "repo1"
    assert result[0].loc == 1000
    assert result[0].commits == 10
    assert result[0].stars == 50
    assert result[0].forks == 5


def test_data_collector_missing_optional_fields():
    """Test parsing with missing optional fields."""
    mock_source = MagicMock()
    mock_source.fetch.return_value = [
        {
            "name": "repo1",
            "loc": 1000,
            "commits": 10
            # Missing: stars, forks, languages
        }
    ]

    collector = DataCollector([mock_source])
    result = collector.collect()

    assert result[0].name == "repo1"
    assert result[0].stars == 0
    assert result[0].forks == 0
    assert result[0].languages == {}


def test_data_collector_dict_input():
    """Test collector with dict input instead of list."""
    mock_source = MagicMock()
    mock_source.fetch.return_value = {
        "name": "repo1",
        "loc": 1000,
        "commits": 10,
        "stars": 50,
        "languages": {"Python": 1000}
    }

    collector = DataCollector([mock_source])
    result = collector.collect()

    assert len(result) == 1
    assert result[0].name == "repo1"


def test_data_collector_large_dataset():
    """Test collector with large dataset."""
    mock_source = MagicMock()
    mock_source.fetch.return_value = [
        {
            "name": f"repo_{i}",
            "loc": 1000 + i * 100,
            "commits": 10 + i,
            "stars": 50 + i * 10,
            "languages": {"Python": 1000 + i * 100}
        }
        for i in range(100)
    ]

    collector = DataCollector([mock_source])
    result = collector.collect()

    assert len(result) == 100
    assert result[0].name == "repo_0"
    assert result[99].name == "repo_99"
