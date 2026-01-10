import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
from analytics.models.repo import RepoStats

@pytest.fixture
def sample_repo():
    return RepoStats(
        name="test-repo",
        loc=1500,
        commits=10,
        stars=5,
        forks=2,
        languages={"Python": 1000, "JavaScript": 500}
    )
