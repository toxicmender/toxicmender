from pydantic import BaseModel, Field
from typing import Dict, List, Union

class MetricResult(BaseModel):
    name: str
    values: Dict[str, Union[List[int], List[float], int, float]]
    repo_names: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary format for JSON serialization."""
        return {
            "name": self.name,
            "values": self.values,
            "repo_names": self.repo_names
        }

    def get_value_by_repo(self, repo_name: str, dimension_key: str = None) -> Union[float, int, None]:
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
    score: float = Field(ge=0, le=100)
    components: Dict[str, float]

class EvaluationReport(BaseModel):
    metrics: Dict[str, MetricResult]
    overall_score: ScoreResult

__all__ = [
    "MetricResult",
    "ScoreResult",
    "EvaluationReport"
]

# Example usage:
if __name__ == "__main__":
    accuracy_metric = MetricResult(
        name="Accuracy",
        values={"train": 0.95, "test": 0.92}
    )

    f1_metric = MetricResult(
        name="F1 Score",
        values={"train": 0.93, "test": 0.90}
    )

    overall_score = ScoreResult(
        score=91.0,
        components={"accuracy": 92.0, "f1_score": 90.0}
    )

    report = EvaluationReport(
        metrics={
            "accuracy": accuracy_metric,
            "f1_score": f1_metric
        },
        overall_score=overall_score
    )

    print(report.json(indent=4))