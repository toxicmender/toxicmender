import pytest
from analytics.data_sources.github import GitHubSource
from analytics.exceptions import DataSourceError, ValidationError
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import json


def test_github_source_init():
    """Test GitHubSource initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = GitHubSource("torvalds", cache_dir=Path(tmpdir))
        assert source.username == "torvalds"
        assert source.cache_dir.exists()


def test_github_source_empty_username():
    """Test GitHubSource initialization with empty username."""
    with pytest.raises(ValidationError):
        GitHubSource("")


def test_github_source_fetch_success():
    """Test successful GitHub data fetch with all RepoStats fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup mock repos with all required RepoStats attributes
        mock_commits1 = MagicMock()
        mock_commits1.totalCount = 5000
        mock_commits1.__getitem__ = MagicMock(return_value=MagicMock(sha="abc123"))

        mock_commits2 = MagicMock()
        mock_commits2.totalCount = 200
        mock_commits2.__getitem__ = MagicMock(return_value=MagicMock(sha="def456"))

        mock_repo1 = MagicMock()
        mock_repo1.name = "linux"
        mock_repo1.stargazers_count = 1000
        mock_repo1.forks_count = 500
        mock_repo1.updated_at = datetime(2025, 1, 20)
        mock_repo1.get_languages.return_value = {"C": 800000, "Python": 50000, "Shell": 20000}
        mock_repo1.get_commits.return_value = mock_commits1

        mock_repo2 = MagicMock()
        mock_repo2.name = "subsurface"
        mock_repo2.stargazers_count = 500
        mock_repo2.forks_count = 100
        mock_repo2.updated_at = datetime(2025, 1, 15)
        mock_repo2.get_languages.return_value = {"C++": 60000, "C": 30000}
        mock_repo2.get_commits.return_value = mock_commits2

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("torvalds", cache_dir=Path(tmpdir))
            data = source.fetch()

            assert len(data) == 2

            # Verify all RepoStats fields for repo1
            assert data[0]["name"] == "linux"
            assert data[0]["loc"] == 870000  # Sum of all languages
            assert data[0]["commits"] == 5000
            assert data[0]["stars"] == 1000
            assert data[0]["forks"] == 500
            assert data[0]["languages"] == {"C": 800000, "Python": 50000, "Shell": 20000}
            assert "updated_at" in data[0]
            assert "latest_commit" in data[0]
            assert "cached_at" in data[0]

            # Verify all RepoStats fields for repo2
            assert data[1]["name"] == "subsurface"
            assert data[1]["loc"] == 90000  # Sum of all languages
            assert data[1]["commits"] == 200
            assert data[1]["stars"] == 500
            assert data[1]["forks"] == 100
            assert data[1]["languages"] == {"C++": 60000, "C": 30000}

            # Verify cache files were created
            cache_files = list(Path(tmpdir).glob("*.json"))
            assert len(cache_files) == 2


def test_github_source_fetch_empty_list():
    """Test GitHub fetch with no repositories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_user = MagicMock()
        mock_user.get_repos.return_value = []

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            data = source.fetch()
            assert data == []


def test_github_source_fetch_single_repo():
    """Test GitHub fetch with single repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_commits = MagicMock()
        mock_commits.totalCount = 150
        mock_commits.__getitem__ = MagicMock(return_value=MagicMock(sha="single123"))

        mock_repo = MagicMock()
        mock_repo.name = "project"
        mock_repo.stargazers_count = 42
        mock_repo.forks_count = 10
        mock_repo.updated_at = datetime(2025, 1, 10)
        mock_repo.get_languages.return_value = {"Python": 15000}
        mock_repo.get_commits.return_value = mock_commits

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            data = source.fetch()

            assert len(data) == 1
            assert data[0]["name"] == "project"
            assert data[0]["loc"] == 15000
            assert data[0]["commits"] == 150
            assert data[0]["stars"] == 42
            assert data[0]["forks"] == 10
            assert data[0]["languages"] == {"Python": 15000}


def test_github_source_fetch_command_error():
    """Test GitHub fetch when API call fails."""
    from github import GithubException

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.side_effect = GithubException(404, "Not Found")

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            with pytest.raises(DataSourceError):
                source.fetch()


