"""
Analytics package for toxicmender.
Provides metrics computation, data source fetching, chart rendering, and scoring.
"""

try:
    import importlib.metadata
    __version__ = importlib.metadata.version("gh-profile")
except importlib.metadata.PackageNotFoundError:
    __version__ = "1.0.0"  # Fallback


from analytics.exceptions import (
    AnalyticsError,
    DataSourceError,
    ValidationError,
    MetricError,
    ChartError,
)

__all__ = [
    "__version__",
    "AnalyticsError",
    "DataSourceError",
    "ValidationError",
    "MetricError",
    "ChartError",
]
