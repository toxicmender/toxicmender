from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt
from typing import Dict

class RepoStats(BaseModel):
    name: str
    loc: PositiveInt
    commits: PositiveInt
    stars: NonNegativeInt = 0
    forks: NonNegativeInt = 0
    languages: Dict[str, PositiveInt]

    class Config:
        frozen = True

class RepoAnalysisResult(BaseModel):
    repo: RepoStats
    toxicity_score: float = Field(..., ge=0.0, le=1.0)
    maintenance_score: float = Field(..., ge=0.0, le=1.0)

    class Config:
        frozen = True

class AggregateRepoMetrics(BaseModel):
    total_repos: NonNegativeInt
    average_loc: float
    average_commits: float
    average_stars: float
    average_forks: float

    class Config:
        frozen = True

class LanguageDistribution(BaseModel):
    languages: Dict[str, PositiveInt]

    class Config:
        frozen = True

class RepoAnalysisSummary(BaseModel):
    aggregate_metrics: AggregateRepoMetrics
    language_distribution: LanguageDistribution

    class Config:
        frozen = True

__all__ = [
    "RepoStats",
    "RepoAnalysisResult",
    "AggregateRepoMetrics",
    "LanguageDistribution",
    "RepoAnalysisSummary"
]