def test_github_source_fetch_exception_error():
    """Test GitHub fetch with general exception."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.side_effect = Exception("Network error")

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            with pytest.raises(DataSourceError):
                source.fetch()


def test_github_source_fetch_partial_error():
    """Test GitHub fetch with API error."""
    from github import GithubException
    error = GithubException(403, "Forbidden")

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.side_effect = error

            source = GitHubSource("user", cache_dir=Path(tmpdir))

            with pytest.raises(DataSourceError) as exc_info:
                source.fetch()

            assert "Failed to fetch repos" in str(exc_info.value)


def test_github_source_fetch_calls_github_api():
    """Test that fetch calls correct GitHub API."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_user = MagicMock()
        mock_user.get_repos.return_value = []

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("testuser", cache_dir=Path(tmpdir))
            source.fetch()

            mock_github_instance.get_user.assert_called_once_with("testuser")
            mock_user.get_repos.assert_called_once()



def test_github_source_username_validation():
    """Test username validation."""
    with pytest.raises(ValidationError) as exc_info:
        GitHubSource("")

    assert "username" in str(exc_info.value).lower()


def test_github_source_none_username():
    """Test GitHubSource with None username."""
    with pytest.raises(ValidationError):
        GitHubSource(None)


def test_github_source_repo_with_empty_languages():
    """Test repository with no languages returns empty dict and LOC=1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_commits = MagicMock()
        mock_commits.totalCount = 10
        mock_commits.__getitem__ = MagicMock(return_value=MagicMock(sha="empty123"))

        mock_repo = MagicMock()
        mock_repo.name = "empty-repo"
        mock_repo.stargazers_count = 0
        mock_repo.forks_count = 0
        mock_repo.updated_at = datetime(2025, 1, 5)
        mock_repo.get_languages.return_value = {}  # No languages
        mock_repo.get_commits.return_value = mock_commits

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            data = source.fetch()

            assert len(data) == 1
            assert data[0]["loc"] == 1  # Default when no languages
            assert data[0]["languages"] == {}
            assert data[0]["commits"] == 10


def test_github_source_repo_with_multiple_languages():
    """Test repository with multiple languages calculates correct LOC."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_commits = MagicMock()
        mock_commits.totalCount = 500
        mock_commits.__getitem__ = MagicMock(return_value=MagicMock(sha="poly123"))

        mock_repo = MagicMock()
        mock_repo.name = "polyglot-repo"
        mock_repo.stargazers_count = 250
        mock_repo.forks_count = 50
        mock_repo.updated_at = datetime(2025, 1, 12)
        mock_repo.get_languages.return_value = {
            "Python": 10000,
            "JavaScript": 8000,
            "TypeScript": 12000,
            "CSS": 3000,
            "HTML": 2000
        }
        mock_repo.get_commits.return_value = mock_commits

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            data = source.fetch()

            assert len(data) == 1
            assert data[0]["loc"] == 35000  # Sum of all language LOCs
            assert len(data[0]["languages"]) == 5


def test_github_source_repo_attributes_types():
    """Test that all RepoStats attributes have correct types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_commits = MagicMock()
        mock_commits.totalCount = 100
        mock_commits.__getitem__ = MagicMock(return_value=MagicMock(sha="type123"))

        mock_repo = MagicMock()
        mock_repo.name = "test-repo"
        mock_repo.stargazers_count = 50
        mock_repo.forks_count = 25
        mock_repo.updated_at = datetime(2025, 1, 8)
        mock_repo.get_languages.return_value = {"Python": 5000}
        mock_repo.get_commits.return_value = mock_commits

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            data = source.fetch()

            repo_data = data[0]

            # Verify types match RepoStats model expectations
            assert isinstance(repo_data["name"], str)
            assert isinstance(repo_data["loc"], int)
            assert isinstance(repo_data["commits"], int)
            assert isinstance(repo_data["stars"], int)
            assert isinstance(repo_data["forks"], int)
            assert isinstance(repo_data["languages"], dict)

            # Verify all language values are integers
            for lang, loc in repo_data["languages"].items():
                assert isinstance(lang, str)
                assert isinstance(loc, int)


def test_github_source_repo_all_required_fields_present():
    """Test that all RepoStats required fields are present in returned data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_commits = MagicMock()
        mock_commits.totalCount = 75
        mock_commits.__getitem__ = MagicMock(return_value=MagicMock(sha="complete123"))

        mock_repo = MagicMock()
        mock_repo.name = "complete-repo"
        mock_repo.stargazers_count = 100
        mock_repo.forks_count = 20
        mock_repo.updated_at = datetime(2025, 1, 6)
        mock_repo.get_languages.return_value = {"Go": 7500}
        mock_repo.get_commits.return_value = mock_commits

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            data = source.fetch()

            repo_data = data[0]

            # All fields from RepoStats must be present
            required_fields = ["name", "loc", "commits", "stars", "forks", "languages"]
            for field in required_fields:
                assert field in repo_data, f"Missing required field: {field}"


