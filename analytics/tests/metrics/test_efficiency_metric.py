import pytest
from analytics.metrics.efficiency import EfficiencyMetric
from analytics.exceptions import MetricError
from analytics.models.repo import RepoStats

def test_efficiency_calculation(sample_repo):
    metric = EfficiencyMetric()
    result = metric.compute([sample_repo])
    # Use new list-based structure
    assert "test-repo" in result
    assert result.get_value_by_repo("test-repo", "loc_per_commit") == 150.0


def test_efficiency_zero_commits():
    """Test that RepoStats validation rejects zero commits."""
    # RepoStats requires PositiveInt for commits, so zero should raise ValidationError
    with pytest.raises(Exception):  # ValidationError from pydantic
        repo = RepoStats(
            name="zero-commits-repo",
            loc=1000,
            commits=0,
            stars=5,
            forks=2,
            languages={"Python": 1000}
        )
        metric = EfficiencyMetric()
        with pytest.raises(MetricError):
            result = metric.compute([repo])
            assert "zero-commits-repo" not in result.values