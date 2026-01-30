import json

from analytics.migration import MigrationManager


def test_migration_manager_migrates_legacy_data(tmp_path):
    user_dir = tmp_path / "test_user"
    user_dir.mkdir(parents=True)

    legacy_data = {
        "aggregate_metrics": {
            "total_loc": 1000,
            "total_commits": 50,
            "normalised": {"loc": 0.5, "impact": 0.2}
        },
        "repos": [
            {
                "name": "repo1",
                "loc": 1000,
                "commits": 50,
                "stars": 10,
                "forks": 1,
                "languages": {"Python": 1000}
            }
        ],
        "engineering_score": {"score": 75.0}
    }

    legacy_file = user_dir / "metrics.json"
    with open(legacy_file, "w", encoding="utf-8") as f:
        json.dump(legacy_data, f)

    manager = MigrationManager(user_dir)
    assert manager.detect_legacy_data() is True

    history = manager.migrate_user_data(username="test_user")
    assert history.username == "test_user"
    assert len(history.runs) == 1

    report = manager.validate_migration()
    assert report["success"] is True
    assert report["runs_found"] == 1
