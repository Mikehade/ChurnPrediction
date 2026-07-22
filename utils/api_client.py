import os
from typing import Any, Dict, Optional

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
DEFAULT_TIMEOUT = 10


class APIClientError(Exception):
    """Raised when the API is unreachable or returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


def _request(method: str, path: str, **kwargs) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{path}"

    try:
        response = requests.request(method, url, timeout=DEFAULT_TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError as e:
        raise APIClientError(
            f"Could not reach the API at {url}. Is the server running?"
        ) from e
    except requests.exceptions.Timeout as e:
        raise APIClientError(f"Request to {url} timed out.") from e

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise APIClientError(detail, status_code=response.status_code)

    try:
        return response.json()
    except ValueError as e:
        raise APIClientError(
            "API returned a non-JSON response.", status_code=response.status_code
        ) from e


def create_prediction(features: Dict[str, Any]) -> Dict[str, Any]:
    """POST /predictions/ - run a single churn prediction.

    features: dict with credit_score, geography, gender, age, balance,
    is_active_member.
    """
    return _request("POST", "/predictions/", json=features)


def list_predictions(page: int = 1, limit: int = 50) -> Dict[str, Any]:
    """GET /predictions/ - fetch a page of persisted predictions."""
    return _request("GET", "/predictions/", params={"page": page, "limit": limit})


def update_actual(
    prediction_id: str, actual_churn: int, notes: Optional[str] = None
) -> Dict[str, Any]:
    """PATCH /predictions/{id}/actual - record the true outcome for a prediction."""
    return _request(
        "PATCH",
        f"/predictions/{prediction_id}/actual",
        json={"actual_churn": actual_churn, "notes": notes},
    )


def health_check() -> Dict[str, Any]:
    """GET /health - basic connectivity check, used by the homepage.

    Adjust the path here if your health router is mounted somewhere else.
    """
    return _request("GET", "/health")