"""Time-series models for tracking metric evolution over time."""

from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4


class MetricSnapshot(BaseModel):
    """Single point-in-time measurement."""
    model_config = {'frozen': True}

    timestamp: datetime
    metric_name: str
    value: float
    normalized_value: Optional[float] = Field(None, ge=0.0, le=1.0)
    repo_name: Optional[str] = None  # None = aggregate

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Ensure timestamp is timezone-aware (UTC)."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator('metric_name')
    @classmethod
    def validate_metric_name(cls, v: str) -> str:
        """Validate metric name is not empty."""
        if not v or not v.strip():
            raise ValueError("metric_name cannot be empty")
        return v.strip()

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: float) -> float:
        """Ensure value is finite."""
        if not (-1e308 < v < 1e308):
            raise ValueError("value must be finite")
        return v


class AnalysisRun(BaseModel):
    """Complete analysis execution record."""
    model_config = {'frozen': True}

    run_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    username: str = Field(min_length=1, max_length=100)

    # Summary metrics
    total_repos: int = Field(ge=0)
    total_loc: int = Field(ge=0)
    total_commits: int = Field(ge=0)
    engineering_score: float = Field(ge=0.0, le=100.0)

    # Aggregate metrics (per-user)
    metrics: Dict[str, float]  # {metric_name: raw_value}
    normalized_metrics: Dict[str, float]  # {metric_name: normalized}

    # Per-repository data
    repositories: List[Dict[str, Any]]

    # Configuration snapshot
    config: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    analysis_duration_seconds: Optional[float] = Field(None, ge=0.0)
    filtered_repos_count: Optional[int] = Field(None, ge=0)

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Ensure timestamp is timezone-aware (UTC)."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        v = v.strip()
        if not v:
            raise ValueError("username cannot be empty")
        # GitHub username constraints
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("username must be alphanumeric with optional hyphens/underscores")
        return v

    @model_validator(mode='after')
    def validate_metrics(self) -> 'AnalysisRun':
        """Validate normalized metrics are in [0, 1] range."""
        for metric_name, value in self.normalized_metrics.items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"Normalized metric {metric_name} must be in [0, 1], got {value}")
        return self

    @model_validator(mode='after')
    def validate_filtered_repos(self) -> 'AnalysisRun':
        """Ensure filtered_repos_count doesn't exceed total_repos."""
        if self.filtered_repos_count is not None:
            if self.filtered_repos_count > self.total_repos:
                raise ValueError("filtered_repos_count cannot exceed total_repos")
        return self


class AnalysisHistory(BaseModel):
    """Master history container."""
    model_config = {'frozen': False}  # Mutable to allow appending runs

    username: str = Field(min_length=1, max_length=100)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    runs: List[AnalysisRun] = Field(default_factory=list)
    version: str = Field(default="2.0.0", pattern=r'^\d+\.\d+\.\d+$')

    @field_validator('created_at', 'updated_at')
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Ensure timestamps are timezone-aware (UTC)."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @model_validator(mode='after')
    def validate_timestamps_order(self) -> 'AnalysisHistory':
        """Ensure created_at <= updated_at."""
        if self.created_at > self.updated_at:
            raise ValueError("created_at cannot be after updated_at")
        return self

    @model_validator(mode='after')
    def validate_runs_order(self) -> 'AnalysisHistory':
        """Ensure runs are in chronological order."""
        if len(self.runs) > 1:
            for i in range(len(self.runs) - 1):
                if self.runs[i].timestamp > self.runs[i + 1].timestamp:
                    raise ValueError("Runs must be in chronological order")
        return self

    def get_latest(self) -> Optional[AnalysisRun]:
        """Get most recent analysis run."""
        return self.runs[-1] if self.runs else None

    def get_by_id(self, run_id: UUID) -> Optional[AnalysisRun]:
        """Get run by UUID."""
        return next((r for r in self.runs if r.run_id == run_id), None)

    def get_range(self, start: datetime, end: datetime) -> List[AnalysisRun]:
        """Get runs within time range (inclusive)."""
        # Ensure timezone-aware
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        return [r for r in self.runs if start <= r.timestamp <= end]


__all__ = [
    "MetricSnapshot",
    "AnalysisRun",
    "AnalysisHistory",
]


