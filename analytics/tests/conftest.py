import pytest
from analytics.models.repo import RepoStats

@pytest.fixture
def sample_repo():
    return RepoStats(
        name="test-repo",
        loc=1500,
        commits=10,
        stars=5,
        forks=2
    )
