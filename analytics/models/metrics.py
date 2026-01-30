from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Union, Optional

class MetricResult(BaseModel):
    model_config = {'frozen': False}

    name: str
    values: Dict[str, Union[List[int], List[float], int, float]]
    repo_names: List[str] = Field(default_factory=list)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate metric name is not empty."""
        if not v or not v.strip():
            raise ValueError("Metric name cannot be empty")
        return v.strip()

    def to_dict(self) -> Dict:
        """Convert to dictionary format for JSON serialization."""
        return {
            "name": self.name,
            "values": self.values,
            "repo_names": self.repo_names
        }

    def get_value_by_repo(self, repo_name: str, dimension_key: Optional[str] = None) -> Union[float, int, None]:
        """
        Get value for a specific repository (backward compatibility helper).

        Args:
            repo_name: Name of the repository
            dimension_key: Specific dimension key to retrieve (if None, gets first dimension)

        Returns:
            Value for the repository or None if not found
        """
        try:
            repo_index = self.repo_names.index(repo_name)

            # If dimension_key not specified, use first available dimension
            if dimension_key is None:
                dimension_key = next(iter(self.values.keys()))

            values_list = self.values[dimension_key]
            return values_list[repo_index]
        except (ValueError, IndexError, KeyError):
            return None

    def __contains__(self, item: str) -> bool:
        """Check if a repo_name exists (backward compatibility)."""
        return item in self.repo_names

class ScoreResult(BaseModel):
    model_config = {'frozen': True}

    score: float = Field(ge=0, le=100)
    components: Dict[str, float] = Field(default_factory=dict)

    @field_validator('components')
    @classmethod
    def validate_components(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate component scores are in valid range."""
        for key, score in v.items():
            if not (0 <= score <= 100):
                raise ValueError(f"Component score '{key}' must be in [0, 100], got {score}")
        return v

class EvaluationReport(BaseModel):
    model_config = {'frozen': False}

    metrics: Dict[str, MetricResult]
    overall_score: ScoreResult

__all__ = [
    "MetricResult",
    "ScoreResult",
    "EvaluationReport"
]
