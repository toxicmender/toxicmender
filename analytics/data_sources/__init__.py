"""
Data sources module for fetching repository data.
Provides implementations for various data source types.
"""

from analytics.data_sources.base import DataSource
from analytics.data_sources.github import GitHubSource
from analytics.data_sources.cache import CacheDataSource
from analytics.data_sources.filesystem import FilesystemDataSource

__all__ = [
    "DataSource",
    "GitHubSource",
    "CacheDataSource",
    "FilesystemDataSource",
]
