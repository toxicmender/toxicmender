from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt, field_validator
from typing import Dict, Optional, List


class PRMetrics(BaseModel):
    """Pull request and code review metrics."""
    model_config = {'frozen': True}

    pr_count: NonNegativeInt = 0  # Total PRs
    pr_merged_count: NonNegativeInt = 0  # Merged PRs
    pr_closed_count: NonNegativeInt = 0  # Closed without merge
    avg_pr_merge_time_hours: Optional[float] = None  # Average hours to merge
    pr_review_count: NonNegativeInt = 0  # Total reviews
    avg_reviews_per_pr: float = 0.0  # Average reviews per PR
    pr_comments_count: NonNegativeInt = 0  # Total PR comments
    unique_reviewers: NonNegativeInt = 0  # Number of unique reviewers


class RepoStats(BaseModel):
    model_config = {'frozen': True}  # Pydantic v2 ConfigDict

    name: str = Field(min_length=1)
    loc: PositiveInt
    commits: PositiveInt
    stars: NonNegativeInt = 0
    forks: NonNegativeInt = 0
    languages: Dict[str, PositiveInt]
    # Optional tracking fields for language filtering
    original_loc: Optional[PositiveInt] = None  # LOC before filtering
    filtered_languages: Optional[List[str]] = None  # Languages that were filtered out
    # PR and code review metrics
    pr_metrics: Optional[PRMetrics] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate repository name."""
        v = v.strip()
        if not v:
            raise ValueError("Repository name cannot be empty")
        return v

class RepoAnalysisResult(BaseModel):
    model_config = {'frozen': True}

    repo: RepoStats
    toxicity_score: float = Field(..., ge=0.0, le=1.0)
    maintenance_score: float = Field(..., ge=0.0, le=1.0)

class AggregateRepoMetrics(BaseModel):
    model_config = {'frozen': True}

    total_repos: NonNegativeInt
    average_loc: float = Field(ge=0.0)
    average_commits: float = Field(ge=0.0)
    average_stars: float = Field(ge=0.0)
    average_forks: float = Field(ge=0.0)

class LanguageDistribution(BaseModel):
    model_config = {'frozen': True}

    languages: Dict[str, PositiveInt]

class RepoAnalysisSummary(BaseModel):
    model_config = {'frozen': True}

    aggregate_metrics: AggregateRepoMetrics
    language_distribution: LanguageDistribution

__all__ = [
    "PRMetrics",
    "RepoStats",
    "RepoAnalysisResult",
    "AggregateRepoMetrics",
    "LanguageDistribution",
    "RepoAnalysisSummary"
]