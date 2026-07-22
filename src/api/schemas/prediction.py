from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    """Raw features required to run a churn prediction."""
    credit_score: int
    geography: str
    gender: str
    age: int
    balance: float
    is_active_member: int


class PredictionResponse(BaseModel):
    """Result returned immediately after running inference."""
    predicted_churn: int
    churn_probability: float
    decision_threshold: float
    model_name: str
    model_version: str


class UpdateActualRequest(BaseModel):
    """Payload for recording the real-world outcome of a prediction."""
    actual_churn: int
    notes: Optional[str] = None


class PredictionRecord(BaseModel):
    """Full persisted prediction record, as stored/returned by the repository."""
    id: UUID
    model_name: str
    credit_score: int
    geography: str
    gender: str
    age: int
    balance: float
    is_active_member: int
    predicted_churn: int
    churn_probability: float
    decision_threshold: float
    actual_churn: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class PaginatedPredictionsResponse(BaseModel):
    """Page of persisted prediction records."""
    page: int
    limit: int
    data: List[PredictionRecord]