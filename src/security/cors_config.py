"""
CORS и заголовки безопасности
Строгая конфигурация для production
"""

from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.observability.structured_logging import get_logger

log = get_logger(__name__)


# ============================================================================
# CORS CONFIGURATION
# ============================================================================

class CORSConfig:
    """Конфигурация CORS"""
    
    # Production: только доверенные origins
    PRODUCTION_ORIGINS = [
        "https://oneflow.ai",
        "https://www.oneflow.ai",
        "https://app.oneflow.ai",
        "https://api.oneflow.ai",
    ]
    
    # Development: localhost
    DEVELOPMENT_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Разрешённые методы
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    
    # Разрешённые заголовки
    ALLOWED_HEADERS = [
        "Authorization",
        "Content-Type",
        "X-API-Key",
        "X-Request-ID",
        "X-Correlation-ID",
    ]
    
    # Exposed headers (доступны для чтения из браузера)
    EXPOSE_HEADERS = [
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]
    
    @staticmethod
    def get_origins(environment: str = "production") -> List[str]:
        """Получить разрешённые origins для окружения"""
        if environment == "development":
            return CORSConfig.DEVELOPMENT_ORIGINS + CORSConfig.PRODUCTION_ORIGINS
        elif environment == "staging":
            return [
                "https://staging.oneflow.ai",
                "https://staging-app.oneflow.ai",
            ] + CORSConfig.DEVELOPMENT_ORIGINS
        else:  # production
            return CORSConfig.PRODUCTION_ORIGINS


def configure_cors(app: FastAPI, environment: str = "production"):
    """
    Настроить CORS middleware
    
    Args:
        app: FastAPI приложение
        environment: Окружение (development, staging, production)
    """
    origins = CORSConfig.get_origins(environment)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=CORSConfig.ALLOWED_METHODS,
        allow_headers=CORSConfig.ALLOWED_HEADERS,
        expose_headers=CORSConfig.EXPOSE_HEADERS,
        max_age=86400,  # 24 hours
    )
    
    log.info(
        "cors_configured",
        environment=environment,
        allowed_origins_count=len(origins),
        allow_credentials=True
    )


# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления заголовков безопасности"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openai.com https://api.anthropic.com; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security (HTTPS only)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # Remove Server header
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Remove X-Powered-By header
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        
        return response


def configure_security_headers(app: FastAPI):
    """
    Настроить security headers middleware
    
    Args:
        app: FastAPI приложение
    """
    app.add_middleware(SecurityHeadersMiddleware)
    
    log.info("security_headers_configured")


# ============================================================================
# PAYLOAD SIZE LIMITER MIDDLEWARE
# ============================================================================

class PayloadSizeLimiter(BaseHTTPMiddleware):
    """Middleware для ограничения размера payload"""
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        # Проверить Content-Length
        content_length = request.headers.get("Content-Length")
        
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                log.warning(
                    "payload_size_exceeded",
                    content_length=content_length,
                    max_size=self.max_size,
                    path=request.url.path
                )
                
                return Response(
                    content=f"Request payload too large. Maximum size: {self.max_size} bytes",
                    status_code=413,
                    headers={"Content-Type": "text/plain"}
                )
        
        response = await call_next(request)
        return response


def configure_payload_limiter(
    app: FastAPI,
    max_size: int = 10 * 1024 * 1024  # 10MB
):
    """
    Настроить payload size limiter
    
    Args:
        app: FastAPI приложение
        max_size: Максимальный размер payload в байтах
    """
    app.add_middleware(PayloadSizeLimiter, max_size=max_size)
    
    log.info(
        "payload_limiter_configured",
        max_size_bytes=max_size,
        max_size_mb=max_size / (1024 * 1024)
    )


# ============================================================================
# REQUEST ID MIDDLEWARE
# ============================================================================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления Request ID"""
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        
        # Получить или сгенерировать Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Добавить в state для использования в handlers
        request.state.request_id = request_id
        
        # Выполнить запрос
        response = await call_next(request)
        
        # Добавить Request ID в response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


def configure_request_id(app: FastAPI):
    """
    Настроить Request ID middleware
    
    Args:
        app: FastAPI приложение
    """
    app.add_middleware(RequestIDMiddleware)
    
    log.info("request_id_middleware_configured")


# ============================================================================
# UNIFIED SECURITY CONFIGURATION
# ============================================================================

def configure_security(
    app: FastAPI,
    environment: str = "production",
    max_payload_size: int = 10 * 1024 * 1024
):
    """
    Единая функция для настройки всех аспектов безопасности
    
    Args:
        app: FastAPI приложение
        environment: Окружение (development, staging, production)
        max_payload_size: Максимальный размер payload
    """
    # CORS
    configure_cors(app, environment)
    
    # Security headers
    configure_security_headers(app)
    
    # Payload size limiter
    configure_payload_limiter(app, max_payload_size)
    
    # Request ID
    configure_request_id(app)
    
    log.info(
        "security_fully_configured",
        environment=environment,
        max_payload_size_mb=max_payload_size / (1024 * 1024)
    )
