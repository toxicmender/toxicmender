"""
Visualization pipeline stage.
Generates charts and visual representations of analysis results.
"""
from analytics.pipeline.base import PipelineStep
from analytics.charts.category import CategoryChart
from analytics.charts.efficiency import EfficiencyChart
from analytics.charts.heatmap import HeatmapChart
from analytics.charts.language import LanguageChart
from analytics.charts.repo_vs_stars import RepoVsStarsChart
from typing import List, Tuple, Any, Dict
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


class Visualizer(PipelineStep):
    """Generates visualizations from analysis results."""

    def __init__(self, charts: List[Tuple[Any, str]]):
        """
        Initialize visualizer with chart configurations.

        Args:
            charts: List of tuples (chart_object, output_path)
        """
        super().__init__("Visualizer")
        self.charts = charts

    def execute(self, **kwargs) -> None:
        """
        Execute visualization generation.

        Renders each configured chart to its output path.
        """
        for chart, path in self.charts:
            self.logger.info(f"Rendering chart to {path}")
            chart.render(path)


def _load_metrics(data_dir: Path) -> Dict:
    """Load metrics from JSON file."""
    metrics_file = data_dir / "metrics.json"
    if not metrics_file.exists():
        raise FileNotFoundError(f"Metrics data not found: {metrics_file}")

    with open(metrics_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_repositories(data_dir: Path, username: str = None) -> List[Dict]:
    """Load repository data from JSON file."""
    # Try to find repositories.json
    if username:
        repo_file = data_dir / username / "repositories.json"
    else:
        # Try to find any repositories.json in subdirectories
        repo_files = list(data_dir.glob("*/repositories.json"))
        if not repo_files:
            raise FileNotFoundError(f"No repositories.json found in {data_dir}")
        repo_file = repo_files[0]

    if not repo_file.exists():
        raise FileNotFoundError(f"Repository data not found: {repo_file}")

    with open(repo_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def _create_efficiency_chart(metrics: Dict, repos: List[Dict]) -> EfficiencyChart:
    """Create efficiency chart from metrics data."""
    efficiency_data = metrics.get("efficiency", {})
    repo_names = efficiency_data.get("repo_names", [])
    values = efficiency_data.get("values", {})

    # Get LOC per commit values
    loc_per_commit = values.get("loc_per_commit", [])

    # Create dictionary mapping repo names to efficiency values
    data = {repo_names[i]: loc_per_commit[i]
            for i in range(min(len(repo_names), len(loc_per_commit)))}

    # Limit to top 20 repositories for readability
    if len(data) > 20:
        data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:20])

    return EfficiencyChart(data)


def _create_language_chart(repos: List[Dict]) -> LanguageChart:
    """Create language distribution pie chart."""
    language_totals = {}

    for repo in repos:
        languages = repo.get("languages", {})
        for lang, loc in languages.items():
            language_totals[lang] = language_totals.get(lang, 0) + loc

    # Keep top 10 languages, group rest as "Other"
    sorted_langs = sorted(language_totals.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_langs) > 10:
        top_langs = dict(sorted_langs[:10])
        other_total = sum(loc for _, loc in sorted_langs[10:])
        if other_total > 0:
            top_langs["Other"] = other_total
        language_totals = top_langs

    return LanguageChart(language_totals)


def _create_repo_vs_stars_chart(metrics: Dict, repos: List[Dict]) -> RepoVsStarsChart:
    """Create scatter plot of repository size vs stars."""
    loc_data = metrics.get("loc", {})
    repo_names = loc_data.get("repo_names", [])
    values = loc_data.get("values", {})
    total_loc = values.get("total_loc", [])

    # Create repo name to LOC mapping
    loc_map = {repo_names[i]: total_loc[i]
               for i in range(min(len(repo_names), len(total_loc)))}

    # Create data with (LOC, stars) tuples
    data = {}
    for repo in repos:
        name = repo.get("name")
        stars = repo.get("stars", 0)
        if name in loc_map:
            data[name] = (loc_map[name], stars)

    # Limit to top 30 repositories for readability
    if len(data) > 30:
        data = dict(sorted(data.items(), key=lambda x: x[1][1], reverse=True)[:30])

    return RepoVsStarsChart(data, x_label="Lines of Code")


