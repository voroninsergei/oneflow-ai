from fastapi import APIRouter, HTTPException, Depends
from .schemas import RequestSchemaV1, ResponseSchemaV1, ErrorResponseV1
from src.main import OneFlowAI
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.post("/request", response_model=ResponseSchemaV1, responses={
    400: {"model": ErrorResponseV1},
    500: {"model": ErrorResponseV1}
})
async def process_request_v1(request: RequestSchemaV1):
    """
    Обработка запроса к AI провайдеру (API v1)
    """
    try:
        system = OneFlowAI()
        result = system.process_request(
            request.provider,
            request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return ResponseSchemaV1(
            status="success",
            response=result.get("response"),
            cost=result.get("cost", 0.0),
            provider_used=result.get("provider", request.provider),
            timestamp=datetime.utcnow(),
            request_id=str(uuid.uuid4()),
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