def test_github_source_calls_correct_repo_methods():
    """Test that fetch calls all necessary repository methods."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_commits = MagicMock()
        mock_commits.totalCount = 50
        mock_commits.__getitem__ = MagicMock(return_value=MagicMock(sha="xyz789"))

        mock_repo = MagicMock()
        mock_repo.name = "method-test"
        mock_repo.stargazers_count = 10
        mock_repo.forks_count = 5
        mock_repo.updated_at = datetime(2025, 1, 10)
        mock_repo.get_languages.return_value = {"Ruby": 3000}
        mock_repo.get_commits.return_value = mock_commits

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))
            source.fetch()

            # Verify all necessary methods were called
            mock_repo.get_languages.assert_called_once()
            mock_repo.get_commits.assert_called()


def test_github_source_cache_validity():
    """Test cache validation based on updated_at and commit hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_commits = MagicMock()
        mock_commits.totalCount = 100
        mock_commits.__getitem__ = MagicMock(return_value=MagicMock(sha="commit123"))

        mock_repo = MagicMock()
        mock_repo.name = "cached-repo"
        mock_repo.stargazers_count = 50
        mock_repo.forks_count = 10
        mock_repo.updated_at = datetime(2025, 1, 20)
        mock_repo.get_languages.return_value = {"Python": 5000}
        mock_repo.get_commits.return_value = mock_commits

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=Path(tmpdir))

            # First fetch - should call API
            data1 = source.fetch()
            assert len(data1) == 1
            call_count1 = mock_repo.get_languages.call_count

            # Second fetch with same updated_at - should use cache
            data2 = source.fetch()
            assert len(data2) == 1
            call_count2 = mock_repo.get_languages.call_count

            # Should not have called API again (cache hit)
            assert call_count2 == call_count1

            # Update repo timestamp to invalidate cache
            mock_repo.updated_at = datetime(2025, 1, 25)
            mock_repo.get_languages.reset_mock()

            # Third fetch - should refetch due to updated timestamp
            data3 = source.fetch()
            assert len(data3) == 1
            mock_repo.get_languages.assert_called()


def test_github_source_rate_limit_handling():
    """Test that rate limit errors are handled gracefully with cache fallback."""
    from github import RateLimitExceededException

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir)

        # Pre-populate cache
        cached_data = {
            "name": "cached-repo",
            "loc": 5000,
            "commits": 100,
            "stars": 50,
            "forks": 10,
            "languages": {"Python": 5000},
            "updated_at": datetime(2025, 1, 20).isoformat(),
            "latest_commit": "abc123",
            "cached_at": datetime(2025, 1, 20).isoformat()
        }
        cache_file = cache_dir / "cached-repo.json"
        with open(cache_file, 'w') as f:
            json.dump(cached_data, f)

        mock_repo = MagicMock()
        mock_repo.name = "cached-repo"
        mock_repo.get_languages.side_effect = RateLimitExceededException(403, "Rate limit exceeded")

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]

        with patch("analytics.data_sources.github.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_user.return_value = mock_user

            source = GitHubSource("user", cache_dir=cache_dir)
            data = source.fetch()

            # Should fallback to cache
            assert len(data) == 1
            assert data[0]["name"] == "cached-repo"
            assert data[0]["loc"] == 5000


def test_github_source_get_cache_stats():
    """Test cache statistics retrieval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir)

        # Create some cache files
        for i in range(3):
            cache_file = cache_dir / f"repo{i}.json"
            with open(cache_file, 'w') as f:
                json.dump({"name": f"repo{i}"}, f)

        source = GitHubSource("user", cache_dir=cache_dir)
        stats = source.get_cache_stats()

        assert stats["total_cached"] == 3
        assert str(cache_dir) in stats["cache_dir"]
