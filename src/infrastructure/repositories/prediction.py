from typing import Any, Dict, List, Optional, Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.infrastructure.db.models.prediction import ChurnPrediction

from utils.logger import get_logger

logger = get_logger()

FEATURE_COLUMNS = [
    "credit_score",
    "geography",
    "gender",
    "age",
    "balance",
    "is_active_member"
]

class SQLAlchemyPredictionRepository:

    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    def _to_dict(
        self,
        model: ChurnPrediction
    ) -> Dict[str, Any]:
        data = {
            "id": str(model.id),
            "model_name": model.model_name,
            "credit_score": model.credit_score,
            "geography": model.geography,
            "gender": model.gender,
            "age": model.age,
            "balance": model.balance,
            "is_active_member": model.is_active_member,
            "predicted_churn": model.predicted_churn,
            "churn_probability": model.churn_probability,
            "decision_threshold": model.decision_threshold,
            "actual_churn": model.actual_churn,
            "created_at": model.created_at,
            "updated_at": model.updated_at
        }

        return data

    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """ 
        Method for creating a new record for a prediction

        Input:
        {
            "credit_score": 500,
            "geography": "German",
            "gender": "male",
            "age": 59,
            "balance": 100000,
            "is_active_member": 0
        }

        returns
        - sqlalchemy object


        """
        try:
            async with self.session_factory() as session:
                model = ChurnPrediction(**data)
                session.add(model)
                await session.commit()
                await session.refresh(model)

                return self._to_dict(model)

        except IntegrityError as e:
            logger.error(f"Integrity error creating user: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating prediction: {e}")
            raise

    async def list_predictions(
        self,
        limit: int = 50,
        offset: int =  0,
        actual_recorded: bool = False,
    ) -> Dict[str, Any]:
        try:
            async with self.session_factory() as session:
                query = select(ChurnPrediction).where(
                    ChurnPrediction.deleted_at.is_(None)
                )

                if actual_recorded is True:
                    query = query.where(
                        ChurnPrediction.actual_recorded.is_(True)
                    )

                query = (
                    query.order_by(ChurnPrediction.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                )

                result = await session.execute(query)
                # return result
                return [self._to_dict(model) for model in result.scalars().all()]

        except Exception as e:
            logger.error(f"Error listing predictions: {e}")
            raise

    
    async def update_actual(
        self, 
        prediction_id: UUID, 
        actual_churn: int, 
        notes: str = None
    ) -> dict[str, Any] | None:
        """
        Update the actual churn status of an already predicted churn data
        Input:

        Output:

        """

        try:
            # logger.info(f"Prediction id: {type(prediction_id)}")
            # Update churn=1 where id=prediction_id
            async with self.session_factory() as session:
                model = await session.execute(select(ChurnPrediction).where(
                    ChurnPrediction.id==prediction_id
                ))

                model = model.scalar_one_or_none()

                if model is None or model.deleted_at is not None:
                    return None

                model.actual_churn = actual_churn
                model.actual_recorded = True

                # notes: - this prediction was wrong and had too high confidence
                if notes is not None:
                    model.notes = notes

                await session.commit()
                await session.refresh(model)
                return self._to_dict(model)


        except Exception as e:
            logger.error(f"Error updating a prediction: {e}")
            raise

        




