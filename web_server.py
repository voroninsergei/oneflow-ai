"""
OneFlow.AI Web Server - Production Ready
Secure FastAPI server with observability and security middleware
"""
import os
import re
import time
from datetime import datetime
from typing import Optional

import structlog
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.middleware.base import BaseHTTPMiddleware

# Инициализация structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False
)

logger = structlog.get_logger()

# Инициализация FastAPI
app = FastAPI(
    title="OneFlow.AI API",
    description="Production-ready AI Model Aggregator",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== SECURITY MIDDLEWARE =====

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Добавление security headers ко всем ответам"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Ограничение размера входящих запросов"""
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB по умолчанию
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_size:
                logger.warning(
                    "request_too_large",
                    content_length=content_length,
                    max_size=self.max_size,
                    path=request.url.path
                )
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request body too large"}
                )
        return await call_next(request)


class LogSanitizerMiddleware(BaseHTTPMiddleware):
    """Санитизация секретов в логах"""
    SENSITIVE_PATTERNS = [
        r'(api[_-]?key|token|secret|password|bearer)[\s:="]+([^\s"&]+)',
        r'(sk-[a-zA-Z0-9]{20,})',
        r'(Bearer\s+[a-zA-Z0-9\-._~+/]+=*)'
    ]

    @staticmethod
    def sanitize(text: str) -> str:
        """Замена чувствительных данных на ***"""
        for pattern in LogSanitizerMiddleware.SENSITIVE_PATTERNS:
            text = re.sub(pattern, r'\1=***REDACTED***', text, flags=re.IGNORECASE)
        return text

    async def dispatch(self, request: Request, call_next):
        # Санитизация headers
        sanitized_headers = {
            k: self.sanitize(v) if k.lower() in ['authorization', 'x-api-key'] else v
            for k, v in request.headers.items()
        }
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
            client_ip=request.client.host if request.client else None
        )
        
        return response


# ===== CORS Configuration =====
# ВАЖНО: Замените на ваши реальные домены в продакшене!
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# Trusted Host Protection (раскомментируйте в продакшене)
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
# )

# Применение custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)
app.add_middleware(LogSanitizerMiddleware)

# ===== OBSERVABILITY =====

# Prometheus metrics
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health", "/ready"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)

@app.on_event("startup")
async def startup():
    """Инициализация при старте приложения"""
    logger.info("application_startup", version="2.0.0")
    
    # Запуск Prometheus instrumentator
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    
    # OpenTelemetry tracing
    if os.getenv("ENABLE_TRACING", "false").lower() == "true":
        FastAPIInstrumentor.instrument_app(app)
        logger.info("opentelemetry_tracing_enabled")


@app.on_event("shutdown")
async def shutdown():
    """Очистка при остановке"""
    logger.info("application_shutdown")


# ===== HEALTH CHECKS =====

@app.get("/health", include_in_schema=False)
async def health_check():
    """Liveness probe - проверка, что приложение запущено"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/ready", include_in_schema=False)
async def readiness_check():
    """Readiness probe - проверка готовности к приёму запросов"""
    # Здесь можно добавить проверки БД, внешних сервисов и т.д.
    try:
        # Пример: проверка БД
        # db.execute("SELECT 1")
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")


# ===== MAIN API ENDPOINTS =====
# Здесь подключаются ваши существующие роуты из оригинального web_server.py

# Пример структуры:
# from src.main import OneFlowAI
# from src.auth_module import get_current_user
# 
# @app.post("/api/v1/request")
# async def process_request(
#     request_data: dict,
#     current_user: dict = Depends(get_current_user)
# ):
#     logger.info("processing_request", user_id=current_user["id"])
#     # ... ваша логика
#     return response


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "OneFlow.AI",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,  # Используем structlog вместо uvicorn логов
    )
