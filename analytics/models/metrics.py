from pydantic import BaseModel, Field
from typing import Dict

class MetricResult(BaseModel):
    name: str
    values: Dict[str, float]

class ScoreResult(BaseModel):
    score: float = Field(ge=0, le=100)
    components: Dict[str, float]

class EvaluationReport(BaseModel):
    metrics: Dict[str, MetricResult]
    overall_score: ScoreResult

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