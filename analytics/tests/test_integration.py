"""
Integration tests for the analytics pipeline.
Tests full workflow: collect -> analyse -> visualize -> render
"""
import pytest
from unittest.mock import MagicMock
from analytics.models.repo import RepoStats
from analytics.pipeline.analyse import Analyser
from analytics.pipeline.visualize import Visualizer
from analytics.metrics.loc import LOCMetric
from analytics.normalisation.minmax import log_minmax, z_score, rank_based
from analytics.scoring.impact_score import ImpactScore
from analytics.scoring.engineering_score import EngineeringScore


@pytest.fixture
def sample_repos():
    """Create sample repositories for integration tests."""
    return [
        RepoStats(
            name="project_a",
            loc=5000,
            commits=50,
            stars=100,
            languages={"Python": 4500, "JavaScript": 500}
        ),
        RepoStats(
            name="project_b",
            loc=10000,
            commits=100,
            stars=250,
            languages={"Go": 8000, "Python": 2000}
        ),
        RepoStats(
            name="project_c",
            loc=2000,
            commits=30,
            stars=50,
            languages={"Rust": 2000}
        ),
    ]


def test_pipeline_end_to_end_analysis(sample_repos):
    """Test full analysis pipeline."""
    # Step 1: Analyze
    metric = LOCMetric()
    analyser = Analyser([metric])
    metrics_result = analyser.run(sample_repos)

    assert "loc" in metrics_result
    assert len(metrics_result["loc"]) == 3
    assert metrics_result["loc"]["project_a"] == 5000
    assert metrics_result["loc"]["project_b"] == 10000
    assert metrics_result["loc"]["project_c"] == 2000


def test_pipeline_normalisation_workflow(sample_repos):
    """Test normalisation as part of pipeline."""
    metric = LOCMetric()
    analyser = Analyser([metric])
    metrics_result = analyser.run(sample_repos)

    # Normalize using different methods
    raw_metrics = metrics_result["loc"]

    # Test each normalisation method
    log_normalized = log_minmax(raw_metrics)
    z_normalized = z_score(raw_metrics)
    rank_normalized = rank_based(raw_metrics)

    # All should be in [0, 1] range
    for method, normalized in [
        ("log", log_normalized),
        ("z_score", z_normalized),
        ("rank", rank_normalized)
    ]:
        assert len(normalized) == 3
        for value in normalized.values():
            assert 0 <= value <= 1, f"{method} normalization out of range: {value}"


def test_pipeline_scoring_workflow(sample_repos):
    """Test scoring as part of pipeline."""
    metric = LOCMetric()
    analyser = Analyser([metric])
    metrics_result = analyser.run(sample_repos)

    # Normalize
    raw_metrics = metrics_result["loc"]
    normalized = log_minmax(raw_metrics)

    # Score using impact scoring
    weights = {"loc": 1.0}
    impact_scorer = ImpactScore(weights)
    scores = impact_scorer.score({"loc": normalized})

    assert len(scores) == 3
    assert all(0 <= score <= 1 for score in scores.values())


def test_pipeline_end_to_end_with_multiple_metrics(sample_repos):
    """Test pipeline with multiple metrics."""
    metric1 = LOCMetric()

    metric2 = MagicMock()
    metric2.name = "commits_per_loc"
    metric2.compute.return_value = {
        "project_a": 50 / 5000,
        "project_b": 100 / 10000,
        "project_c": 30 / 2000
    }

    analyser = Analyser([metric1, metric2])
    result = analyser.run(sample_repos)

    assert "loc" in result
    assert "commits_per_loc" in result
    assert len(result["loc"]) == 3
    assert len(result["commits_per_loc"]) == 3


def test_pipeline_normalisation_consistency():
    """Test that normalisation methods are consistent."""
    data = {"repo_a": 100, "repo_b": 200, "repo_c": 300}

    log_norm = log_minmax(data)
    z_norm = z_score(data)
    rank_norm = rank_based(data)

    # All methods should preserve order
    repos_by_log = sorted(log_norm.items(), key=lambda x: x[1])
    repos_by_z = sorted(z_norm.items(), key=lambda x: x[1])
    repos_by_rank = sorted(rank_norm.items(), key=lambda x: x[1])

    log_order = [r[0] for r in repos_by_log]
    z_order = [r[0] for r in repos_by_z]
    rank_order = [r[0] for r in repos_by_rank]

    # Original order should be preserved in all methods
    assert log_order == rank_order
    assert z_order == rank_order


def test_pipeline_scoring_aggregation():
    """Test aggregating multiple normalized metrics for scoring."""
    data = {
        "metric1": {"repo_a": 0.9, "repo_b": 0.6, "repo_c": 0.3},
        "metric2": {"repo_a": 0.8, "repo_b": 0.7, "repo_c": 0.5},
        "metric3": {"repo_a": 0.7, "repo_b": 0.8, "repo_c": 0.9}
    }

    weights = {"metric1": 0.4, "metric2": 0.3, "metric3": 0.3}
    scorer = ImpactScore(weights)
    scores = scorer.score(data)

    assert len(scores) == 3
    assert 0 <= scores["repo_a"] <= 1
    assert 0 <= scores["repo_b"] <= 1
    assert 0 <= scores["repo_c"] <= 1


