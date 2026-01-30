import pytest
from datetime import datetime, timezone

from analytics.models.time_series import MetricSnapshot, AnalysisRun, AnalysisHistory


def test_metric_snapshot_timezone_coercion():
    snapshot = MetricSnapshot(
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        metric_name="loc",
        value=123.0
    )
    assert snapshot.timestamp.tzinfo is not None


def test_analysis_history_runs_order_validation():
    run1 = AnalysisRun(
        timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
        username="test_user",
        total_repos=0,
        total_loc=0,
        total_commits=0,
        engineering_score=0.0,
        metrics={},
        normalized_metrics={},
        repositories=[]
    )
    run2 = AnalysisRun(
        timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
        username="test_user",
        total_repos=0,
        total_loc=0,
        total_commits=0,
        engineering_score=0.0,
        metrics={},
        normalized_metrics={},
        repositories=[]
    )

    with pytest.raises(ValueError):
        AnalysisHistory(
            username="test_user",
            runs=[run1, run2]
        )


def test_analysis_run_filtered_repos_validation():
    with pytest.raises(ValueError):
        AnalysisRun(
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            username="test_user",
            total_repos=1,
            total_loc=0,
            total_commits=0,
            engineering_score=0.0,
            metrics={},
            normalized_metrics={},
            repositories=[],
            filtered_repos_count=2
        )
