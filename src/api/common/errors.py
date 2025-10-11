"""
RFC 7807 Problem Details for HTTP APIs.
RFC 7807 Problem Details для HTTP API.
"""

from typing import Any, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ErrorCode(str, Enum):
    """Standard error codes."""

    # Authentication & Authorization
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    INVALID_API_KEY = "invalid_api_key"

    # Validation
    VALIDATION_ERROR = "validation_error"
    INVALID_REQUEST = "invalid_request"
    MISSING_PARAMETER = "missing_parameter"

    # Resources
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    CONFLICT = "conflict"

    # Rate Limiting & Quotas
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"

    # Wallet & Billing
    INSUFFICIENT_FUNDS = "insufficient_funds"
    PAYMENT_REQUIRED = "payment_required"

    # Providers
    PROVIDER_ERROR = "provider_error"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    ALL_PROVIDERS_FAILED = "all_providers_failed"

    # System
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    TIMEOUT = "timeout"


class ProblemDetail(BaseModel):
    """
    RFC 7807 Problem Details for HTTP APIs.

    See: https://tools.ietf.org/html/rfc7807
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "type": "https://oneflow.ai/errors/insufficient_funds",
                "title": "Insufficient Funds",
                "status": 402,
                "detail": "Account balance is too low to process request",
                "instance": "/api/v2/requests/12345",
                "request_id": "req_abc123xyz",
                "balance": 5.0,
                "required": 10.0,
            }
        },
    )

    type: str = Field(
        ...,
        description="URI reference identifying the problem type",
        examples=["https://oneflow.ai/errors/insufficient_funds"],
    )
    title: str = Field(
        ...,
        description="Short, human-readable summary of the problem",
        examples=["Insufficient Funds"],
    )
    status: int = Field(
        ...,
        ge=100,
        le=599,
        description="HTTP status code",
        examples=[402],
    )
    detail: Optional[str] = Field(
        None,
        description="Human-readable explanation specific to this occurrence",
        examples=["Account balance is too low to process request"],
    )
    instance: Optional[str] = Field(
        None,
        description="URI reference identifying the specific occurrence",
        examples=["/api/v2/requests/12345"],
    )

    # Additional custom fields
    request_id: Optional[str] = Field(
        None,
        description="Unique request identifier for debugging",
        examples=["req_abc123xyz"],
    )
    timestamp: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp of when error occurred",
        examples=["2025-10-11T12:34:56.789Z"],
    )

    class Config:
        extra = "allow"  # Allow additional custom fields

    @classmethod
    def create(
        cls,
        error_code: ErrorCode,
        title: str,
        status: int,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        request_id: Optional[str] = None,
        **extra_fields: Any,
    ) -> "ProblemDetail":
        """
        Factory method to create ProblemDetail.

        Args:
            error_code: Standard error code.
            title: Short description.
            status: HTTP status code.
            detail: Detailed description.
            instance: URI of specific occurrence.
            request_id: Request identifier.
            **extra_fields: Additional custom fields.

        Returns:
            ProblemDetail instance.
        """
        from datetime import datetime, timezone

        return cls(
            type=f"https://oneflow.ai/errors/{error_code.value}",
            title=title,
            status=status,
            detail=detail,
            instance=instance,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            **extra_fields,
        )


__all__ = [
    "ProblemDetail",
    "ErrorCode",
]
