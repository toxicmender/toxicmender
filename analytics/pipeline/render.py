"""
Rendering pipeline stage.
Outputs analysis results in various formats (JSON, CSV, HTML).
"""
from analytics.pipeline.base import PipelineStep
from typing import Dict, Any, List
from pathlib import Path
import json
import csv
import logging

logger = logging.getLogger(__name__)


class ResultRenderer(PipelineStep):
    """Renders analysis results in multiple output formats."""

    SUPPORTED_FORMATS = {'.json', '.csv', '.txt'}

    def __init__(self, output_dir: Path):
        """
        Initialize result renderer.

        Args:
            output_dir: Directory to write rendered results
        """
        super().__init__("ResultRenderer")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, results: Dict[str, Any], format: str = 'json', **kwargs) -> Path:
        """
        Execute rendering of results.

        Args:
            results: Analysis results dictionary
            format: Output format (json, csv, txt)

        Returns:
            Path to rendered output file
        """
        return self.render(results, format)

    def render(self, results: Dict[str, Any], format: str = 'json') -> Path:
        """
        Render results to specified format.

        Args:
            results: Analysis results dictionary
            format: Output format (json, csv, txt)

        Returns:
            Path to rendered output file

        Raises:
            ValueError: If format is not supported
        """
        format_lower = format.lower()
        if not format_lower.startswith('.'):
            format_lower = f'.{format_lower}'

        if format_lower not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )

        if format_lower == '.json':
            return self._render_json(results)
        elif format_lower == '.csv':
            return self._render_csv(results)
        elif format_lower == '.txt':
            return self._render_text(results)

    def _render_json(self, results: Dict[str, Any]) -> Path:
        """Render results as JSON."""
        output_path = self.output_dir / 'results.json'
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Rendered JSON results to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to render JSON: {e}")
            raise

    def _render_csv(self, results: Dict[str, Any]) -> Path:
        """Render results as CSV."""
        output_path = self.output_dir / 'results.csv'
        try:
            # Flatten results for CSV format
            rows = self._flatten_results(results)

            if not rows:
                logger.warning("No data to render as CSV")
                return output_path

            # Get all keys from all rows for CSV headers
            fieldnames = set()
            for row in rows:
                fieldnames.update(row.keys())
            fieldnames = sorted(list(fieldnames))

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"Rendered CSV results to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to render CSV: {e}")
            raise

    def _render_text(self, results: Dict[str, Any]) -> Path:
        """Render results as formatted text."""
        output_path = self.output_dir / 'results.txt'
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("Analysis Results\n")
                f.write("=" * 80 + "\n\n")

                self._write_dict_to_file(f, results, indent=0)

            logger.info(f"Rendered text results to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to render text: {e}")
            raise

    def _flatten_results(self, obj: Any, prefix: str = '') -> List[Dict[str, Any]]:
        """Flatten nested results for CSV output."""
        rows = []

        if isinstance(obj, dict):
            # Check if this looks like a metric result with values
            if 'values' in obj and isinstance(obj['values'], dict):
                for key, value in obj['values'].items():
                    rows.append({
                        'metric': obj.get('name', prefix),
                        'key': key,
                        'value': value
                    })
            else:
                # Recurse into nested dicts/lists to flatten deeper structures
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        rows.extend(self._flatten_results(value, prefix=key))
                    else:
                        rows.append({key: value})
        elif isinstance(obj, list):
            for item in obj:
                rows.extend(self._flatten_results(item, prefix))

        return rows

    def _write_dict_to_file(self, f, obj: Any, indent: int = 0) -> None:
        """Recursively write dictionary to file with formatting."""
        indent_str = "  " * indent

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    f.write(f"{indent_str}{key}:\n")
                    self._write_dict_to_file(f, value, indent + 1)
                elif isinstance(value, list):
                    f.write(f"{indent_str}{key}:\n")
                    for item in value:
                        if isinstance(item, dict):
                            self._write_dict_to_file(f, item, indent + 1)
                        else:
                            f.write(f"{indent_str}  - {item}\n")
                else:
                    f.write(f"{indent_str}{key}: {value}\n")
        else:
            f.write(f"{indent_str}{obj}\n")


