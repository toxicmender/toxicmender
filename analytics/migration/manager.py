"""Migration utilities for v1.x to v2.0 data format."""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json
import shutil
import logging
from uuid import uuid4

from analytics.models.time_series import AnalysisRun, AnalysisHistory

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages data migration from v1.x to v2.0 format."""

    def __init__(self, data_dir: Path):
        """
        Initialize migration manager.

        Args:
            data_dir: Root data directory (e.g., data/username)
        """
        self.data_dir = Path(data_dir)
        self.history_dir = self.data_dir / "history"
        self.legacy_metrics_file = self.data_dir / "metrics.json"
        self.backup_dir = self.data_dir / "backup_v1"

    def detect_legacy_data(self) -> bool:
        """
        Check if legacy v1.x data exists.

        Returns:
            True if legacy data found, False otherwise
        """
        return self.legacy_metrics_file.exists() and not self.history_dir.exists()

    def backup_legacy_data(self) -> Path:
        """
        Create backup of legacy data before migration.

        Returns:
            Path to backup directory

        Raises:
            IOError: If backup fails
        """
        if not self.legacy_metrics_file.exists():
            raise FileNotFoundError(f"No legacy data found at {self.legacy_metrics_file}")

        # Create backup with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"metrics_{timestamp}.json"

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.legacy_metrics_file, backup_path)

        logger.info(f"Legacy data backed up to: {backup_path}")
        return backup_path

    def migrate_user_data(self, username: str, force: bool = False) -> AnalysisHistory:
        """
        Migrate legacy metrics.json to v2.0 history format.

        Args:
            username: GitHub username
            force: If True, overwrite existing history

        Returns:
            Created AnalysisHistory instance

        Raises:
            FileNotFoundError: If legacy data not found
            ValueError: If history already exists and force=False
            ValidationError: If legacy data is invalid
        """
        # Check preconditions
        if not self.legacy_metrics_file.exists():
            raise FileNotFoundError(f"No legacy data at {self.legacy_metrics_file}")

        if self.history_dir.exists() and not force:
            raise ValueError(
                f"History already exists at {self.history_dir}. "
                "Use force=True to overwrite."
            )

        # Backup first
        backup_path = self.backup_legacy_data()
        logger.info(f"Created backup: {backup_path}")

        # Load legacy data
        with open(self.legacy_metrics_file, 'r') as f:
            legacy_data = json.load(f)

        # Validate legacy data structure
        self._validate_legacy_data(legacy_data)

        # Convert to v2.0 format
        analysis_run = self._convert_legacy_to_run(legacy_data, username)

        # Create history
        history = AnalysisHistory(
            username=username,
            runs=[analysis_run],
            version="2.0.0"
        )

        # Save to new structure
        self._save_history(history)

        logger.info(f"Migration complete: {username}")
        logger.info(f"  Backup: {backup_path}")
        logger.info(f"  History: {self.history_dir}")

        return history

    def _validate_legacy_data(self, data: Dict[str, Any]) -> None:
        """
        Validate legacy data structure.

        Args:
            data: Legacy metrics.json content

        Raises:
            ValueError: If data structure is invalid
        """
        required_fields = ["aggregate_metrics", "repos"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Legacy data missing required field: {field}")

        # Validate aggregate_metrics
        agg = data["aggregate_metrics"]
        if not isinstance(agg, dict):
            raise ValueError("aggregate_metrics must be a dict")

        # Validate repos
        repos = data["repos"]
        if not isinstance(repos, list):
            raise ValueError("repos must be a list")

        logger.info(f"Validated legacy data: {len(repos)} repositories")

    def _convert_legacy_to_run(
        self,
        legacy_data: Dict[str, Any],
        username: str
    ) -> AnalysisRun:
        """
        Convert legacy metrics.json to AnalysisRun.

        Args:
            legacy_data: Legacy data structure
            username: GitHub username

        Returns:
            AnalysisRun instance with migrated data
        """
        agg = legacy_data["aggregate_metrics"]
        repos = legacy_data["repos"]

        # Extract summary stats
        total_loc = int(agg.get("total_loc", 0))
        total_commits = int(agg.get("total_commits", 0))
        total_repos = len(repos)

        # Engineering score (may not exist in v1)
        engineering_score = float(legacy_data.get("engineering_score", {}).get("score", 0.0))

        # Extract normalized metrics
        normalized = {}
        if "normalised" in agg:
            for key, value in agg["normalised"].items():
                if isinstance(value, (int, float)):
                    normalized[key] = float(value)

        # Extract raw metrics
        metrics = {}
        for key, value in agg.items():
            if key not in ["normalised", "total_loc", "total_commits"] and isinstance(value, (int, float)):
                metrics[key] = float(value)

        # Migration timestamp
        migration_timestamp = datetime.now(timezone.utc)

        # Create AnalysisRun
        return AnalysisRun(
            run_id=uuid4(),
            timestamp=migration_timestamp,
            username=username,
            total_repos=total_repos,
            total_loc=total_loc,
            total_commits=total_commits,
            engineering_score=engineering_score,
            metrics=metrics,
            normalized_metrics=normalized,
            repositories=repos,
            config={
                "migrated_from": "v1.x",
                "migration_timestamp": migration_timestamp.isoformat(),
                "original_file": str(self.legacy_metrics_file)
            }
        )

    def _save_history(self, history: AnalysisHistory) -> None:
        """
        Save history to v2.0 structure.

        Args:
            history: AnalysisHistory to save
        """
        # Create directory structure
        self.history_dir.mkdir(parents=True, exist_ok=True)
        runs_dir = self.history_dir / "runs"
        runs_dir.mkdir(exist_ok=True)

        # Save index
        index_file = self.history_dir / "index.json"
        index_data = {
            "username": history.username,
            "created_at": history.created_at.isoformat(),
            "updated_at": history.updated_at.isoformat(),
            "version": history.version,
            "run_count": len(history.runs),
            "run_ids": [str(run.run_id) for run in history.runs]
        }

        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)

        # Save individual runs
        for run in history.runs:
            run_file = runs_dir / f"{run.run_id}.json"
            with open(run_file, 'w') as f:
                json.dump(run.model_dump(mode='json'), f, indent=2)

        logger.info(f"Saved history: {len(history.runs)} runs")

    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate migration was successful.

        Returns:
            Validation report with status and details
        """
        report = {
            "success": False,
            "backup_exists": False,
            "history_exists": False,
            "runs_found": 0,
            "errors": []
        }

        # Check backup
        if self.backup_dir.exists() and list(self.backup_dir.glob("*.json")):
            report["backup_exists"] = True
        else:
            report["errors"].append("No backup found")

        # Check history structure
        if self.history_dir.exists():
            report["history_exists"] = True

            index_file = self.history_dir / "index.json"
            if not index_file.exists():
                report["errors"].append("index.json missing")
            else:
                try:
                    with open(index_file, 'r') as f:
                        index_data = json.load(f)
                    report["runs_found"] = index_data.get("run_count", 0)
                except Exception as e:
                    report["errors"].append(f"Failed to read index: {e}")
        else:
            report["errors"].append("History directory missing")

        report["success"] = report["backup_exists"] and report["history_exists"] and len(report["errors"]) == 0

        return report


__all__ = ["MigrationManager"]
