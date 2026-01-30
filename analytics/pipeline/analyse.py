"""
Analysis pipeline stage.
Computes metrics and normalized scores on collected repository data.
"""
from analytics.pipeline.base import PipelineStep
from analytics.models.repo import RepoStats
from analytics.metrics.base import Metric
from analytics.metrics import (
    LOCMetric,
    EfficiencyMetric,
    BreadthMetric,
    ConsistencyMetric,
    ImpactMetric,
    ScaleMetric,
    PRReviewMetric,
    CodeReviewMetric,
)
from analytics.utils.language_filter import load_language_filters, filter_repos_list
from analytics.config.settings import LANGUAGE_FILTER_CONFIG, MAX_RUNS_PER_USER
from analytics.history import HistoryManager
from analytics.models.time_series import AnalysisRun
from analytics.normalisation.minmax import log_minmax
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime, timezone
import logging
import json

logger = logging.getLogger(__name__)


class Analyser(PipelineStep):
    """Analyzes repository data using configured metrics."""

    def __init__(self, metrics: List[Metric]) -> None:
        """
        Initialize analyzer with metrics.

        Args:
            metrics: List of metric objects to compute
        """
        super().__init__("Analyser")
        self.metrics: List[Metric] = metrics

    def execute(self, repos: List[RepoStats], **kwargs) -> Dict[str, Any]:
        """
        Execute analysis on repository data.

        Args:
            repos: List of repository statistics

        Returns:
            Dictionary mapping metric names to computed results
        """
        return {
            metric.name: metric.compute(repos)
            for metric in self.metrics
        }


def _resolve_user_dir(input_dir: Path) -> Path:
    """
    Resolve the user-specific data directory.

    Args:
        input_dir: Input directory provided by caller

    Returns:
        Path to user directory

    Raises:
        FileNotFoundError: If no suitable directory is found
    """
    input_dir = Path(input_dir)

    if (input_dir / "repositories.json").exists() or (input_dir / "repos_cache").is_dir():
        return input_dir

    if input_dir.exists() and input_dir.is_dir():
        candidates = []
        for child in input_dir.iterdir():
            if not child.is_dir():
                continue
            if (child / "repositories.json").exists() or (child / "repos_cache").is_dir():
                candidates.append(child)

        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            names = ", ".join(sorted(c.name for c in candidates))
            raise FileNotFoundError(
                "Multiple repository data directories found. "
                f"Specify one of: {names}"
            )

    raise FileNotFoundError(f"Repository data not found in: {input_dir}")


def _load_repos_data(input_dir: Path) -> List[Dict[str, Any]]:
    """
    Load repository data from either a single JSON file or a directory of per-repo JSON files.

    Args:
        input_dir: Directory containing repository data

    Returns:
        List of repository data dictionaries

    Raises:
        FileNotFoundError: If no repository data can be located
    """
    input_dir = Path(input_dir)

    # Legacy single-file format
    repos_file = input_dir / "repositories.json"
    if repos_file.exists():
        with open(repos_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]

    # New per-repo cache directory format
    repos_dir = input_dir / "repos_cache"
    if repos_dir.exists() and repos_dir.is_dir():
        repos = []
        for repo_file in sorted(repos_dir.glob("*.json")):
            try:
                with open(repo_file, 'r', encoding='utf-8') as f:
                    repos.append(json.load(f))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load {repo_file}: {e}")
        if repos:
            return repos

    raise FileNotFoundError(f"Repository data not found in: {input_dir}")


