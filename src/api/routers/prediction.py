from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.container import Container
from src.core.inference import ChurnInference

from src.api.schemas.prediction import (
    PaginatedPredictionsResponse,
    PredictionRecord,
    PredictionRequest,
    PredictionResponse,
    UpdateActualRequest,
)

from utils.logger import get_logger

logger = get_logger()

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/", response_model=PredictionResponse, status_code=201)
@inject
async def create_prediction(
    payload: PredictionRequest,
    inference: ChurnInference = Depends(Provide[Container.inference]),
):
    """Run inference on a single set of features and persist the result."""
    try:
        result = await inference.predict(payload.model_dump())
        return result.to_dict()
    except ValueError as e:
        # raised by ChurnInference.validate_features for missing/extra fields
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to create prediction, please try again later",
        )


@router.get("/", response_model=PaginatedPredictionsResponse)
@inject
async def list_predictions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    inference: ChurnInference = Depends(Provide[Container.inference]),
):
    """List persisted predictions, paginated."""
    result = await inference.list_predictions(page=page, limit=limit)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return {
        "page": page,
        "limit": limit,
        "data": result.get("data", []),
    }


@router.patch("/{prediction_id}/actual", response_model=PredictionRecord)
@inject
async def update_actual(
    prediction_id: str,
    payload: UpdateActualRequest,
    inference: ChurnInference = Depends(Provide[Container.inference]),
):
    """Record the real-world outcome for an existing prediction."""
    result = await inference.update_actual(
        prediction_id=prediction_id,
        actual_churn=payload.actual_churn,
        notes=payload.notes,
    )

    if not result.get("success"):
        # covers invalid UUID and unexpected repository/service errors
        raise HTTPException(status_code=400, detail=result.get("message"))

    data = result.get("data")
    if not data:
        # repository returns None when no matching (non-deleted) record exists
        raise HTTPException(
            status_code=404,
            detail=f"Prediction {prediction_id} not found",
        )

    return data