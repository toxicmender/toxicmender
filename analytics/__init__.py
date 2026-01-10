"""
Analytics package for toxicmender.
Provides metrics computation, data source fetching, chart rendering, and scoring.
"""

from analytics.exceptions import (
    AnalyticsError,
    DataSourceError,
    ValidationError,
    MetricError,
    ChartError,
)

__version__ = "0.1.0"
__all__ = [
    "AnalyticsError",
    "DataSourceError",
    "ValidationError",
    "MetricError",
    "ChartError",
]
