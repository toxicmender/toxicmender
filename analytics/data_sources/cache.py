"""
Cache-based data source for caching fetched repository data.
Implements memory-based caching with optional persistence.
Supports both single-file and per-repo caching strategies.
"""
from analytics.data_sources.base import DataSource
from analytics.exceptions import DataSourceError
from typing import Any, Dict, Optional, List
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CacheDataSource(DataSource):
    """Caches data from other sources with in-memory and file-based persistence."""

    def __init__(self, cache_file: Optional[Path] = None, cache_dir: Optional[Path] = None) -> None:
        """
        Initialize cache data source.

        Args:
            cache_file: Optional path to persist cache to disk (legacy single file)
            cache_dir: Optional directory containing per-repo cache files
        """
        self.cache: Dict[str, Any] = {}
        self.cache_file: Optional[Path] = cache_file
        self.cache_dir: Optional[Path] = cache_dir

        # Load from cache_dir if provided (per-repo caching)
        if cache_dir and cache_dir.exists():
            self._load_from_directory()
        # Otherwise try legacy single file
        elif cache_file and cache_file.exists():
            self._load_from_file()

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Retrieve cached data.

        Returns:
            List of cached repository data dictionaries

        Raises:
            DataSourceError: If cache is empty
        """
        if not self.cache:
            raise DataSourceError("Cache is empty - no data available")

        # Return as list of repo data
        if isinstance(self.cache, list):
            return self.cache
        elif isinstance(self.cache, dict):
            # If cache is dict, return values as list
            return list(self.cache.values()) if self.cache else []

        return []

    def set_cache(self, key: str, value: Any) -> None:
        """
        Store data in cache.

        Args:
            key: Cache key
            value: Data to cache
        """
        self.cache[key] = value

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()

    def _load_from_file(self) -> None:
        """Load cache from disk file."""
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                # Store as list for consistent interface
                if isinstance(data, list):
                    self.cache = data
                else:
                    self.cache = data
            logger.info(f"Loaded cache from {self.cache_file}")
        except (json.JSONDecodeError, IOError) as e:
            raise DataSourceError(f"Failed to load cache from {self.cache_file}") from e

    def _load_from_directory(self) -> None:
        """Load cache from directory of per-repo JSON files."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            repos = []

            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        repo_data = json.load(f)
                        repos.append(repo_data)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load {cache_file}: {e}")

            self.cache = repos
            logger.info(f"Loaded {len(repos)} repos from cache directory {self.cache_dir}")
        except Exception as e:
            raise DataSourceError(f"Failed to load cache from {self.cache_dir}") from e

    def persist(self) -> None:
        """Persist cache to disk file."""
        if not self.cache_file:
            return

        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            raise DataSourceError(f"Failed to persist cache to {self.cache_file}") from e