def test_pipeline_engineering_score_components():
    """Test engineering score with multiple components."""
    components = {
        "quality": 0.85,
        "performance": 0.72,
        "maintainability": 0.90,
        "security": 0.78,
        "weights": {
            "quality": 0.3,
            "performance": 0.2,
            "maintainability": 0.3,
            "security": 0.2
        }
    }

    scorer = EngineeringScore()
    score = scorer.score(components)

    assert 0 <= score <= 100
    # (0.85*0.3 + 0.72*0.2 + 0.90*0.3 + 0.78*0.2) * 100
    # = (0.255 + 0.144 + 0.27 + 0.156) * 100 = 82.5
    assert score == pytest.approx(82.5, abs=1.0)


def test_pipeline_visualization_integration(sample_repos, tmp_path):
    """Test visualization as part of pipeline."""
    from analytics.charts.language import LanguageChart

    # Create a chart with aggregated data
    language_data = {}
    for repo in sample_repos:
        for lang, count in repo.languages.items():
            language_data[lang] = language_data.get(lang, 0) + count

    chart = LanguageChart(language_data)
    visualizer = Visualizer([(chart, tmp_path / "languages.svg")])
    visualizer.run()

    assert (tmp_path / "languages.svg").exists()


def test_pipeline_full_workflow_simulation(sample_repos, tmp_path):
    """Simulate complete pipeline workflow."""
    # 1. Collect (mock)
    repos = sample_repos

    # 2. Analyze
    metric = LOCMetric()
    analyser = Analyser([metric])
    raw_metrics = analyser.run(repos)

    # 3. Normalize
    normalized = {
        "loc": log_minmax(raw_metrics["loc"])
    }

    # 4. Score
    weights = {"loc": 1.0}
    scorer = ImpactScore(weights)
    final_scores = scorer.score(normalized)

    # 5. Visualize (mock)
    from analytics.charts.language import LanguageChart
    chart = LanguageChart({"Python": 100, "Go": 50})
    visualizer = Visualizer([(chart, tmp_path / "languages.svg")])
    visualizer.run()

    # Verify results
    assert len(final_scores) == 3
    assert all(0 <= score <= 1 for score in final_scores.values())
    assert (tmp_path / "languages.svg").exists()


def test_language_filtering_integration(tmp_path):
    """Test that language filtering is applied during analysis."""
    from analytics.utils.language_filter import filter_repos_list

    # Create repos with various languages including ones to be filtered
    repos = [
        RepoStats(
            name="web-project",
            loc=2000,
            commits=50,
            stars=10,
            languages={"Python": 1000, "HTML": 500, "CSS": 300, "JavaScript": 200}
        ),
        RepoStats(
            name="notebook-project",
            loc=1500,
            commits=20,
            stars=5,
            languages={"Jupyter Notebook": 1000, "Python": 500}
        ),
        RepoStats(
            name="docs-only",
            loc=500,
            commits=10,
            stars=0,
            languages={"HTML": 300, "CSS": 200}
        ),
        RepoStats(
            name="code-project",
            loc=3000,
            commits=100,
            stars=50,
            languages={"Python": 2000, "Go": 1000}
        )
    ]

    # Apply filtering
    config = {
        'filter_enabled': True,
        'excluded_languages': ['HTML', 'CSS', 'Jupyter Notebook'],
        'minimum_language_loc': 0,
        'remove_empty_repos': True,
        'case_sensitive': False
    }

    filtered_repos = filter_repos_list(repos, config)

    # Verify filtering results
    assert len(filtered_repos) == 3  # docs-only should be removed

    # Check web-project was filtered correctly
    web_proj = next(r for r in filtered_repos if r.name == "web-project")
    assert 'Python' in web_proj.languages
    assert 'JavaScript' in web_proj.languages
    assert 'HTML' not in web_proj.languages
    assert 'CSS' not in web_proj.languages
    assert web_proj.loc == 1200  # 1000 + 200
    assert web_proj.original_loc == 2000

    # Check notebook-project was filtered
    notebook_proj = next(r for r in filtered_repos if r.name == "notebook-project")
    assert 'Python' in notebook_proj.languages
    assert 'Jupyter Notebook' not in notebook_proj.languages
    assert notebook_proj.loc == 500

    # Check code-project was unchanged
    code_proj = next(r for r in filtered_repos if r.name == "code-project")
    assert len(code_proj.languages) == 2
    assert code_proj.loc == 3000

    # Verify docs-only was removed
    assert not any(r.name == "docs-only" for r in filtered_repos)

