"""
Unit tests for language filtering utility.
"""
import pytest
from pathlib import Path
from analytics.utils.language_filter import (
    load_language_filters,
    should_exclude_language,
    filter_repo_languages,
    filter_repos_list,
    get_filter_summary
)
from analytics.models.repo import RepoStats
import yaml
import tempfile


class TestLoadLanguageFilters:
    """Tests for load_language_filters function."""

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid configuration file."""
        config_file = tmp_path / "filters.yml"
        config_data = {
            'excluded_languages': ['HTML', 'CSS'],
            'filter_enabled': True,
            'minimum_language_loc': 100,
            'remove_empty_repos': True,
            'case_sensitive': False
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        result = load_language_filters(config_file)

        assert result['excluded_languages'] == ['HTML', 'CSS']
        assert result['filter_enabled'] is True
        assert result['minimum_language_loc'] == 100
        assert result['remove_empty_repos'] is True
        assert result['case_sensitive'] is False

    def test_load_config_with_defaults(self, tmp_path):
        """Test loading config with missing keys uses defaults."""
        config_file = tmp_path / "filters.yml"
        config_data = {'excluded_languages': ['HTML']}

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        result = load_language_filters(config_file)

        assert result['excluded_languages'] == ['HTML']
        assert result['filter_enabled'] is True  # default
        assert result['minimum_language_loc'] == 0  # default

    def test_load_nonexistent_config(self):
        """Test loading non-existent config raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_language_filters(Path("nonexistent.yml"))


class TestShouldExcludeLanguage:
    """Tests for should_exclude_language function."""

    def test_exclude_exact_match(self):
        """Test excluding language with exact match."""
        assert should_exclude_language('HTML', ['HTML', 'CSS']) is True

    def test_exclude_case_insensitive(self):
        """Test case-insensitive matching (default)."""
        assert should_exclude_language('html', ['HTML', 'CSS']) is True
        assert should_exclude_language('HtMl', ['HTML', 'CSS']) is True

    def test_exclude_case_sensitive(self):
        """Test case-sensitive matching when enabled."""
        assert should_exclude_language('html', ['HTML', 'CSS'], case_sensitive=True) is False
        assert should_exclude_language('HTML', ['HTML', 'CSS'], case_sensitive=True) is True

    def test_not_excluded(self):
        """Test language not in exclusion list."""
        assert should_exclude_language('Python', ['HTML', 'CSS']) is False

    def test_empty_exclusion_list(self):
        """Test with empty exclusion list."""
        assert should_exclude_language('Python', []) is False


class TestFilterRepoLanguages:
    """Tests for filter_repo_languages function."""

    def test_filter_excludes_languages(self):
        """Test filtering removes excluded languages."""
        repo = RepoStats(
            name="test-repo",
            loc=1500,
            commits=10,
            stars=5,
            forks=2,
            languages={'Python': 1000, 'HTML': 300, 'CSS': 200}
        )

        filtered = filter_repo_languages(repo, ['HTML', 'CSS'])

        assert 'Python' in filtered.languages
        assert 'HTML' not in filtered.languages
        assert 'CSS' not in filtered.languages
        assert filtered.loc == 1000

    def test_filter_recalculates_loc(self):
        """Test that LOC is recalculated after filtering."""
        repo = RepoStats(
            name="test-repo",
            loc=1500,
            commits=10,
            languages={'Python': 1000, 'JavaScript': 300, 'HTML': 200}
        )

        filtered = filter_repo_languages(repo, ['HTML'])

        assert filtered.loc == 1300  # 1000 + 300

    def test_filter_tracks_original_loc(self):
        """Test that original LOC is tracked when filtering."""
        repo = RepoStats(
            name="test-repo",
            loc=1500,
            commits=10,
            languages={'Python': 1000, 'HTML': 500}
        )

        filtered = filter_repo_languages(repo, ['HTML'], track_filtered=True)

        assert filtered.original_loc == 1500
        assert 'HTML' in filtered.filtered_languages

    def test_filter_minimum_loc_threshold(self):
        """Test filtering by minimum LOC threshold."""
        repo = RepoStats(
            name="test-repo",
            loc=1550,
            commits=10,
            languages={'Python': 1000, 'JavaScript': 500, 'Ruby': 50}
        )

        filtered = filter_repo_languages(repo, [], minimum_loc=100)

        assert 'Python' in filtered.languages
        assert 'JavaScript' in filtered.languages
        assert 'Ruby' not in filtered.languages
        assert filtered.loc == 1500

    def test_filter_all_languages_removed(self):
        """Test when all languages are filtered out."""
        repo = RepoStats(
            name="test-repo",
            loc=500,
            commits=10,
            languages={'HTML': 300, 'CSS': 200}
        )

        filtered = filter_repo_languages(repo, ['HTML', 'CSS'])

        assert len(filtered.languages) == 0
        assert filtered.loc == 1  # Minimum value for PositiveInt

    def test_no_filtering_when_no_exclusions(self):
        """Test that no filtering occurs with empty exclusion list."""
        repo = RepoStats(
            name="test-repo",
            loc=1000,
            commits=10,
            languages={'Python': 1000}
        )

        filtered = filter_repo_languages(repo, [])

        assert filtered.languages == repo.languages
        assert filtered.loc == repo.loc


