from pathlib import Path
import json

from analytics.pipeline import analyse


def test_analyse_creates_history(tmp_path):
    username = "test_user"
    user_dir = tmp_path / username
    user_dir.mkdir(parents=True)

    repos = [
        {
            "name": "repo-one",
            "loc": 1000,
            "commits": 10,
            "stars": 5,
            "forks": 1,
            "languages": {"Python": 1000}
        },
        {
            "name": "repo-two",
            "loc": 500,
            "commits": 5,
            "stars": 2,
            "forks": 0,
            "languages": {"Python": 500}
        }
    ]

    repos_file = user_dir / "repositories.json"
    with open(repos_file, "w", encoding="utf-8") as f:
        json.dump(repos, f)

    analyse.run(input_dir=tmp_path, output_dir=tmp_path)

    history_dir = user_dir / "history"
    index_file = history_dir / "index.json"
    runs_dir = history_dir / "runs"

    assert index_file.exists()
    assert runs_dir.exists()

    with open(index_file, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    assert index_data["username"] == username
    assert index_data["run_count"] == 1
    assert len(index_data["run_ids"]) == 1

    run_id = index_data["run_ids"][0]
    run_file = runs_dir / f"{run_id}.json"
    assert run_file.exists()
