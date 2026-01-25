"""
Data collection pipeline stage.
Coordinates fetching data from various sources and preparing it for analysis.
"""
from analytics.pipeline.base import PipelineStep
from analytics.data_sources.base import DataSource
from analytics.data_sources.github import GitHubSource
from analytics.data_sources.cache import CacheDataSource
from analytics.models.repo import RepoStats
from analytics.exceptions import DataSourceError
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


class DataCollector(PipelineStep):
    """Orchestrates data collection from configured sources."""

    def __init__(self, sources: List[DataSource]):
        """
        Initialize data collector with multiple sources.

        Args:
            sources: List of DataSource implementations to fetch from
        """
        super().__init__("DataCollector")
        self.sources = sources

    def execute(self, **kwargs) -> List[RepoStats]:
        """
        Execute data collection from all sources.

        Returns:
            List of RepoStats objects

        Raises:
            DataSourceError: If all sources fail or no sources provided
        """
        return self.collect()

    def collect(self) -> List[RepoStats]:
        """
        Collect data from all sources and aggregate.

        Returns:
            List of RepoStats objects

        Raises:
            DataSourceError: If all sources fail or no sources provided
        """
        if not self.sources:
            raise DataSourceError("No data sources configured")

        all_repos: List[RepoStats] = []
        errors: List[str] = []

        for source in self.sources:
            try:
                logger.info(f"Collecting from {source.__class__.__name__}")
                raw_data = source.fetch()
                repos = self._parse_repo_data(raw_data)
                all_repos.extend(repos)
                logger.info(f"Successfully collected {len(repos)} repositories")
            except Exception as e:
                error_msg = f"Collection from {source.__class__.__name__} failed: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)

        if not all_repos:
            if errors:
                raise DataSourceError(
                    f"Failed to collect data from any source. Errors: {errors}"
                )
            else:
                raise DataSourceError("No repository data collected from sources")

        # Remove duplicates by repository name
        unique_repos: Dict[str, RepoStats] = {}
        for repo in all_repos:
            if repo.name not in unique_repos:
                unique_repos[repo.name] = repo

        return list(unique_repos.values())

    def _parse_repo_data(self, raw_data: Any) -> List[RepoStats]:
        """
        Parse raw data into RepoStats objects.

        Args:
            raw_data: Raw data from source (list of dicts or similar)

        Returns:
            List of RepoStats objects

        Raises:
            DataSourceError: If data cannot be parsed
        """
        repos: List[RepoStats] = []

        if isinstance(raw_data, list):
            for item in raw_data:
                try:
                    repo = self._parse_repo_item(item)
                    if repo:
                        repos.append(repo)
                except Exception as e:
                    logger.debug(f"Failed to parse repo item {item}: {e}")
        elif isinstance(raw_data, dict):
            try:
                repo = self._parse_repo_item(raw_data)
                if repo:
                    repos.append(repo)
            except Exception as e:
                logger.debug(f"Failed to parse repo data: {e}")

        return repos

    def _parse_repo_item(self, item: Dict[str, Any]) -> RepoStats:
        """
        Parse single repository item into RepoStats.

        Args:
            item: Dictionary containing repository data

        Returns:
            RepoStats object

        Raises:
            ValueError: If required fields are missing
        """
        return RepoStats(
            name=item.get('name', item.get('repo_name', 'Unknown')),
            loc=int(item.get('loc', item.get('lines_of_code', 0))),
            commits=int(item.get('commits', item.get('commit_count', 0))),
            stars=int(item.get('stars', item.get('stargazers_count', 0))),
            forks=int(item.get('forks', item.get('forks_count', 0))),
            languages=item.get('languages', {})
        )

def run(username: str, output_dir: Path = Path("data"), github_token: Optional[str] = None) -> None:
    """
    Run data collection pipeline step.

    Args:
        username: GitHub username to collect data for
        output_dir: Directory to save collected data
        github_token: Optional GitHub personal access token for higher rate limits
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = output_dir / "repos_cache"

    # Configure data sources - GitHubSource now handles its own caching
    sources = [
        GitHubSource(username=username, cache_dir=cache_dir, token=github_token),
        # Fallback to cache directory if GitHub fetch fails
        CacheDataSource(cache_dir=cache_dir)
    ]

    # Collect data
    collector = DataCollector(sources=sources)
    repos = collector.run()

    # Save collected data
    output_file = output_dir / "repositories.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(
            [repo.__dict__ for repo in repos],
            f,
            indent=2,
            default=str
        )

    logger.info(f"Saved {len(repos)} repositories to {output_file}")
