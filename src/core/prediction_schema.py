from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PredictionResult:
    predicted_churn: int
    churn_probability: float
    decision_threshold: float
    model_name: str
    model_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            'predicted_churn': self.predicted_churn,
            'label': 'Churned' if self.predicted_churn == 1 else 'Stayed',
            'churn_probability': round(self.churn_probability, 6),
            'decision_threshold': self.decision_threshold,
            'model_name': self.model_name,
            'model_version': self.model_version,
        }