def run(input_dir: Path, output_dir: Path) -> None:
    """
    Run analysis pipeline step.

    Args:
        input_dir: Directory containing collected repository data
        output_dir: Directory to save analysis results
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve user directory
    user_dir = _resolve_user_dir(input_dir)
    username = user_dir.name

    # Load repository data (supports single file or per-repo cache directory)
    repos_data = _load_repos_data(user_dir)

    # Convert to RepoStats objects
    from analytics.models.repo import PRMetrics
    repos = []
    for repo in repos_data:
        # Parse PR metrics if present
        pr_metrics = None
        if 'pr_metrics' in repo and repo['pr_metrics']:
            pm = repo['pr_metrics']
            pr_metrics = PRMetrics(
                pr_count=pm.get('pr_count', 0),
                pr_merged_count=pm.get('pr_merged_count', 0),
                pr_closed_count=pm.get('pr_closed_count', 0),
                avg_pr_merge_time_hours=pm.get('avg_pr_merge_time_hours'),
                pr_review_count=pm.get('pr_review_count', 0),
                avg_reviews_per_pr=pm.get('avg_reviews_per_pr', 0.0),
                pr_comments_count=pm.get('pr_comments_count', 0),
                unique_reviewers=pm.get('unique_reviewers', 0)
            )

        repos.append(RepoStats(
            name=repo['name'],
            loc=repo['loc'],
            commits=repo['commits'],
            stars=repo['stars'],
            forks=repo['forks'],
            languages=repo.get('languages', {}),
            pr_metrics=pr_metrics
        ))

    # Apply language filtering if configured
    filter_config_path = LANGUAGE_FILTER_CONFIG
    original_repo_count = len(repos)
    if filter_config_path.exists():
        try:
            logger.info("Loading language filter configuration...")
            filter_config = load_language_filters(filter_config_path)

            if filter_config.get('filter_enabled', True):
                logger.info("Applying language filters to repositories...")
                repos = filter_repos_list(repos, filter_config)
                logger.info(f"Language filtering complete. {len(repos)} repositories retained.")
            else:
                logger.info("Language filtering disabled in configuration")
        except Exception as e:
            logger.warning(f"Failed to apply language filtering: {e}")
            logger.warning("Continuing analysis without filtering")
    else:
        logger.info(f"Language filter config not found at {filter_config_path}, skipping filtering")

    # Load and configure metrics
    metrics = [
        LOCMetric(),
        EfficiencyMetric(),
        BreadthMetric(),
        ConsistencyMetric(),
        ImpactMetric(),
        ScaleMetric(),
        PRReviewMetric(),
        CodeReviewMetric(),
    ]

    analyser = Analyser(metrics=metrics)
    results = analyser.run(repos=repos)

    # Convert MetricResult objects to dictionaries for JSON serialization
    serializable_results = {}
    for metric_name, metric_result in results.items():
        if hasattr(metric_result, 'to_dict'):
            serializable_results[metric_name] = metric_result.to_dict()
        else:
            serializable_results[metric_name] = metric_result

    # Save analysis results
    output_file = output_dir / "metrics.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2, default=str)

    logger.info(f"Saved analysis results to {output_file}")

    # Build analysis run for history tracking
    total_repos = len(repos)
    total_loc = sum(repo.loc for repo in repos)
    total_commits = sum(repo.commits for repo in repos)
    filtered_repos_count = original_repo_count - total_repos

    # Aggregate metric values (average of first dimension)
    aggregated_metrics: Dict[str, float] = {}
    for metric_name, metric_result in results.items():
        try:
            values_dict = metric_result.values
            if values_dict:
                first_key = next(iter(values_dict.keys()))
                values_list = values_dict.get(first_key, [])
                if values_list:
                    aggregated_metrics[metric_name] = sum(values_list) / len(values_list)
        except Exception as e:
            logger.warning(f"Failed to aggregate metric {metric_name}: {e}")

    # Normalize aggregated metrics
    try:
        normalized_metrics = log_minmax(aggregated_metrics) if aggregated_metrics else {}
    except Exception as e:
        logger.warning(f"Failed to normalize metrics: {e}")
        normalized_metrics = {}

    analysis_run = AnalysisRun(
        timestamp=datetime.now(timezone.utc),
        username=username,
        total_repos=total_repos,
        total_loc=total_loc,
        total_commits=total_commits,
        engineering_score=0.0,
        metrics=aggregated_metrics,
        normalized_metrics=normalized_metrics,
        repositories=[repo.model_dump() for repo in repos],
        config={
            "language_filter_enabled": filter_config_path.exists(),
            "filter_config_path": str(filter_config_path),
        },
        filtered_repos_count=filtered_repos_count
    )

    # Persist history
    history_manager = HistoryManager(user_dir, max_runs=MAX_RUNS_PER_USER)
    history = history_manager.load_or_create(username)
    history_manager.append_run(history, analysis_run)
    history_manager.save(history)

    logger.info(f"History updated for {username}: {len(history.runs)} run(s)")
