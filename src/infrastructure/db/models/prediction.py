from sqlalchemy import Boolean, Column, Float, Integer, String, Text

from src.infrastructure.db.base import Base


class ChurnPrediction(Base):
    """Stores inputs, model outputs, and eventual real-world outcomes.

    Unlike the original pilot-attrition project (which stored the raw
    features as one JSON column), this table has one explicit column per
    model feature. This is only practical because the feature set here is
    small (6 columns) and fixed.
    """

    __tablename__ = 'churn_prediction'

    model_name = Column(String(120), nullable=False, index=True)
    model_version = Column(String(80), nullable=True)

    # --- Feature columns (one per model input) ---
    credit_score = Column(Integer, nullable=False)
    geography = Column(String(80), nullable=False)
    gender = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    balance = Column(Float, nullable=False)
    is_active_member = Column(Integer, nullable=False)

    # --- Model output ---
    predicted_churn = Column(Integer, nullable=False, index=True)
    churn_probability = Column(Float, nullable=False)
    decision_threshold = Column(Float, nullable=False)

    # --- Filled later when the real outcome becomes known ---
    actual_churn = Column(Integer, nullable=True, index=True)
    actual_recorded = Column(Boolean, nullable=False, default=False)

    source = Column(String(100), nullable=False, default='api')
    external_reference = Column(String(255), nullable=True, index=True)
    notes = Column(Text, nullable=True)