def _create_heatmap_chart(metrics: Dict) -> HeatmapChart:
    """Create correlation heatmap for metrics."""
    # Extract metric values for correlation analysis
    metric_data = {}
    metric_names = []

    for metric_name in ["breadth", "consistency", "efficiency", "impact", "scale"]:
        if metric_name in metrics:
            metric_obj = metrics[metric_name]
            values = metric_obj.get("values", {})

            # Get first dimension values for each metric
            if values:
                first_key = list(values.keys())[0]
                first_values = values[first_key]
                if first_values:
                    metric_data[metric_name] = first_values
                    metric_names.append(metric_name)

    return HeatmapChart(metric_data, metric_names)


def _create_category_chart(repos: List[Dict]) -> CategoryChart:
    """Create category-based bar chart."""
    # Group repositories by primary language
    categories = {}

    for repo in repos:
        languages = repo.get("languages", {})
        if languages:
            # Get primary language (highest LOC)
            primary_lang = max(languages.items(), key=lambda x: x[1])[0]
            if primary_lang not in categories:
                categories[primary_lang] = []

            # Add total LOC for this repo
            total_loc = sum(languages.values())
            categories[primary_lang].append(total_loc)

    # Calculate average LOC per category
    category_data = {
        lang: [sum(locs) / len(locs)]
        for lang, locs in categories.items()
    }

    # Keep top 10 categories
    if len(category_data) > 10:
        sorted_cats = sorted(category_data.items(), key=lambda x: x[1][0], reverse=True)
        category_data = dict(sorted_cats[:10])

    category_names = list(category_data.keys())

    return CategoryChart(category_data, category_names)


def run(data_dir: Path, charts_dir: Path) -> None:
    """
    Run visualization pipeline step.

    Args:
        data_dir: Directory containing metrics and analysis results
        charts_dir: Directory to save generated charts
    """
    data_dir = Path(data_dir)
    charts_dir = Path(charts_dir)
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    metrics = _load_metrics(data_dir)
    repos = _load_repositories(data_dir)

    # Create charts list
    charts = []

    try:
        # 1. Efficiency Analysis Chart
        efficiency_chart = _create_efficiency_chart(metrics, repos)
        charts.append((efficiency_chart, charts_dir / "efficiency_analysis.png"))
        logger.info("Created efficiency chart")
    except Exception as e:
        logger.warning(f"Failed to create efficiency chart: {e}")

    try:
        # 2. Language Distribution Chart
        language_chart = _create_language_chart(repos)
        charts.append((language_chart, charts_dir / "language_distribution.png"))
        logger.info("Created language chart")
    except Exception as e:
        logger.warning(f"Failed to create language chart: {e}")

    try:
        # 3. Repository vs Stars Chart
        repo_stars_chart = _create_repo_vs_stars_chart(metrics, repos)
        charts.append((repo_stars_chart, charts_dir / "repo_vs_stars.png"))
        logger.info("Created repo vs stars chart")
    except Exception as e:
        logger.warning(f"Failed to create repo vs stars chart: {e}")

    try:
        # 4. Metric Correlation Heatmap
        heatmap_chart = _create_heatmap_chart(metrics)
        charts.append((heatmap_chart, charts_dir / "activity_heatmap.png"))
        logger.info("Created heatmap chart")
    except Exception as e:
        logger.warning(f"Failed to create heatmap chart: {e}")

    try:
        # 5. Category Chart
        category_chart = _create_category_chart(repos)
        charts.append((category_chart, charts_dir / "category_distribution.png"))
        logger.info("Created category chart")
    except Exception as e:
        logger.warning(f"Failed to create category chart: {e}")

    # Render all charts
    visualizer = Visualizer(charts=charts)
    visualizer.run()

    logger.info(f"Generated {len(charts)} charts in {charts_dir}")