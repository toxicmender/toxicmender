"""History management for analysis runs."""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import logging

from analytics.models.time_series import AnalysisRun, AnalysisHistory
from uuid import UUID

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages persistence and retrieval of analysis history."""

    def __init__(self, data_dir: Path, max_runs: int = 100):
        """
        Initialize history manager.

        Args:
            data_dir: Root data directory (e.g., data/username)
            max_runs: Maximum number of runs to keep per user
        """
        self.data_dir = Path(data_dir)
        self.history_dir = self.data_dir / "history"
        self.runs_dir = self.history_dir / "runs"
        self.index_file = self.history_dir / "index.json"
        self.max_runs = max_runs

    def load_or_create(self, username: str) -> AnalysisHistory:
        """
        Load existing history or create new one.

        Args:
            username: GitHub username

        Returns:
            AnalysisHistory instance (loaded or new)
        """
        if self.index_file.exists():
            return self._load_history(username)
        else:
            logger.info(f"Creating new history for: {username}")
            return AnalysisHistory(
                username=username,
                runs=[],
                version="2.0.0"
            )

    def _load_history(self, username: str) -> AnalysisHistory:
        """
        Load history from disk.

        Args:
            username: GitHub username

        Returns:
            AnalysisHistory instance

        Raises:
            FileNotFoundError: If history files missing
            json.JSONDecodeError: If JSON is malformed
        """
        # Load index
        with open(self.index_file, 'r') as f:
            index_data = json.load(f)

        # Validate username match
        if index_data["username"] != username:
            raise ValueError(
                f"Username mismatch: expected {username}, "
                f"got {index_data['username']}"
            )

        # Load runs
        run_ids = index_data.get("run_ids", [])
        runs = []

        for run_id_str in run_ids:
            run_file = self.runs_dir / f"{run_id_str}.json"
            if not run_file.exists():
                logger.warning(f"Run file missing: {run_file}")
                continue

            with open(run_file, 'r') as f:
                run_data = json.load(f)

            # Convert timestamps to datetime objects
            run_data = self._parse_timestamps(run_data)
            runs.append(AnalysisRun(**run_data))

        logger.info(f"Loaded history: {len(runs)} runs for {username}")

        return AnalysisHistory(
            username=username,
            created_at=datetime.fromisoformat(index_data["created_at"]),
            updated_at=datetime.fromisoformat(index_data["updated_at"]),
            runs=runs,
            version=index_data.get("version", "2.0.0")
        )

    def _parse_timestamps(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse timestamp strings to datetime objects.

        Args:
            run_data: Raw run data from JSON

        Returns:
            Run data with parsed timestamps
        """
        if "timestamp" in run_data and isinstance(run_data["timestamp"], str):
            run_data["timestamp"] = datetime.fromisoformat(run_data["timestamp"])

        # Parse UUID strings
        if "run_id" in run_data and isinstance(run_data["run_id"], str):
            run_data["run_id"] = UUID(run_data["run_id"])

        return run_data

    def append_run(self, history: AnalysisHistory, run: AnalysisRun) -> AnalysisHistory:
        """
        Append new run to history.

        Args:
            history: Existing history
            run: New analysis run

        Returns:
            Updated history (mutable update)
        """
        # Add run
        history.runs.append(run)

        # Update timestamp
        history.updated_at = datetime.now(timezone.utc)

        # Prune if needed
        if len(history.runs) > self.max_runs:
            removed_count = len(history.runs) - self.max_runs
            history.runs = history.runs[-self.max_runs:]
            logger.info(f"Pruned {removed_count} oldest runs")

        return history

    def save(self, history: AnalysisHistory) -> None:
        """
        Save history to disk.

        Args:
            history: AnalysisHistory to persist
        """
        # Create directory structure
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(exist_ok=True)

        # Save index
        index_data = {
            "username": history.username,
            "created_at": history.created_at.isoformat(),
            "updated_at": history.updated_at.isoformat(),
            "version": history.version,
            "run_count": len(history.runs),
            "run_ids": [str(run.run_id) for run in history.runs]
        }

        with open(self.index_file, 'w') as f:
            json.dump(index_data, f, indent=2)

        # Save individual runs
        for run in history.runs:
            run_file = self.runs_dir / f"{run.run_id}.json"
            run_dict = run.model_dump(mode='json')

            with open(run_file, 'w') as f:
                json.dump(run_dict, f, indent=2)

        logger.info(f"Saved history: {len(history.runs)} runs")

    def prune_old_runs(self, history: AnalysisHistory, keep_count: int) -> int:
        """
        Remove old runs, keeping only most recent.

        Args:
            history: AnalysisHistory to prune
            keep_count: Number of recent runs to keep

        Returns:
            Number of runs removed
        """
        if len(history.runs) <= keep_count:
            return 0

        removed_count = len(history.runs) - keep_count
        removed_runs = history.runs[:removed_count]

        # Delete run files
        for run in removed_runs:
            run_file = self.runs_dir / f"{run.run_id}.json"
            if run_file.exists():
                run_file.unlink()

        # Update history
        history.runs = history.runs[-keep_count:]
        history.updated_at = datetime.now(timezone.utc)

        logger.info(f"Pruned {removed_count} runs, {keep_count} remaining")

        return removed_count

    def get_run_by_id(self, run_id: UUID) -> Optional[AnalysisRun]:
        """
        Load specific run by ID.

        Args:
            run_id: UUID of run to load

        Returns:
            AnalysisRun if found, None otherwise
        """
        run_file = self.runs_dir / f"{run_id}.json"
        if not run_file.exists():
            return None

        with open(run_file, 'r') as f:
            run_data = json.load(f)

        run_data = self._parse_timestamps(run_data)
        return AnalysisRun(**run_data)

    def delete_run(self, history: AnalysisHistory, run_id: UUID) -> bool:
        """
        Delete specific run from history.

        Args:
            history: AnalysisHistory to modify
            run_id: UUID of run to delete

        Returns:
            True if deleted, False if not found
        """
        # Find and remove from history
        original_count = len(history.runs)
        history.runs = [r for r in history.runs if r.run_id != run_id]

        if len(history.runs) == original_count:
            return False  # Not found

        # Delete file
        run_file = self.runs_dir / f"{run_id}.json"
        if run_file.exists():
            run_file.unlink()

        # Update timestamp
        history.updated_at = datetime.now(timezone.utc)

        logger.info(f"Deleted run: {run_id}")
        return True


__all__ = ["HistoryManager"]
