import pytest
from analytics.data_sources.github import GitHubSource
from analytics.exceptions import DataSourceError, ValidationError
from unittest.mock import patch, MagicMock


def test_github_source_init():
    """Test GitHubSource initialization."""
    source = GitHubSource("torvalds")
    assert source.username == "torvalds"


def test_github_source_empty_username():
    """Test GitHubSource initialization with empty username."""
    with pytest.raises(ValidationError):
        GitHubSource("")


def test_github_source_fetch_success():
    """Test successful GitHub data fetch."""
    mock_repo1 = MagicMock()
    mock_repo1.name = "linux"
    mock_repo1.stargazers_count = 1000

    mock_repo2 = MagicMock()
    mock_repo2.name = "subsurface"
    mock_repo2.stargazers_count = 500

    mock_user = MagicMock()
    mock_user.get_repos.return_value = [mock_repo1, mock_repo2]

    with patch("analytics.data_sources.github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.return_value = mock_user

        source = GitHubSource("torvalds")
        data = source.fetch()

        assert len(data) == 2
        assert data[0]["name"] == "linux"
        assert data[0]["stargazerCount"] == 1000
        assert data[1]["name"] == "subsurface"
        assert data[1]["stargazerCount"] == 500


def test_github_source_fetch_empty_list():
    """Test GitHub fetch with no repositories."""
    mock_user = MagicMock()
    mock_user.get_repos.return_value = []

    with patch("analytics.data_sources.github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.return_value = mock_user

        source = GitHubSource("user")
        data = source.fetch()
        assert data == []


def test_github_source_fetch_single_repo():
    """Test GitHub fetch with single repository."""
    mock_repo = MagicMock()
    mock_repo.name = "project"
    mock_repo.stargazers_count = 42

    mock_user = MagicMock()
    mock_user.get_repos.return_value = [mock_repo]

    with patch("analytics.data_sources.github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.return_value = mock_user

        source = GitHubSource("user")
        data = source.fetch()

        assert len(data) == 1
        assert data[0]["name"] == "project"


def test_github_source_fetch_command_error():
    """Test GitHub fetch when API call fails."""
    from github import GithubException

    with patch("analytics.data_sources.github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.side_effect = GithubException(404, "Not Found")

        source = GitHubSource("user")
        with pytest.raises(DataSourceError):
            source.fetch()


def test_github_source_fetch_exception_error():
    """Test GitHub fetch with general exception."""
    with patch("analytics.data_sources.github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.side_effect = Exception("Network error")

        source = GitHubSource("user")
        with pytest.raises(DataSourceError):
            source.fetch()


def test_github_source_fetch_partial_error():
    """Test GitHub fetch with API error."""
    from github import GithubException
    error = GithubException(403, "Forbidden")

    with patch("analytics.data_sources.github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.side_effect = error

        source = GitHubSource("user")

        with pytest.raises(DataSourceError) as exc_info:
            source.fetch()

        assert "Failed to fetch repos" in str(exc_info.value)


def test_github_source_fetch_calls_github_api():
    """Test that fetch calls correct GitHub API."""
    mock_user = MagicMock()
    mock_user.get_repos.return_value = []

    with patch("analytics.data_sources.github.Github") as mock_github:
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.return_value = mock_user

        source = GitHubSource("testuser")
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