def run(template: Path, output: Path, data_dir: Path) -> None:
    """
    Run README rendering pipeline step.

    Args:
        template: Path to README template file
        output: Path to output README file
        data_dir: Directory containing metrics and data
    """
    from datetime import datetime
    import yaml
    import statistics

    template = Path(template)
    output = Path(output)
    data_dir = Path(data_dir)

    # Load metrics data
    metrics_file = data_dir / "metrics.json"
    if not metrics_file.exists():
        logger.warning(f"Metrics file not found: {metrics_file}")
        metrics = {}
    else:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics = json.load(f)

    # Load repository data
    repos = _load_repositories(data_dir)

    # Load weights configuration
    weights_file = Path("analytics/config/weights.yml")
    if weights_file.exists():
        with open(weights_file, 'r') as f:
            config = yaml.safe_load(f)
            weights = config.get('metric_weights', {})
    else:
        weights = {}

    # Load template if it exists
    if template.exists():
        with open(template, 'r', encoding='utf-8') as f:
            template_content = f.read()
    else:
        logger.warning(f"Template not found: {template}. Creating basic README.")
        template_content = "# Analytics Results\n\n{metrics}\n"

    # Build context dictionary with all placeholder values
    context = _build_context(metrics, repos, weights, data_dir)

    # Render template with context
    try:
        rendered_content = template_content.format(**context)
    except KeyError as e:
        logger.warning(f"Missing placeholder in template: {e}")
        rendered_content = template_content

    # Write output
    with open(output, 'w', encoding='utf-8') as f:
        f.write(rendered_content)

    logger.info(f"Rendered README to {output}")


def _load_repositories(data_dir: Path) -> List[Dict]:
    """Load repository data from data directory."""
    repos_file = data_dir / "toxicmender" / "repositories.json"
    if repos_file.exists():
        with open(repos_file, 'r') as f:
            return json.load(f)

    # Try alternative location
    repos_file = data_dir / "repositories.json"
    if repos_file.exists():
        with open(repos_file, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]

    logger.warning(f"Repository data not found in {data_dir}")
    return []


def _build_context(metrics: Dict, repos: List[Dict], weights: Dict, data_dir: Path) -> Dict:
    """Build context dictionary with all template placeholders."""
    from datetime import datetime
    import statistics

    context = {}

    # Basic info
    context['analysis_date'] = datetime.now().strftime('%Y-%m-%d')
    context['total_repos'] = len(repos)
    context['username'] = 'toxicmender'
    context['version'] = '1.0.0'

    # Extract metric values
    metric_data = _extract_metric_values(metrics, repos)

    # Weights (as percentages)
    context['breadth_weight'] = int(weights.get('breadth', 0.1) * 100)
    context['consistency_weight'] = int(weights.get('consistency', 0.2) * 100)
    context['efficiency_weight'] = int(weights.get('efficiency', 0.15) * 100)
    context['impact_weight'] = int(weights.get('impact', 0.15) * 100)
    context['scale_weight'] = int(weights.get('scale', 0.1) * 100)

    # Compute engineering score
    score_data = _compute_engineering_score(metric_data, weights)
    context.update(score_data)

    # Statistical summaries
    context.update(_compute_statistics(repos, metric_data))

    # Chart paths
    context['category_chart_path'] = 'charts/category_metrics.png'
    context['language_chart_path'] = 'charts/language_distribution.png'
    context['efficiency_chart_path'] = 'charts/efficiency_analysis.png'
    context['repo_stars_chart_path'] = 'charts/repo_vs_stars.png'
    context['heatmap_chart_path'] = 'charts/activity_heatmap.png'

    # Top repositories tables
    context['top_repos_by_stars'] = _generate_top_repos_table(repos, 'stars', 5)
    context['top_repos_by_size'] = _generate_top_repos_table(repos, 'loc', 5)
    context['top_repos_by_activity'] = _generate_top_repos_table(repos, 'commits', 5)

    # Language breakdown
    context['language_breakdown_table'] = _generate_language_table(repos)

    # Achievements
    context['achievements_section'] = _generate_achievements(repos, metric_data)

    # Fill in any missing placeholders with default values
    _fill_defaults(context)

    return context


def _extract_metric_values(metrics: Dict, repos: List[Dict]) -> Dict:
    """Extract and normalize metric values."""
    result = {}

    for metric_name, metric_obj in metrics.items():
        if isinstance(metric_obj, dict) and 'values' in metric_obj:
            values = metric_obj['values']
            if isinstance(values, dict):
                # Get first dimension's values
                first_key = next(iter(values.keys()))
                result[metric_name] = values[first_key]
            else:
                result[metric_name] = values

    return result


