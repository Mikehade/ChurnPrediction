from uuid import UUID
from typing import Dict, List, Any, Optional
from src.infrastructure.repositories.prediction import SQLAlchemyPredictionRepository

from utils.logger import get_logger

logger = get_logger()

class PredictionService:
    """service layer for prediction operations"""

    def __init__(
        self,
        repository: SQLAlchemyPredictionRepository
    ) -> None:
        self.repo = repository

    async def list_predictions(
        self,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """service method to list predictions """

        try:
            logger.info(f"Page: {type(page)}, limit: {type(limit)}")

            if not isinstance(page, int) or not isinstance(limit, int):
                return {
                    "success": False,
                    "message": "Please provide a valid integer for page or limit",
                    "data": []
                }

            offset = limit * (page - 1)

            result = await self.repo.list_predictions(
                limit=limit,
                offset=offset,
            )

            return {
                    "success": True,
                    "message": f"Successfully listed predictions for page: {page}",
                    "data": result
                }

        except Exception as e:
            logger.error(f"Error occured while listing predictions in predictions sevice: {e}")
            return {
                    "success": False,
                    "message": "Error occured while listing predictions, please try again later",
                    "data": []
                }

        
    async def create_prediction(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """service method to create prediction """

        try:
            logger.info(f"In create prediction: {data}")

            if not isinstance(data.get("credit_score"), int) or not isinstance(data.get("age"), int) or not isinstance(data.get("balance"), float) or not isinstance(data.get("is_active_member"), int)  or not isinstance(data.get("predicted_churn"), int)  or not isinstance(data.get("churn_probability"), float) or not isinstance(data.get("decision_threshold"), float):
                return {
                    "success": False,
                    "message": f"Unable to create prediction, please provide valid data",
                    "data": {}
                }
                
            result = await self.repo.create(data)


            return {
                    "success": True,
                    "message": f"Successfully created prediction",
                    "data": result
                }

        except Exception as e:
            logger.error(f"Error occured while creating prediction in predictions sevice: {e}")
            return {
                    "success": False,
                    "message": "Error occured while creating predictions, please try again later",
                    "data": {}
                }

    
    async def update_actual(
        self,
        prediction_id: str,
        actual_churn: int,
        notes: str = None
    ) -> Dict[str, Any]:
        """service method to update actual churn status of a prediction """

        try:
            prediction_id = UUID(prediction_id)

            if not isinstance(actual_churn, int):
                return {
                    "success": False,
                    "message": f"Unable to update prediction, please provide valid integer for actual churn",
                    "data": {}
                }
                
            result = await self.repo.update_actual(
                prediction_id=prediction_id, 
                actual_churn=actual_churn, 
                notes=notes
            )


            return {
                    "success": True,
                    "message": f"Successfully updated prediction",
                    "data": result
                }
    
        except ValueError as e:
            return {
                    "success": False,
                    "message": "Error occured while updating actual prediction, please provide valid UUID",
                    "data": {}
                }

        except Exception as e:
            logger.error(f"Error occured while updating actual prediction in predictions sevice: {e}")
            return {
                    "success": False,
                    "message": "Error occured while updating actual prediction, please try again later",
                    "data": {}
                }