class TestFilterReposList:
    """Tests for filter_repos_list function."""

    def test_filter_multiple_repos(self):
        """Test filtering a list of repositories."""
        repos = [
            RepoStats(name="repo1", loc=1000, commits=10, languages={'Python': 1000}),
            RepoStats(name="repo2", loc=500, commits=5, languages={'HTML': 500}),
            RepoStats(name="repo3", loc=1500, commits=15, languages={'Python': 1000, 'CSS': 500})
        ]

        config = {
            'filter_enabled': True,
            'excluded_languages': ['HTML', 'CSS'],
            'minimum_language_loc': 0,
            'remove_empty_repos': True,
            'case_sensitive': False
        }

        filtered = filter_repos_list(repos, config)

        # repo2 should be removed (only had HTML)
        assert len(filtered) == 2
        assert filtered[0].name == "repo1"
        assert filtered[1].name == "repo3"
        assert filtered[1].loc == 1000  # CSS removed

    def test_filter_disabled(self):
        """Test that filtering is skipped when disabled."""
        repos = [
            RepoStats(name="repo1", loc=1000, commits=10, languages={'HTML': 1000})
        ]

        config = {
            'filter_enabled': False,
            'excluded_languages': ['HTML']
        }

        filtered = filter_repos_list(repos, config)

        assert len(filtered) == 1
        assert 'HTML' in filtered[0].languages

    def test_keep_empty_repos_when_configured(self):
        """Test keeping repos with no languages after filtering."""
        repos = [
            RepoStats(name="repo1", loc=500, commits=5, languages={'HTML': 500})
        ]

        config = {
            'filter_enabled': True,
            'excluded_languages': ['HTML'],
            'remove_empty_repos': False
        }

        filtered = filter_repos_list(repos, config)

        assert len(filtered) == 1
        assert len(filtered[0].languages) == 0

    def test_no_filters_configured(self):
        """Test behavior when no filters are configured."""
        repos = [
            RepoStats(name="repo1", loc=1000, commits=10, languages={'Python': 1000})
        ]

        config = {
            'filter_enabled': True,
            'excluded_languages': [],
            'minimum_language_loc': 0
        }

        filtered = filter_repos_list(repos, config)

        assert len(filtered) == 1
        assert filtered == repos


class TestGetFilterSummary:
    """Tests for get_filter_summary function."""

    def test_summary_statistics(self):
        """Test that summary contains correct statistics."""
        repos_before = [
            RepoStats(name="repo1", loc=1000, commits=10, languages={'Python': 1000}),
            RepoStats(name="repo2", loc=500, commits=5, languages={'HTML': 500})
        ]

        repos_after = [
            RepoStats(
                name="repo1",
                loc=1000,
                commits=10,
                languages={'Python': 1000},
                original_loc=1000,
                filtered_languages=[]
            )
        ]

        summary = get_filter_summary(repos_before, repos_after)

        assert summary['repos_before'] == 2
        assert summary['repos_after'] == 1
        assert summary['repos_removed'] == 1
        assert summary['loc_before'] == 1500
        assert summary['loc_after'] == 1000
        assert summary['loc_removed'] == 500

    def test_summary_tracks_filtered_languages(self):
        """Test that summary includes list of filtered languages."""
        repos_before = [
            RepoStats(name="repo1", loc=1500, commits=10, languages={'Python': 1000, 'HTML': 300, 'CSS': 200})
        ]

        repos_after = [
            RepoStats(
                name="repo1",
                loc=1000,
                commits=10,
                languages={'Python': 1000},
                original_loc=1500,
                filtered_languages=['HTML', 'CSS']
            )
        ]

        summary = get_filter_summary(repos_before, repos_after)

        assert 'HTML' in summary['filtered_languages']
        assert 'CSS' in summary['filtered_languages']
