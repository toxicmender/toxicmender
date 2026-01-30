from datetime import datetime, timezone
from uuid import uuid4

from analytics.history import HistoryManager
from analytics.models.time_series import AnalysisRun, AnalysisHistory


def _make_run(timestamp: datetime):
    return AnalysisRun(
        run_id=uuid4(),
        timestamp=timestamp,
        username="test_user",
        total_repos=0,
        total_loc=0,
        total_commits=0,
        engineering_score=0.0,
        metrics={},
        normalized_metrics={},
        repositories=[]
    )


def test_history_manager_save_and_load(tmp_path):
    user_dir = tmp_path / "test_user"
    manager = HistoryManager(user_dir, max_runs=10)

    run = _make_run(datetime(2024, 1, 1, tzinfo=timezone.utc))
    history = AnalysisHistory(username="test_user", runs=[run])

    manager.save(history)

    loaded = manager.load_or_create("test_user")
    assert len(loaded.runs) == 1
    assert loaded.runs[0].run_id == run.run_id


def test_history_manager_append_and_prune(tmp_path):
    user_dir = tmp_path / "test_user"
    manager = HistoryManager(user_dir, max_runs=2)

    history = AnalysisHistory(username="test_user", runs=[])

    run1 = _make_run(datetime(2024, 1, 1, tzinfo=timezone.utc))
    run2 = _make_run(datetime(2024, 1, 2, tzinfo=timezone.utc))
    run3 = _make_run(datetime(2024, 1, 3, tzinfo=timezone.utc))

    manager.append_run(history, run1)
    manager.append_run(history, run2)
    manager.append_run(history, run3)

    assert len(history.runs) == 2
    assert history.runs[0].run_id == run2.run_id
    assert history.runs[1].run_id == run3.run_id

    manager.save(history)

    # Prune to keep only 1
    removed = manager.prune_old_runs(history, keep_count=1)
    assert removed == 1
    assert len(history.runs) == 1
