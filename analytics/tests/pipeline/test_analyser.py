import pytest
from unittest.mock import MagicMock
from analytics.pipeline.analyse import Analyser
from analytics.metrics.loc import LOCMetric
from analytics.models.repo import RepoStats


def test_analyser_init():
    """Test Analyser initialization."""
    metric1 = LOCMetric()
    metric2 = MagicMock()

    analyser = Analyser([metric1, metric2])
    assert analyser.metrics == [metric1, metric2]


def test_analyser_run_single_metric(sample_repo):
    """Test Analyser runs single metric."""
    metric = LOCMetric()
    analyser = Analyser([metric])

    result = analyser.run([sample_repo])

    assert "loc" in result
    assert result["loc"]["test-repo"] == 1500


def test_analyser_run_multiple_metrics(sample_repo):
    """Test Analyser runs multiple metrics."""
    metric1 = MagicMock()
    metric1.name = "metric1"
    metric1.compute.return_value = {"test-repo": 100}

    metric2 = MagicMock()
    metric2.name = "metric2"
    metric2.compute.return_value = {"test-repo": 200}

    analyser = Analyser([metric1, metric2])
    result = analyser.run([sample_repo])

    assert "metric1" in result
    assert "metric2" in result
    assert result["metric1"]["test-repo"] == 100
    assert result["metric2"]["test-repo"] == 200


def test_analyser_with_multiple_repos():
    """Test Analyser with multiple repositories."""
    repos = [
        RepoStats(name="repo1", loc=1000, commits=10, stars=5, languages={"Python": 100}),
        RepoStats(name="repo2", loc=2000, commits=20, stars=10, languages={"JS": 200}),
        RepoStats(name="repo3", loc=3000, commits=30, stars=15, languages={"Go": 300})
    ]

    metric = LOCMetric()
    analyser = Analyser([metric])

    result = analyser.run(repos)

    assert "loc" in result
    assert len(result["loc"]) == 3
    assert result["loc"]["repo1"] == 1000
    assert result["loc"]["repo2"] == 2000
    assert result["loc"]["repo3"] == 3000


def test_analyser_empty_metrics():
    """Test Analyser with no metrics."""
    analyser = Analyser([])
    result = analyser.run([])

    assert result == {}


def test_analyser_empty_repos():
    """Test Analyser with no repositories."""
    metric = MagicMock()
    metric.name = "metric"
    metric.compute.return_value = {}

    analyser = Analyser([metric])
    result = analyser.run([])

    assert result["metric"] == {}


def test_analyser_metric_error_propagates(sample_repo):
    """Test that metric compute errors propagate."""
    metric = MagicMock()
    metric.name = "failing_metric"
    metric.compute.side_effect = RuntimeError("Metric failed")

    analyser = Analyser([metric])

    with pytest.raises(RuntimeError):
        analyser.run([sample_repo])


def test_analyser_preserves_metric_order(sample_repo):
    """Test that Analyser preserves metric execution order."""
    call_order = []

    def make_metric(name):
        metric = MagicMock()
        metric.name = name
        metric.compute.side_effect = lambda repos: (call_order.append(name), {name: 1})[1]
        return metric

    metrics = [make_metric("first"), make_metric("second"), make_metric("third")]
    analyser = Analyser(metrics)
    result = analyser.run([sample_repo])

    assert call_order == ["first", "second", "third"]


def test_analyser_different_metric_results(sample_repo):
    """Test Analyser with metrics returning different data types."""
    metric1 = MagicMock()
    metric1.name = "integer_metric"
    metric1.compute.return_value = {"test-repo": 100}

    metric2 = MagicMock()
    metric2.name = "float_metric"
    metric2.compute.return_value = {"test-repo": 99.5}

    metric3 = MagicMock()
    metric3.name = "dict_metric"
    metric3.compute.return_value = {"test-repo": {"nested": "value"}}

    analyser = Analyser([metric1, metric2, metric3])
    result = analyser.run([sample_repo])

    assert isinstance(result["integer_metric"]["test-repo"], int)
    assert isinstance(result["float_metric"]["test-repo"], float)
    assert isinstance(result["dict_metric"]["test-repo"], dict)


def test_analyser_with_real_metric(sample_repo):
    """Test Analyser with real LOCMetric."""
    analyser = Analyser([LOCMetric()])
    result = analyser.run([sample_repo])

    assert "loc" in result
    assert result["loc"]["test-repo"] == sample_repo.loc
