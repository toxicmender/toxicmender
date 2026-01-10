import pytest
from analytics.metrics.efficiency import EfficiencyMetric
from analytics.exceptions import MetricError

def test_efficiency_calculation(sample_repo):
    metric = EfficiencyMetric()
    result = metric.compute([sample_repo])
    assert result["test-repo"] == 150.0


def test_efficiency_zero_commits(sample_repo):
    sample_repo.commits = 0
    metric = EfficiencyMetric()
    with pytest.raises(MetricError):
        metric.compute([sample_repo])
