"""
Pydantic v2 схемы для API v1
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Literal, Optional
from datetime import datetime

class RequestSchemaV1(BaseModel):
    """Схема запроса API v1"""
    model_config = ConfigDict(
        strict=True,
        json_schema_extra={
            "examples": [{
                "provider": "gpt",
                "prompt": "Hello world",
                "max_tokens": 100
            }]
        }
    )
    
    provider: Literal["gpt", "claude", "stability", "elevenlabs"]
    prompt: str = Field(..., min_length=1, max_length=10000)
    max_tokens: Optional[int] = Field(None, gt=0, le=4096)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()

class ResponseSchemaV1(BaseModel):
    """Схема ответа API v1"""
    model_config = ConfigDict(strict=True)
    
    status: Literal["success", "error"]
    data: Optional[dict] = None
    response: Optional[str] = None
    cost: float = Field(..., ge=0.0)
    provider_used: str
    timestamp: datetime
    api_version: Literal["v1"] = "v1"
    request_id: str

class ErrorResponseV1(BaseModel):
    """Схема ошибки API v1"""
    status: Literal["error"] = "error"
    error_code: str
    message: str
    details: Optional[dict] = None
    api_version: Literal["v1"] = "v1"
