"""
Cache-based data source for caching fetched repository data.
Implements memory-based caching with optional persistence.
"""
from analytics.data_sources.base import DataSource
from analytics.exceptions import DataSourceError
from typing import Any, Dict, Optional
import json
from pathlib import Path


class CacheDataSource(DataSource):
    """Caches data from other sources with in-memory and file-based persistence."""

    def __init__(self, cache_file: Optional[Path] = None):
        """
        Initialize cache data source.

        Args:
            cache_file: Optional path to persist cache to disk
        """
        self.cache: Dict[str, Any] = {}
        self.cache_file = cache_file
        if cache_file and cache_file.exists():
            self._load_from_file()

    def fetch(self):
        """
        Retrieve cached data.

        Returns:
            Cached data dictionary

        Raises:
            DataSourceError: If cache is empty
        """
        if not self.cache:
            raise DataSourceError("Cache is empty - no data available")
        return self.cache

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
                self.cache = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise DataSourceError(f"Failed to load cache from {self.cache_file}") from e

    def persist(self) -> None:
        """Persist cache to disk file."""
        if not self.cache_file:
            return

        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            raise DataSourceError(f"Failed to persist cache to {self.cache_file}") from e