def _compute_engineering_score(metric_data: Dict, weights: Dict) -> Dict:
    """Compute overall engineering score and component breakdowns."""
    from analytics.normalisation.minmax import log_minmax

    context = {}

    # Normalize each metric
    normalised = {}

    for metric_name, values in metric_data.items():
        if isinstance(values, list) and len(values) > 0:
            # Convert list to dict for normalization function
            value_dict = {f'repo_{i}': v for i, v in enumerate(values)}
            try:
                norm_dict = log_minmax(value_dict)
                normalised[metric_name] = list(norm_dict.values())
            except Exception as e:
                logger.warning(f"Failed to normalize {metric_name}: {e}")
                normalised[metric_name] = [0.0] * len(values)

    # Compute weighted score
    total_score = 0.0
    components = {}

    for metric_name in ['breadth', 'consistency', 'efficiency', 'impact', 'scale']:
        if metric_name in normalised and metric_name in weights:
            norm_values = normalised[metric_name]
            avg_norm = sum(norm_values) / len(norm_values) if norm_values else 0
            weight = weights[metric_name]
            contribution = avg_norm * weight * 100

            components[f'{metric_name}_normalized'] = f'{avg_norm:.2f}'
            components[f'{metric_name}_contribution'] = f'{contribution:.2f}'

            total_score += contribution

    context['engineering_score'] = f'{total_score:.1f}'

    # Add raw values
    for metric_name in ['breadth', 'consistency', 'efficiency', 'impact', 'scale']:
        if metric_name in metric_data:
            values = metric_data[metric_name]
            if isinstance(values, list) and len(values) > 0:
                avg_val = sum(values) / len(values)
                context[f'{metric_name}_raw'] = f'{avg_val:.2f}'
            else:
                context[f'{metric_name}_raw'] = '0.00'

    context.update(components)

    return context


def _compute_statistics(repos: List[Dict], metric_data: Dict) -> Dict:
    """Compute statistical summaries."""
    import statistics

    context = {}

    if not repos:
        return context

    # Repository statistics
    total_loc = sum(r.get('loc', 0) for r in repos)
    total_commits = sum(r.get('commits', 0) for r in repos)
    total_stars = sum(r.get('stars', 0) for r in repos)
    total_forks = sum(r.get('forks', 0) for r in repos)

    context['total_loc'] = total_loc
    context['total_commits'] = total_commits
    context['total_stars'] = total_stars
    context['total_forks'] = total_forks

    # Averages
    n = len(repos)
    context['avg_repo_size'] = total_loc / n if n > 0 else 0
    context['avg_commits_per_repo'] = total_commits / n if n > 0 else 0
    context['avg_stars_per_repo'] = total_stars / n if n > 0 else 0
    context['avg_forks_per_repo'] = total_forks / n if n > 0 else 0

    # Median and std dev
    loc_values = [r.get('loc', 0) for r in repos]
    if loc_values:
        context['median_repo_size'] = statistics.median(loc_values)
        context['std_loc'] = statistics.stdev(loc_values) if len(loc_values) > 1 else 0
        context['min_repo_size'] = min(loc_values)
        context['max_repo_size'] = max(loc_values)

    # Language diversity
    all_languages = set()
    for repo in repos:
        all_languages.update(repo.get('languages', {}).keys())

    context['total_languages'] = len(all_languages)
    context['primary_languages'] = ', '.join(sorted(list(all_languages))[:5])

    # Compute language entropy (diversity measure)
    lang_totals = {}
    for repo in repos:
        for lang, loc in repo.get('languages', {}).items():
            lang_totals[lang] = lang_totals.get(lang, 0) + loc

    if lang_totals:
        most_used = max(lang_totals.items(), key=lambda x: x[1])
        context['most_used_language'] = most_used[0]
        context['most_used_language_percentage'] = f'{(most_used[1] / total_loc * 100):.1f}' if total_loc > 0 else '0.0'

    # Additional computed metrics
    context['active_repo_ratio'] = f'{(sum(1 for r in repos if r.get("commits", 0) > 10) / n * 100):.1f}' if n > 0 else '0.0'
    context['avg_loc_per_commit'] = f'{(total_loc / total_commits):.1f}' if total_commits > 0 else '0.0'
    context['engagement_rate'] = f'{((total_stars + total_forks) / n):.1f}' if n > 0 else '0.0'

    # Find largest repo
    if repos:
        largest = max(repos, key=lambda r: r.get('loc', 0))
        context['largest_repo'] = largest['name']
        context['largest_repo_loc'] = largest.get('loc', 0)

    return context


