"""
src/api/app.py - Production-Ready FastAPI Application
Тонкий entrypoint с полной observability: healthz, CORS, RFC7807, Prometheus, OTEL
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_client import make_asgi_app

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Импорты модулей проекта
try:
    from observability.structured_logging import setup_logging, get_logger
    from observability.telemetry import init_telemetry, get_telemetry
    from observability.metrics import init_metrics, metrics_endpoint
    from api.common.errors import ProblemDetail, ErrorCode
    from security.cors_config import configure_security
    HAS_OBSERVABILITY = True
except ImportError as e:
    logging.warning(f"Observability modules not available: {e}")
    HAS_OBSERVABILITY = False
    get_logger = lambda name: logging.getLogger(name)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Application configuration"""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Service info
    SERVICE_NAME = "oneflow-ai"
    SERVICE_VERSION = "2.0.0"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Observability
    OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    TRACING_ENABLED = os.getenv("TRACING_ENABLED", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    JSON_LOGS = os.getenv("JSON_LOGS", "true").lower() == "true"


config = Config()


# ============================================================================
# LOGGING SETUP
# ============================================================================

if HAS_OBSERVABILITY:
    setup_logging(
        level=config.LOG_LEVEL,
        json_logs=config.JSON_LOGS,
        environment=config.ENVIRONMENT
    )
    log = get_logger(__name__)
else:
    logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
    log = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # ========== STARTUP ==========
    log.info(
        "application_starting",
        service=config.SERVICE_NAME,
        version=config.SERVICE_VERSION,
        environment=config.ENVIRONMENT,
        debug=config.DEBUG
    )
    
    # Initialize observability
    if HAS_OBSERVABILITY:
        # Initialize telemetry (OpenTelemetry)
        if config.TRACING_ENABLED:
            telemetry = init_telemetry(
                service_name=config.SERVICE_NAME,
                service_version=config.SERVICE_VERSION,
                environment=config.ENVIRONMENT,
                otlp_endpoint=config.OTLP_ENDPOINT
            )
            telemetry.instrument_app(app)
            telemetry.instrument_http_clients()
            log.info("telemetry_initialized", tracing=True)
        
        # Initialize metrics (Prometheus)
        if config.METRICS_ENABLED:
            init_metrics(
                version=config.SERVICE_VERSION,
                environment=config.ENVIRONMENT
            )
            log.info("metrics_initialized", metrics=True)
    
    log.info(
        "application_ready",
        service=config.SERVICE_NAME,
        host=config.HOST,
        port=config.PORT
    )
    
    yield
    
    # ========== SHUTDOWN ==========
    log.info("application_shutting_down")
    
    # Cleanup telemetry
    if HAS_OBSERVABILITY and config.TRACING_ENABLED:
        try:
            get_telemetry().shutdown()
            log.info("telemetry_shutdown_complete")
        except Exception as e:
            log.error("telemetry_shutdown_error", error=str(e))
    
    log.info("application_shutdown_complete")


# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    Создать и настроить FastAPI приложение
    """
    
    app = FastAPI(
        title="OneFlow.AI API",
        description="Multi-provider AI orchestration platform with intelligent routing",
        version=config.SERVICE_VERSION,
        docs_url="/api/docs" if config.DEBUG else None,
        redoc_url="/api/redoc" if config.DEBUG else None,
        openapi_url="/api/openapi.json" if config.DEBUG else None,
        lifespan=lifespan,
        # Disable default 422 validation responses in favor of RFC 7807
        responses={
            422: {
                "description": "Validation Error",
                "content": {
                    "application/problem+json": {
                        "schema": {"$ref": "#/components/schemas/ProblemDetail"}
                    }
                }
            }
        }
    )
    
    # ========================================================================
    # MIDDLEWARE STACK (order matters!)
    # ========================================================================
    
    # 1. Security (CORS, headers, payload limiter, request ID)
    if HAS_OBSERVABILITY:
        configure_security(
            app,
            environment=config.ENVIRONMENT,
            max_payload_size=10 * 1024 * 1024  # 10MB
        )
    else:
        # Fallback basic CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
        )
    
    # 2. Request logging middleware
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        """Log request and response with timing"""
        import time
        import uuid
        
        # Get or generate request ID
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        start_time = time.time()
        
        log.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        try:
            response = await call_next(request)
            
            duration = (time.time() - start_time) * 1000
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"
            
            log.info(
                "request_completed",
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=f"{duration:.2f}"
            )
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            log.error(
                "request_failed",
                request_id=request_id,
                error=str(e),
                duration_ms=f"{duration:.2f}",
                exc_info=True
            )
            raise
    
    # ========================================================================
    # EXCEPTION HANDLERS (RFC 7807)
    # ========================================================================
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions with RFC 7807 Problem Details"""
        request_id = getattr(request.state, "request_id", None)
        
        if HAS_OBSERVABILITY:
            problem = ProblemDetail.create(
                error_code=ErrorCode.VALIDATION_ERROR if exc.status_code == 422 else ErrorCode.NOT_FOUND,
                title=exc.detail or "HTTP Error",
                status=exc.status_code,
                detail=str(exc.detail) if exc.detail else None,
                instance=str(request.url.path),
                request_id=request_id
            )
            content = problem.model_dump(exclude_none=True)
        else:
            content = {
                "type": f"https://oneflow.ai/errors/http-{exc.status_code}",
                "title": exc.detail or "HTTP Error",
                "status": exc.status_code,
                "instance": str(request.url.path),
                "request_id": request_id
            }
        
        log.error(
            "http_exception",
            request_id=request_id,
            status_code=exc.status_code,
            detail=exc.detail
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers={"Content-Type": "application/problem+json"}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors with RFC 7807"""
        request_id = getattr(request.state, "request_id", None)
        
        if HAS_OBSERVABILITY:
            problem = ProblemDetail.create(
                error_code=ErrorCode.VALIDATION_ERROR,
                title="Request Validation Error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The request contains invalid parameters",
                instance=str(request.url.path),
                request_id=request_id,
                validation_errors=exc.errors()
            )
            content = problem.model_dump(exclude_none=True)
        else:
            content = {
                "type": "https://oneflow.ai/errors/validation_error",
                "title": "Request Validation Error",
                "status": 422,
                "detail": "The request contains invalid parameters",
                "instance": str(request.url.path),
                "request_id": request_id,
                "validation_errors": exc.errors()
            }
        
        log.warning(
            "validation_error",
            request_id=request_id,
            errors=exc.errors()
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=content,
            headers={"Content-Type": "application/problem+json"}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with RFC 7807"""
        request_id = getattr(request.state, "request_id", None)
        
        if HAS_OBSERVABILITY:
            problem = ProblemDetail.create(
                error_code=ErrorCode.INTERNAL_ERROR,
                title="Internal Server Error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred" if not config.DEBUG else str(exc),
                instance=str(request.url.path),
                request_id=request_id
            )
            content = problem.model_dump(exclude_none=True)
        else:
            content = {
                "type": "https://oneflow.ai/errors/internal_error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred" if not config.DEBUG else str(exc),
                "instance": str(request.url.path),
                "request_id": request_id
            }
        
        log.error(
            "internal_server_error",
            request_id=request_id,
            error=str(exc),
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
            headers={"Content-Type": "application/problem+json"}
        )
    
    # ========================================================================
    # HEALTH CHECK ENDPOINTS
    # ========================================================================
    
    @app.get("/healthz", tags=["Health"], status_code=200)
    async def healthz():
        """
        Kubernetes health check endpoint
        Returns 200 OK if service is healthy
        """
        return {
            "status": "healthy",
            "service": config.SERVICE_NAME,
            "version": config.SERVICE_VERSION,
            "environment": config.ENVIRONMENT
        }
    
    @app.get("/livez", tags=["Health"], status_code=200)
    async def livez():
        """
        Kubernetes liveness probe
        Returns 200 OK if service process is alive
        """
        return {"status": "alive"}
    
    @app.get("/readyz", tags=["Health"])
    async def readyz():
        """
        Kubernetes readiness probe
        Returns 200 OK if service is ready to accept traffic
        Checks dependencies (database, cache, etc.)
        """
        # TODO: Add dependency checks
        # - Database connectivity
        # - Redis/Cache availability
        # - External API availability
        
        dependencies_ready = True  # Placeholder
        
        if not dependencies_ready:
            log.warning("readiness_check_failed", dependencies_ready=False)
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not ready",
                    "message": "Service dependencies are not available"
                }
            )
        
        return {"status": "ready"}
    
    # ========================================================================
    # METRICS ENDPOINT (Prometheus)
    # ========================================================================
    
    if HAS_OBSERVABILITY and config.METRICS_ENABLED:
        # Mount Prometheus metrics endpoint
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        
        log.info("metrics_endpoint_mounted", path="/metrics")
    
    # ========================================================================
    # ROOT ENDPOINT
    # ========================================================================
    
    @app.get("/", tags=["Root"])
    async def root():
        """
        API root endpoint with service information
        Корневой endpoint API с информацией о сервисе
        """
        return {
            "service": config.SERVICE_NAME,
            "version": config.SERVICE_VERSION,
            "environment": config.ENVIRONMENT,
            "documentation": {
                "swagger": "/api/docs" if config.DEBUG else None,
                "redoc": "/api/redoc" if config.DEBUG else None,
                "openapi": "/api/openapi.json" if config.DEBUG else None
            },
            "health": {
                "health_check": "/healthz",
                "liveness": "/livez",
                "readiness": "/readyz"
            },
            "observability": {
                "metrics": "/metrics" if config.METRICS_ENABLED else None,
                "tracing": config.TRACING_ENABLED
            },
            "supported_versions": ["v1", "v2"],
            "current_version": "v2"
        }
    
    # ========================================================================
    # VERSIONED API ROUTERS
    # ========================================================================
    
    # Import and include versioned routers
    try:
        from api.v1.endpoints import router as v1_router
        app.include_router(v1_router, prefix="/api/v1", tags=["API v1"])
        log.info("v1_router_registered", prefix="/api/v1")
    except ImportError as e:
        log.warning("v1_router_not_available", error=str(e))
    
    try:
        from api.v2.endpoints import router as v2_router
        app.include_router(v2_router, prefix="/api/v2", tags=["API v2"])
        log.info("v2_router_registered", prefix="/api/v2")
    except ImportError as e:
        log.warning("v2_router_not_available", error=str(e))
    
    # ========================================================================
    # STARTUP LOG
    # ========================================================================
    
    log.info(
        "application_configured",
        service=config.SERVICE_NAME,
        version=config.SERVICE_VERSION,
        environment=config.ENVIRONMENT,
        debug=config.DEBUG,
        cors_origins=config.CORS_ORIGINS,
        metrics_enabled=config.METRICS_ENABLED,
        tracing_enabled=config.TRACING_ENABLED
    )
    
    return app


# ============================================================================
# APPLICATION INSTANCE
# ============================================================================

# Create application instance
app = create_app()


# ============================================================================
# CLI ENTRYPOINT (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print(f"🚀 Starting {config.SERVICE_NAME} v{config.SERVICE_VERSION}")
    print("=" * 70)
    print(f"\nEnvironment: {config.ENVIRONMENT}")
    print(f"Debug mode: {config.DEBUG}")
    print(f"Host: {config.HOST}:{config.PORT}")
    print(f"\nEndpoints:")
    print(f"  Health:   http://{config.HOST}:{config.PORT}/healthz")
    print(f"  Liveness: http://{config.HOST}:{config.PORT}/livez")
    print(f"  Readiness: http://{config.HOST}:{config.PORT}/readyz")
    if config.METRICS_ENABLED:
        print(f"  Metrics:  http://{config.HOST}:{config.PORT}/metrics")
    if config.DEBUG:
        print(f"  Docs:     http://{config.HOST}:{config.PORT}/api/docs")
    print("\n" + "=" * 70)
    
    # Run with uvicorn
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )
