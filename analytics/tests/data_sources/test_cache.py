"""
Unit tests for CacheDataSource.
"""
import pytest
import json
from pathlib import Path
from analytics.data_sources.cache import CacheDataSource
from analytics.exceptions import DataSourceError


def test_cache_data_source_init_without_file():
    """Test CacheDataSource initialization without file."""
    cache = CacheDataSource()
    assert cache.cache == {}
    assert cache.cache_file is None


def test_cache_data_source_init_with_file(tmp_path):
    """Test CacheDataSource initialization with cache file."""
    cache_file = tmp_path / "cache.json"
    cache = CacheDataSource(cache_file=cache_file)
    assert cache.cache == {}
    assert cache.cache_file == cache_file


def test_cache_data_source_set_cache():
    """Test setting cache values."""
    cache = CacheDataSource()
    cache.set_cache("key1", {"data": "value1"})

    assert "key1" in cache.cache
    assert cache.cache["key1"] == {"data": "value1"}


def test_cache_data_source_fetch_empty():
    """Test fetching from empty cache."""
    cache = CacheDataSource()
    with pytest.raises(DataSourceError):
        cache.fetch()


def test_cache_data_source_fetch_with_data():
    """Test fetching data from cache."""
    cache = CacheDataSource()
    test_data = {"repo1": {"stars": 100}}
    cache.set_cache("repos", test_data)

    result = cache.fetch()
    assert "repos" in result


def test_cache_data_source_clear_cache():
    """Test clearing cache."""
    cache = CacheDataSource()
    cache.set_cache("key1", "value1")
    cache.set_cache("key2", "value2")

    assert len(cache.cache) == 2
    cache.clear_cache()
    assert len(cache.cache) == 0


def test_cache_data_source_persist_and_load(tmp_path):
    """Test persisting cache to file and loading it."""
    cache_file = tmp_path / "cache.json"

    # Create and populate cache
    cache1 = CacheDataSource(cache_file=cache_file)
    cache1.set_cache("repo1", {"stars": 100, "forks": 10})
    cache1.set_cache("repo2", {"stars": 50, "forks": 5})
    cache1.persist()

    # Verify file exists
    assert cache_file.exists()

    # Load in new cache instance
    cache2 = CacheDataSource(cache_file=cache_file)
    assert len(cache2.cache) == 2
    assert cache2.cache["repo1"]["stars"] == 100
    assert cache2.cache["repo2"]["forks"] == 5


def test_cache_data_source_persist_creates_file(tmp_path):
    """Test persist creates cache file."""
    cache_file = tmp_path / "new_cache.json"
    cache = CacheDataSource(cache_file=cache_file)
    cache.set_cache("test", "data")
    cache.persist()

    assert cache_file.exists()
    with open(cache_file, 'r') as f:
        data = json.load(f)
    assert data == {"test": "data"}


def test_cache_data_source_persist_without_file():
    """Test persist with no cache file specified."""
    cache = CacheDataSource()
    cache.set_cache("key", "value")
    # Should not raise error
    cache.persist()


def test_cache_data_source_load_existing_file(tmp_path):
    """Test loading existing cache file."""
    cache_file = tmp_path / "existing.json"
    test_data = {"repo1": {"stars": 100}, "repo2": {"stars": 50}}

    with open(cache_file, 'w') as f:
        json.dump(test_data, f)

    cache = CacheDataSource(cache_file=cache_file)
    assert cache.cache == test_data


def test_cache_data_source_load_corrupt_file(tmp_path):
    """Test loading corrupt cache file."""
    cache_file = tmp_path / "corrupt.json"
    with open(cache_file, 'w') as f:
        f.write("{ invalid json")

    with pytest.raises(DataSourceError):
        CacheDataSource(cache_file=cache_file)


def test_cache_data_source_multiple_operations():
    """Test multiple cache operations."""
    cache = CacheDataSource()

    # Add data
    cache.set_cache("data1", {"value": 100})
    cache.set_cache("data2", {"value": 200})

    # Fetch and verify
    result = cache.fetch()
    assert len(result) == 2

    # Clear and verify empty
    cache.clear_cache()
    with pytest.raises(DataSourceError):
        cache.fetch()

    # Add new data
    cache.set_cache("data3", {"value": 300})
    result = cache.fetch()
    assert "data3" in result


def test_cache_data_source_complex_data():
    """Test caching complex data structures."""
    cache = CacheDataSource()
    complex_data = {
        "repos": [
            {"name": "repo1", "metrics": {"stars": 100, "loc": 5000}},
            {"name": "repo2", "metrics": {"stars": 50, "loc": 2000}}
        ],
        "summary": {
            "total": 2,
            "avg_stars": 75
        }
    }

    cache.set_cache("analysis", complex_data)
    result = cache.fetch()
    assert result["analysis"]["repos"][0]["name"] == "repo1"
    assert result["analysis"]["summary"]["avg_stars"] == 75
