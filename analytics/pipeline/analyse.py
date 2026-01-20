"""
Analysis pipeline stage.
Computes metrics and normalized scores on collected repository data.
"""
from analytics.pipeline.base import PipelineStep
from analytics.models.repo import RepoStats
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

    # Load repository data
    repos_file = input_dir / "repositories.json"
    if not repos_file.exists():
        raise FileNotFoundError(f"Repository data not found: {repos_file}")

    with open(repos_file, 'r', encoding='utf-8') as f:
        repos_data = json.load(f)

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

    # TODO: Load and configure metrics
    # For now, create analyzer with empty metrics list
    # This should be populated with actual metric instances
    metrics = []

    analyser = Analyser(metrics=metrics)
    results = analyser.run(repos=repos)

    # Save analysis results
    output_file = output_dir / "metrics.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Saved analysis results to {output_file}")
