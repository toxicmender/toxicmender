class AnalyticsError(Exception):
    """Base exception for analytics pipeline"""


class DataSourceError(AnalyticsError):
    """Raised when data fetching fails"""


class ValidationError(AnalyticsError):
    """Raised when input data is invalid"""


class MetricError(AnalyticsError):
    """Raised when metric computation fails"""


class ChartError(AnalyticsError):
    """Raised when chart rendering fails"""
