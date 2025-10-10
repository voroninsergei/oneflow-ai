"""
FastAPI Application Module
Main application with health checks, versioning, CORS, error handlers, and structured logging
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging
import time
import json
from typing import Any, Dict
from datetime import datetime

from .routers import v1_router, v2_router
from .models import APIVersionRegistry


# ============================================================================
# Structured Logging Setup
# ============================================================================

class StructuredLogger:
    """Structured JSON logger"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self._json_formatter())
        self.logger.addHandler(handler)
    
    @staticmethod
    def _json_formatter():
        """Custom JSON formatter"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if hasattr(record, "request_id"):
                    log_data["request_id"] = record.request_id
                if hasattr(record, "extra"):
                    log_data.update(record.extra)
                return json.dumps(log_data)
        return JSONFormatter()
    
    def info(self, message: str, **kwargs):
        extra = {"extra": kwargs} if kwargs else {}
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        extra = {"extra": kwargs} if kwargs else {}
        self.logger.error(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        extra = {"extra": kwargs} if kwargs else {}
        self.logger.warning(message, extra=extra)


logger = StructuredLogger(__name__)


# ============================================================================
# RFC 7807 Problem Details
# ============================================================================

class ProblemDetail:
    """RFC 7807 Problem Details for HTTP APIs"""
    
    @staticmethod
    def create(
        type_: str,
        title: str,
        status: int,
        detail: str = None,
        instance: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create RFC 7807 problem detail response"""
        problem = {
            "type": f"https://oneflow.ai/errors/{type_}",
            "title": title,
            "status": status,
        }
        if detail:
            problem["detail"] = detail
        if instance:
            problem["instance"] = instance
        problem.update(kwargs)
        return problem


# ============================================================================
# Lifespan Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Application starting up", service="oneflow-api")
    yield
    # Shutdown
    logger.info("Application shutting down", service="oneflow-api")


# ============================================================================
# Application Factory
# ============================================================================

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="OneFlow.AI API",
        description="Multi-provider AI orchestration API with versioning",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # ========================================================================
    # CORS Middleware
    # ========================================================================
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8000",
            "https://*.oneflow.ai",  # Production domains
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )
    
    # ========================================================================
    # Request ID and Logging Middleware
    # ========================================================================
    
    @app.middleware("http")
    async def add_request_id_and_logging(request: Request, call_next):
        """Add request ID and structured logging"""
        import uuid
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        start_time = time.time()
        
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None
        )
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        logger.info(
            "Request completed",
            request_id=request_id,
            status_code=response.status_code,
            process_time_ms=f"{process_time:.2f}"
        )
        
        return response
    
    # ========================================================================
    # Error Handlers (RFC 7807)
    # ========================================================================
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions with RFC 7807 format"""
        request_id = getattr(request.state, "request_id", None)
        
        problem = ProblemDetail.create(
            type_="http-error",
            title=exc.detail,
            status=exc.status_code,
            instance=request.url.path,
            request_id=request_id
        )
        
        logger.error(
            "HTTP exception",
            request_id=request_id,
            status_code=exc.status_code,
            detail=exc.detail
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=problem,
            headers={"Content-Type": "application/problem+json"}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with RFC 7807 format"""
        request_id = getattr(request.state, "request_id", None)
        
        problem = ProblemDetail.create(
            type_="validation-error",
            title="Request Validation Error",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The request contains invalid parameters",
            instance=request.url.path,
            request_id=request_id,
            errors=exc.errors()
        )
        
        logger.error(
            "Validation error",
            request_id=request_id,
            errors=exc.errors()
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=problem,
            headers={"Content-Type": "application/problem+json"}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with RFC 7807 format"""
        request_id = getattr(request.state, "request_id", None)
        
        problem = ProblemDetail.create(
            type_="internal-error",
            title="Internal Server Error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
            instance=request.url.path,
            request_id=request_id
        )
        
        logger.error(
            "Internal server error",
            request_id=request_id,
            error=str(exc),
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=problem,
            headers={"Content-Type": "application/problem+json"}
        )
    
    # ========================================================================
    # Health Check Endpoints
    # ========================================================================
    
    @app.get("/healthz", tags=["Health"])
    async def healthz():
        """
        Kubernetes health check endpoint
        Returns 200 if service is healthy
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "oneflow-api"
        }
    
    @app.get("/livez", tags=["Health"])
    async def livez():
        """
        Kubernetes liveness probe endpoint
        Returns 200 if service is alive
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/readyz", tags=["Health"])
    async def readyz():
        """
        Kubernetes readiness probe endpoint
        Returns 200 if service is ready to accept traffic
        """
        # Add checks for dependencies (database, redis, etc.)
        dependencies_ready = True  # Replace with actual checks
        
        if not dependencies_ready:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not ready",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ========================================================================
    # Root and Version Info Endpoints
    # ========================================================================
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information"""
        return {
            "service": "OneFlow.AI API",
            "version": "2.0.0",
            "current_version": "v2",
            "supported_versions": APIVersionRegistry.get_all_versions(),
            "documentation": {
                "swagger": "/api/docs",
                "redoc": "/api/redoc",
                "openapi": "/api/openapi.json"
            },
            "health": {
                "health_check": "/healthz",
                "liveness": "/livez",
                "readiness": "/readyz"
            }
        }
    
    @app.get("/api/versions", tags=["Versions"])
    async def get_versions():
        """List all available API versions"""
        return {
            "current_version": "v2",
            "supported_versions": APIVersionRegistry.get_all_versions(),
            "documentation": {
                "v1": "/api/v1/docs",
                "v2": "/api/v2/docs"
            }
        }
    
    # ========================================================================
    # Include Versioned Routers
    # ========================================================================
    
    app.include_router(v1_router)
    app.include_router(v2_router)
    
    return app


# Create application instance
app = create_app()
