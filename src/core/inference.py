from typing import Dict, Any, Optional, List
import asyncio

import pandas as pd

from src.core.prediction_schema import PredictionResult
from src.infrastructure.ml.loader import ModelArtifactLoader

from src.infrastructure.services.prediction import PredictionService

from utils.logger import get_logger
logger = get_logger()

# API and db uses credit_score instead of CreditScore
FEATURE_FIELD_MAP: Dict[str, Any] = {
    "credit_score": "CreditScore",
    "geography": "Geography",
    "gender": "Gender",
    "age": "Age",
    "balance": "Balance",
    "is_active_member": "IsActiveMember"
}
FEATURE_FIELDS = tuple(FEATURE_FIELD_MAP.keys())

class ChurnInference:
    """Core inference layer for our model"""

    def __init__(
        self,
        model_loader: ModelArtifactLoader,
        prediction_service: PredictionService
    ) -> None:
        self.model_loader = model_loader
        self.prediction_service = prediction_service

    def validate_features(
        self,
        features: Dict[str, Any]
    ) -> None:
        """
        Validate provided features for inference
        """
        missing = [name for name in FEATURE_FIELDS if name not in features]
        extras = [name for name in features if name not in FEATURE_FIELDS]

        if missing:
            raise ValueError(f"Missing required features: {', '.join(missing)}")
        
        if extras:
            raise ValueError(f"Unexpected features: {', '.join(extras)}")

    async def predict(
        self,
        features: Dict[str, Any]
    ) -> PredictionResult:
        # logger.info(f"features provided for predict in churn inference: {features}\n")
        self.validate_features(features)

        features["balance"] = float(features["balance"])

        model_row = {
            FEATURE_FIELD_MAP[field]: features[field] for field in FEATURE_FIELDS
        }

        # logger.info(f"features aligned for predict in churn inference: {model_row}\n")

        frame = pd.DataFrame([model_row])[self.model_loader.schema["feature_columns"]]

        # logger.info(f"dataframe in predict in churn inference: {frame}\n")

        probabilities = self.model_loader.model.predict_proba(frame)

        # logger.info(f"Predicted probabilities: {probabilities}\n")

        # get our probability for churned (1)
        probability = round(float(probabilities[0][1]), 2)
        # logger.info(f"Probability: {probability}")
        threshold = float(self.model_loader.metadata.get("decision_threshold", 0.5))
        # logger.info(f"Threshold: {threshold}")
        predicted = int(probability > threshold)
        # logger.info(f"Predicted: {predicted}")

        prediction_result = PredictionResult(
            predicted_churn=predicted,
            churn_probability=probability,
            decision_threshold=threshold,
            model_name=self.model_loader.metadata.get("best_model", "unknown"),
            model_version=self.model_loader.metadata.get("model_version", '1.0')
        )

        prediction_data = {**features, **prediction_result.to_dict()}
        if "label" in prediction_data.keys():
            del prediction_data["label"]
        prediction_data["is_active_member"] = 1 if prediction_data["is_active_member"] else 0

        # logger.info(f"Prediction data: {prediction_data}")

        # create the prediction record
        record = await self.prediction_service.create_prediction(prediction_data)

        logger.info(f"Prediction record: {record}")

        return prediction_result

    async def list_predictions(
        self,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        return await self.prediction_service.list_predictions(
            page=page,
            limit=limit
        )

    async def update_actual(
        self,
        prediction_id: str,
        actual_churn: int,
        notes: str = None
    ) -> Dict[str, Any]:
        
        return await self.prediction_service.update_actual(
            prediction_id=prediction_id,
            actual_churn=actual_churn,
            notes=notes
        )