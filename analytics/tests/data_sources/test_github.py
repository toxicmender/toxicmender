import pytest
from analytics.data_sources.github import GitHubSource
from analytics.exceptions import DataSourceError, ValidationError
from unittest.mock import patch, MagicMock
import json


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
    mock_output = json.dumps([
        {"name": "linux", "stargazerCount": 1000},
        {"name": "subsurface", "stargazerCount": 500}
    ])

    with patch("subprocess.check_output", return_value=mock_output):
        source = GitHubSource("torvalds")
        data = source.fetch()

        assert len(data) == 2
        assert data[0]["name"] == "linux"
        assert data[0]["stargazerCount"] == 1000
        assert data[1]["name"] == "subsurface"
        assert data[1]["stargazerCount"] == 500


def test_github_source_fetch_empty_list():
    """Test GitHub fetch with no repositories."""
    mock_output = json.dumps([])

    with patch("subprocess.check_output", return_value=mock_output):
        source = GitHubSource("user")
        data = source.fetch()
        assert data == []


def test_github_source_fetch_single_repo():
    """Test GitHub fetch with single repository."""
    mock_output = json.dumps([
        {"name": "project", "stargazerCount": 42}
    ])

    with patch("subprocess.check_output", return_value=mock_output):
        source = GitHubSource("user")
        data = source.fetch()

        assert len(data) == 1
        assert data[0]["name"] == "project"


def test_github_source_fetch_command_error():
    """Test GitHub fetch when gh command fails."""
    with patch("subprocess.check_output") as mock_check:
        mock_check.side_effect = Exception("gh command not found")
        source = GitHubSource("user")

        with pytest.raises(DataSourceError):
            source.fetch()


def test_github_source_fetch_json_error():
    """Test GitHub fetch with invalid JSON response."""
    with patch("subprocess.check_output", return_value="invalid json"):
        source = GitHubSource("user")

        with pytest.raises(DataSourceError):
            source.fetch()


def test_github_source_fetch_partial_error():
    """Test GitHub fetch with subprocess error."""
    import subprocess
    error = subprocess.CalledProcessError(1, "gh")

    with patch("subprocess.check_output", side_effect=error):
        source = GitHubSource("user")

        with pytest.raises(DataSourceError) as exc_info:
            source.fetch()

        assert "Failed to fetch repos" in str(exc_info.value)


def test_github_source_fetch_calls_gh_command():
    """Test that fetch calls correct gh command."""
    mock_output = json.dumps([])

    with patch("subprocess.check_output") as mock_check:
        mock_check.return_value = mock_output
        source = GitHubSource("testuser")
        source.fetch()

        mock_check.assert_called_once()
        call_args = mock_check.call_args[0][0]

        assert "gh" in call_args
        assert "repo" in call_args
        assert "list" in call_args
        assert "testuser" in call_args
        assert "--json" in call_args


def test_github_source_username_validation():
    """Test username validation."""
    with pytest.raises(ValidationError) as exc_info:
        GitHubSource("")

    assert "username" in str(exc_info.value).lower()


def test_github_source_none_username():
    """Test GitHubSource with None username."""
    with pytest.raises(ValidationError):
        GitHubSource(None)
