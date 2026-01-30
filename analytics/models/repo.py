from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt, field_validator
from typing import Dict, Optional, List

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
    "RepoStats",
    "RepoAnalysisResult",
    "AggregateRepoMetrics",
    "LanguageDistribution",
    "RepoAnalysisSummary"
]