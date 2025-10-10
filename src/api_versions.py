"""
API Versioning Module for OneFlow.AI
Handles multiple API versions with backward compatibility
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


# ============================================================================
# API Version Enums
# ============================================================================

class APIVersion(str, Enum):
    """Supported API versions"""
    V1 = "v1"
    V2 = "v2"


class StabilityLevel(str, Enum):
    """API stability levels"""
    STABLE = "stable"
    BETA = "beta"
    DEPRECATED = "deprecated"


# ============================================================================
# Pydantic v2 Base Schemas
# ============================================================================

class BaseRequestSchema(BaseModel):
    """Base request schema with Pydantic v2"""
    model_config = ConfigDict(
        strict=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "provider": "gpt",
                "prompt": "Hello world"
            }
        }
    )


class RequestSchemaV1(BaseRequestSchema):
    """API v1 Request Schema"""
    provider: str = Field(
        ...,
        description="AI provider name (gpt, image, audio, video)",
        min_length=1,
        max_length=50
    )
    prompt: str = Field(
        ...,
        description="User prompt or request text",
        min_length=1,
        max_length=10000
    )
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )


class RequestSchemaV2(BaseRequestSchema):
    """API v2 Request Schema - Extended with new fields"""
    provider: str = Field(
        ...,
        description="AI provider name",
        min_length=1,
        max_length=50
    )
    prompt: str = Field(
        ...,
        description="User prompt",
        min_length=1,
        max_length=10000
    )
    user_id: Optional[str] = Field(
        None,
        description="User identifier"
    )
    # New fields in V2
    model: Optional[str] = Field(
        None,
        description="Specific model name (e.g., gpt-4, claude-3)"
    )
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Model temperature parameter"
    )
    max_tokens: Optional[int] = Field(
        None,
        ge=1,
        le=100000,
        description="Maximum tokens in response"
    )
    stream: Optional[bool] = Field(
        False,
        description="Enable streaming response"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )


class ResponseSchemaV1(BaseModel):
    """API v1 Response Schema"""
    model_config = ConfigDict(strict=False)
    
    status: str = Field(..., description="Request status")
    response: Optional[str] = Field(None, description="AI response text")
    cost: float = Field(..., ge=0, description="Request cost in credits")
    provider: str = Field(..., description="Provider used")
    timestamp: Optional[datetime] = Field(None, description="Response timestamp")


class ResponseSchemaV2(BaseModel):
    """API v2 Response Schema - Extended"""
    model_config = ConfigDict(strict=False)
    
    status: str = Field(..., description="Request status")
    response: Optional[str] = Field(None, description="AI response text")
    cost: float = Field(..., ge=0, description="Request cost")
    provider: str = Field(..., description="Provider used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # New fields in V2
    model_used: Optional[str] = Field(None, description="Actual model used")
    tokens_used: Optional[int] = Field(None, description="Total tokens consumed")
    latency_ms: Optional[int] = Field(None, description="Response latency")
    request_id: str = Field(..., description="Unique request identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


# ============================================================================
# Version Info Schema
# ============================================================================

class VersionInfo(BaseModel):
    """API version information"""
    version: str
    stability: StabilityLevel
    deprecated: bool = False
    sunset_date: Optional[str] = None
    description: str
    endpoints: List[str]


# ============================================================================
# API Version Registry
# ============================================================================

class APIVersionRegistry:
    """Registry for managing API versions"""
    
    VERSIONS: Dict[APIVersion, VersionInfo] = {
        APIVersion.V1: VersionInfo(
            version="1.0.0",
            stability=StabilityLevel.STABLE,
            deprecated=False,
            sunset_date=None,
            description="Stable API v1 - Basic functionality",
            endpoints=["/request", "/status", "/analytics"]
        ),
        APIVersion.V2: VersionInfo(
            version="2.0.0",
            stability=StabilityLevel.STABLE,
            deprecated=False,
            sunset_date=None,
            description="API v2 - Extended features with streaming, metadata",
            endpoints=["/request", "/status", "/analytics", "/stream"]
        )
    }
    
    @classmethod
    def get_version_info(cls, version: APIVersion) -> VersionInfo:
        """Get information about specific API version"""
        return cls.VERSIONS.get(version)
    
    @classmethod
    def get_all_versions(cls) -> Dict[str, VersionInfo]:
        """Get all available API versions"""
        return {v.value: info for v, info in cls.VERSIONS.items()}
    
    @classmethod
    def is_deprecated(cls, version: APIVersion) -> bool:
        """Check if version is deprecated"""
        info = cls.VERSIONS.get(version)
        return info.deprecated if info else True


# ============================================================================
# Version Validation Dependency
# ============================================================================

def validate_api_version(version: str) -> APIVersion:
    """
    FastAPI dependency to validate API version from path
    """
    try:
        api_version = APIVersion(version)
        
        # Check if deprecated
        if APIVersionRegistry.is_deprecated(api_version):
            raise HTTPException(
                status_code=410,
                detail=f"API version {version} is deprecated"
            )
        
        return api_version
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid API version: {version}. Supported: {[v.value for v in APIVersion]}"
        )


# ============================================================================
# Router Factory
# ============================================================================

def create_versioned_router(version: APIVersion) -> APIRouter:
    """
    Factory function to create version-specific routers
    
    Usage:
        router_v1 = create_versioned_router(APIVersion.V1)
        router_v2 = create_versioned_router(APIVersion.V2)
    """
    return APIRouter(
        prefix=f"/api/{version.value}",
        tags=[f"API {version.value.upper()}"],
        dependencies=[Depends(lambda: validate_api_version(version.value))]
    )


# ============================================================================
# Example: Version-specific endpoints
# ============================================================================

# Create routers for each version
router_v1 = create_versioned_router(APIVersion.V1)
router_v2 = create_versioned_router(APIVersion.V2)


@router_v1.get("/info")
async def get_version_info_v1():
    """Get API v1 information"""
    return APIVersionRegistry.get_version_info(APIVersion.V1)


@router_v2.get("/info")
async def get_version_info_v2():
    """Get API v2 information"""
    return APIVersionRegistry.get_version_info(APIVersion.V2)


# Root endpoint to list all versions
def get_versions_endpoint():
    """Endpoint to list all available API versions"""
    return {
        "current_version": "v2",
        "supported_versions": APIVersionRegistry.get_all_versions(),
        "documentation": {
            "v1": "/api/v1/docs",
            "v2": "/api/v2/docs"
        }
    }
