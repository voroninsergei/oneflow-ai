"""
Standard API response models.
Стандартные модели ответов API.
"""

from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    Стандартная обёртка ответа API.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {"id": "req_123", "status": "completed"},
                "timestamp": "2025-10-11T12:34:56.789Z",
                "request_id": "req_abc123xyz",
            }
        }
    )

    success: bool = Field(
        ..., description="Indicates if request was successful", examples=[True]
    )
    data: Optional[T] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(
        None, description="Error details (if success=False)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp",
        examples=["2025-10-11T12:34:56.789Z"],
    )
    request_id: Optional[str] = Field(
        None,
        description="Unique request identifier",
        examples=["req_abc123xyz"],
    )


__all__ = [
    "APIResponse",
]
