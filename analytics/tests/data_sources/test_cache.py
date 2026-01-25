"""
Unit tests for CacheDataSource.
"""
import pytest
import json
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
    # fetch() returns list of values when cache is dict
    assert len(result) == 1
    assert result[0] == test_data


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

    # Fetch and verify - returns list of values
    result = cache.fetch()
    assert len(result) == 2
    assert {"value": 100} in result
    assert {"value": 200} in result

    # Clear and verify empty
    cache.clear_cache()
    with pytest.raises(DataSourceError):
        cache.fetch()

    # Add new data
    cache.set_cache("data3", {"value": 300})
    result = cache.fetch()
    assert len(result) == 1
    assert {"value": 300} in result


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
    # fetch() returns list of values, so result[0] is the complex_data
    assert len(result) == 1
    assert result[0]["repos"][0]["name"] == "repo1"
    assert result[0]["summary"]["avg_stars"] == 75

def test_cache_data_source_init_with_cache_dir(tmp_path):
    """Test CacheDataSource initialization with cache directory."""
    cache_dir = tmp_path / "cache_dir"
    cache_dir.mkdir()

    cache = CacheDataSource(cache_dir=cache_dir)
    assert cache.cache_dir == cache_dir
    assert isinstance(cache.cache, list)
    assert len(cache.cache) == 0


def test_cache_data_source_load_from_directory(tmp_path):
    """Test loading cache from directory of JSON files."""
    cache_dir = tmp_path / "repos_cache"
    cache_dir.mkdir()

    # Create mock repo cache files
    repo1_data = {
        "name": "repo1",
        "loc": 5000,
        "commits": 100,
        "stars": 50,
        "forks": 10,
        "languages": {"Python": 5000}
    }
    repo2_data = {
        "name": "repo2",
        "loc": 3000,
        "commits": 75,
        "stars": 30,
        "forks": 5,
        "languages": {"JavaScript": 3000}
    }

    with open(cache_dir / "repo1.json", 'w') as f:
        json.dump(repo1_data, f)
    with open(cache_dir / "repo2.json", 'w') as f:
        json.dump(repo2_data, f)

    # Load cache from directory
    cache = CacheDataSource(cache_dir=cache_dir)
    data = cache.fetch()

    assert len(data) == 2
    assert any(repo["name"] == "repo1" for repo in data)
    assert any(repo["name"] == "repo2" for repo in data)


def test_cache_data_source_directory_with_corrupt_file(tmp_path):
    """Test loading cache directory with a corrupt file."""
    cache_dir = tmp_path / "repos_cache"
    cache_dir.mkdir()

    # Create good and corrupt files
    with open(cache_dir / "good.json", 'w') as f:
        json.dump({"name": "good_repo"}, f)

    with open(cache_dir / "bad.json", 'w') as f:
        f.write("{ invalid json")

    # Should load successfully, skipping corrupt file
    cache = CacheDataSource(cache_dir=cache_dir)
    data = cache.fetch()

    assert len(data) == 1
    assert data[0]["name"] == "good_repo"


def test_cache_data_source_fetch_returns_list_for_directory(tmp_path):
    """Test that fetch returns list when loading from directory."""
    cache_dir = tmp_path / "repos_cache"
    cache_dir.mkdir()

    repo_data = {"name": "test_repo", "stars": 100}
    with open(cache_dir / "test.json", 'w') as f:
        json.dump(repo_data, f)

    cache = CacheDataSource(cache_dir=cache_dir)
    result = cache.fetch()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == "test_repo"


def test_cache_data_source_empty_directory(tmp_path):
    """Test loading from empty cache directory."""
    cache_dir = tmp_path / "empty_cache"
    cache_dir.mkdir()

    cache = CacheDataSource(cache_dir=cache_dir)

    with pytest.raises(DataSourceError):
        cache.fetch()