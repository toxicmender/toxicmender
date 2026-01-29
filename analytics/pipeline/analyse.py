"""
Analysis pipeline stage.
Computes metrics and normalized scores on collected repository data.
"""
from analytics.pipeline.base import PipelineStep
from analytics.models.repo import RepoStats
from analytics.metrics import (
    LOCMetric,
    EfficiencyMetric,
    BreadthMetric,
    ConsistencyMetric,
    ImpactMetric,
    ScaleMetric,
)
from typing import List, Dict, Any
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


class Analyser(PipelineStep):
    """Analyzes repository data using configured metrics."""

    def __init__(self, metrics: List[Any]):
        """
        Initialize analyzer with metrics.

        Args:
            metrics: List of metric objects to compute
        """
        super().__init__("Analyser")
        self.metrics = metrics

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

    # If input_dir is a root data directory, try to resolve a single user subdirectory
    if input_dir.exists() and input_dir.is_dir():
        candidates = []
        for child in input_dir.iterdir():
            if not child.is_dir():
                continue
            if (child / "repositories.json").exists() or (child / "repos_cache").is_dir():
                candidates.append(child)

        if len(candidates) == 1:
            return _load_repos_data(candidates[0])
        if len(candidates) > 1:
            names = ", ".join(sorted(c.name for c in candidates))
            raise FileNotFoundError(
                "Multiple repository data directories found. "
                f"Specify one of: {names}"
            )

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

    # Load repository data (supports single file or per-repo cache directory)
    repos_data = _load_repos_data(input_dir)

    # Convert to RepoStats objects
    repos = [
        RepoStats(
            name=repo['name'],
            loc=repo['loc'],
            commits=repo['commits'],
            stars=repo['stars'],
            forks=repo['forks'],
            languages=repo.get('languages', {})
        )
        for repo in repos_data
    ]

    # Load and configure metrics
    metrics = [
        LOCMetric(),
        EfficiencyMetric(),
        BreadthMetric(),
        ConsistencyMetric(),
        ImpactMetric(),
        ScaleMetric(),
    ]

    analyser = Analyser(metrics=metrics)
    results = analyser.run(repos=repos)

    # Save analysis results
    output_file = output_dir / "metrics.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Saved analysis results to {output_file}")
