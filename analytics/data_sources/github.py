from analytics.data_sources.base import DataSource
from analytics.exceptions import DataSourceError
from analytics.utils.validation import require_non_empty
from github import Github, GithubException, RateLimitExceededException
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GitHubSource(DataSource):
    def __init__(self, username: str, cache_dir: Optional[Path] = None, token: Optional[str] = None):
        """
        Initialize GitHub data source with per-repo caching.

        Args:
            username: GitHub username to fetch repos from
            cache_dir: Directory to cache individual repo data (defaults to data/{username}/repos_cache)
            token: GitHub personal access token for higher rate limits
        """
        require_non_empty(username, "username")
        self.username = username
        self.client = Github(token) if token else Github()
        self.cache_dir = cache_dir or Path(f"data/{username}/repos_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch all repositories with per-repo caching and rate limit handling.

        Returns:
            List of repository data dictionaries

        Raises:
            DataSourceError: If fetching fails critically
        """
        try:
            user = self.client.get_user(self.username)
            repos = list(user.get_repos())

            result = []
            failed_repos = []

            logger.info(f"Found {len(repos)} repositories for {self.username}")

            for idx, repo in enumerate(repos, 1):
                try:
                    logger.info(f"Processing repo {idx}/{len(repos)}: {repo.name}")
                    repo_data = self._fetch_or_load_repo(repo)
                    result.append(repo_data)
                except RateLimitExceededException as e:
                    logger.warning(f"Rate limit hit on repo {repo.name}. Cached data: {len(result)}/{len(repos)}")
                    failed_repos.append(repo.name)
                    # Try to load from cache if available
                    cached_data = self._load_from_cache(repo.name)
                    if cached_data:
                        logger.info(f"Loaded {repo.name} from cache")
                        result.append(cached_data)
                    else:
                        logger.warning(f"No cache available for {repo.name}, skipping")
                except Exception as e:
                    logger.warning(f"Failed to fetch {repo.name}: {e}")
                    failed_repos.append(repo.name)
                    # Try to load from cache
                    cached_data = self._load_from_cache(repo.name)
                    if cached_data:
                        logger.info(f"Loaded {repo.name} from cache after error")
                        result.append(cached_data)

            if failed_repos:
                logger.warning(f"Failed to fetch {len(failed_repos)} repos: {failed_repos}")
                logger.info(f"Successfully retrieved {len(result)}/{len(repos)} repositories")

            return result

        except GithubException as e:
            raise DataSourceError(
                f"Failed to fetch repos for {self.username} via GitHub API: {e}"
            ) from e
        except Exception as e:
            raise DataSourceError(
                f"Failed to fetch repos for {self.username} due to unexpected error {e}"
            ) from e

    def _fetch_or_load_repo(self, repo) -> Dict[str, Any]:
        """
        Fetch repo data or load from cache if valid.

        Args:
            repo: PyGithub Repository object

        Returns:
            Repository data dictionary
        """
        cache_file = self.cache_dir / f"{repo.name}.json"

        # Try to load from cache first
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)

                # Validate cache
                if self._is_cache_valid(cached_data, repo):
                    logger.debug(f"Using valid cache for {repo.name}")
                    return cached_data
                else:
                    logger.debug(f"Cache for {repo.name} is stale, refetching")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache for {repo.name}: {e}")

        # Fetch fresh data
        repo_data = self._fetch_repo_data(repo)

        # Save to cache
        self._save_to_cache(repo.name, repo_data)

        return repo_data

    def _fetch_repo_data(self, repo) -> Dict[str, Any]:
        """
        Fetch repository data from GitHub API.

        Args:
            repo: PyGithub Repository object

        Returns:
            Repository data dictionary
        """
        # Get languages with their line counts
        languages = repo.get_languages()

        # Calculate total LOC from all languages
        loc = sum(languages.values()) if languages else 1

        # Get latest commit hash for cache validation
        try:
            commits = repo.get_commits()
            commit_count = commits.totalCount
            latest_commit = commits[0].sha if commit_count > 0 else None
        except Exception as e:
            logger.warning(f"Failed to get commits for {repo.name}: {e}")
            commit_count = 0
            latest_commit = None

        return {
            "name": repo.name,
            "loc": loc,
            "commits": commit_count,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "languages": languages if languages else {},
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "latest_commit": latest_commit,
            "cached_at": datetime.now(timezone.utc).isoformat()
        }

    def _is_cache_valid(self, cached_data: Dict[str, Any], repo) -> bool:
        """
        Check if cached data is still valid.

        Args:
            cached_data: Cached repository data
            repo: PyGithub Repository object

        Returns:
            True if cache is valid, False otherwise
        """
        # Check if repo has been updated since cache
        if repo.updated_at and cached_data.get('updated_at'):
            cached_updated = datetime.fromisoformat(cached_data['updated_at'])
            if repo.updated_at > cached_updated:
                logger.debug(f"Repo {repo.name} updated: {repo.updated_at} > {cached_updated}")
                return False

        # Check latest commit hash if available
        if cached_data.get('latest_commit'):
            try:
                commits = repo.get_commits()
                if commits.totalCount > 0:
                    current_latest = commits[0].sha
                    if current_latest != cached_data['latest_commit']:
                        logger.debug(f"Commit mismatch for {repo.name}")
                        return False
            except Exception as e:
                logger.debug(f"Failed to check commit hash for {repo.name}: {e}")
                # If we can't verify, assume cache is valid to avoid unnecessary API calls
                return True

        return True

    def _save_to_cache(self, repo_name: str, data: Dict[str, Any]) -> None:
        """
        Save repository data to cache file.

        Args:
            repo_name: Repository name
            data: Repository data to cache
        """
        cache_file = self.cache_dir / f"{repo_name}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {repo_name} to cache")
        except IOError as e:
            logger.warning(f"Failed to save cache for {repo_name}: {e}")

    def _load_from_cache(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Load repository data from cache file.

        Args:
            repo_name: Repository name

        Returns:
            Cached data if available, None otherwise
        """
        cache_file = self.cache_dir / f"{repo_name}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache for {repo_name}: {e}")
            return None

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get statistics about cached repositories.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        return {
            "total_cached": len(cache_files),
            "cache_dir": str(self.cache_dir)
        }