def _generate_top_repos_table(repos: List[Dict], sort_key: str, limit: int = 5) -> str:
    """Generate markdown table for top repositories."""
    if not repos:
        return "| No data available | | | | |\n"

    sorted_repos = sorted(repos, key=lambda r: r.get(sort_key, 0), reverse=True)[:limit]

    rows = []
    for repo in sorted_repos:
        if sort_key == 'stars':
            row = f"| {repo['name']} | {repo.get('stars', 0)} | {repo.get('forks', 0)} | {list(repo.get('languages', {}).keys())[0] if repo.get('languages') else 'N/A'} | {repo.get('loc', 0):,} |"
        elif sort_key == 'loc':
            row = f"| {repo['name']} | {repo.get('loc', 0):,} | {repo.get('commits', 0)} | {len(repo.get('languages', {}))} | {repo.get('stars', 0)} |"
        else:  # commits (activity)
            langs = ', '.join(list(repo.get('languages', {}).keys())[:3])
            row = f"| {repo['name']} | {repo.get('commits', 0)} | N/A | {langs} | {repo.get('stars', 0) + repo.get('forks', 0)} |"
        rows.append(row)

    return '\n'.join(rows)


def _generate_language_table(repos: List[Dict]) -> str:
    """Generate language breakdown table."""
    if not repos:
        return "| No data available | | | | |\n"

    # Aggregate language statistics
    lang_stats = {}
    total_loc = sum(r.get('loc', 0) for r in repos)

    for repo in repos:
        for lang, loc in repo.get('languages', {}).items():
            if lang not in lang_stats:
                lang_stats[lang] = {'repos': set(), 'total_loc': 0}
            lang_stats[lang]['repos'].add(repo['name'])
            lang_stats[lang]['total_loc'] += loc

    # Sort by total LOC
    sorted_langs = sorted(lang_stats.items(), key=lambda x: x[1]['total_loc'], reverse=True)[:10]

    rows = []
    for lang, stats in sorted_langs:
        repo_count = len(stats['repos'])
        lang_loc = stats['total_loc']
        percentage = (lang_loc / total_loc * 100) if total_loc > 0 else 0
        avg_loc = lang_loc / repo_count if repo_count > 0 else 0

        row = f"| {lang} | {repo_count} | {lang_loc:,} | {percentage:.1f}% | {avg_loc:,.0f} |"
        rows.append(row)

    return '\n'.join(rows)


def _generate_achievements(repos: List[Dict], metric_data: Dict) -> str:
    """Generate achievements section based on repository data."""
    if not repos:
        return "- No repositories analyzed yet"

    achievements = []

    total_repos = len(repos)
    total_loc = sum(r.get('loc', 0) for r in repos)
    total_commits = sum(r.get('commits', 0) for r in repos)

    # Achievement: Large codebase
    if total_loc > 1000000:
        achievements.append(f"- 🏆 **Million+ Lines**: Written over {total_loc:,} lines of code across all repositories")

    # Achievement: Prolific contributor
    if total_commits > 1000:
        achievements.append(f"- 🏆 **Prolific Contributor**: Made {total_commits:,}+ commits across projects")

    # Achievement: Polyglot programmer
    all_languages = set()
    for repo in repos:
        all_languages.update(repo.get('languages', {}).keys())
    if len(all_languages) >= 10:
        achievements.append(f"- 🏆 **Polyglot Programmer**: Proficient in {len(all_languages)} programming languages")

    # Achievement: Popular repositories
    popular_repos = [r for r in repos if r.get('stars', 0) > 0]
    if popular_repos:
        achievements.append(f"- ⭐ **Community Impact**: {len(popular_repos)} repositories with GitHub stars")

    # Achievement: Diverse portfolio
    if total_repos >= 20:
        achievements.append(f"- 📚 **Diverse Portfolio**: Contributed to {total_repos}+ repositories")

    return '\n'.join(achievements) if achievements else "- Building an impressive development portfolio"


def _fill_defaults(context: Dict) -> None:
    """Fill in missing placeholders with default values."""
    defaults = {
        'language_entropy': '0.0',
        'commit_frequency': 'N/A',
        'code_churn_rate': 'N/A',
        'refactoring_index': 'N/A',
        'code_volume_index': 'N/A',
        'language_diversity_index': 'N/A',
        'cross_platform_score': 'N/A',
    }

    for key, value in defaults.items():
        if key not in context:
            context[key] = value
