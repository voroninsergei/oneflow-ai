"""
OneFlow.AI - Security Middleware for FastAPI
Middleware безопасности для FastAPI

Complete security layer with JWT and API key authentication.
Полный слой безопасности с JWT и API key аутентификацией.
"""

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Optional
import logging

from auth_module import get_auth_service, User

logger = logging.getLogger(__name__)

# Security schemes
bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class SecurityMiddleware:
    """
    Security middleware for FastAPI.
    Middleware безопасности для FastAPI.
    """
    
    def __init__(self):
        """Initialize security middleware."""
        self.auth_service = get_auth_service()
    
    async def get_current_user_from_token(
        self,
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
    ) -> User:
        """
        Get current user from JWT token.
        Получить текущего пользователя из JWT токена.
        
        Args:
            credentials: Bearer token credentials.
        
        Returns:
            User: Authenticated user.
        
        Raises:
            HTTPException: If authentication fails.
        """
        token = credentials.credentials
        
        user = self.auth_service.verify_access_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    
    async def get_current_user_from_api_key(
        self,
        api_key: Optional[str] = Security(api_key_header)
    ) -> User:
        """
        Get current user from API key.
        Получить текущего пользователя из API ключа.
        
        Args:
            api_key: API key from header.
        
        Returns:
            User: Authenticated user.
        
        Raises:
            HTTPException: If authentication fails.
        """
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        user = self.auth_service.verify_api_key(api_key)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    
    async def get_current_user(
        self,
        token_user: Optional[User] = Depends(get_current_user_from_token),
        api_key_user: Optional[User] = Depends(get_current_user_from_api_key)
    ) -> User:
        """
        Get current user from either JWT token or API key.
        Получить текущего пользователя из JWT токена или API ключа.
        
        Args:
            token_user: User from JWT token.
            api_key_user: User from API key.
        
        Returns:
            User: Authenticated user.
        
        Raises:
            HTTPException: If authentication fails.
        """
        # Try JWT token first
        try:
            credentials = bearer_scheme()
            if credentials:
                return await self.get_current_user_from_token(credentials)
        except:
            pass
        
        # Try API key
        try:
            api_key = api_key_header()
            if api_key:
                return await self.get_current_user_from_api_key(api_key)
        except:
            pass
        
        # No valid authentication
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide JWT token or API key.",
            headers={"WWW-Authenticate": "Bearer, ApiKey"},
        )
    
    async def get_current_active_user(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Get current active user.
        Получить текущего активного пользователя.
        
        Args:
            current_user: Current user from authentication.
        
        Returns:
            User: Active user.
        
        Raises:
            HTTPException: If user is inactive.
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        return current_user
    
    async def get_current_admin_user(
        self,
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """
        Get current admin user.
        Получить текущего администратора.
        
        Args:
            current_user: Current active user.
        
        Returns:
            User: Admin user.
        
        Raises:
            HTTPException: If user is not admin.
        """
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return current_user


# Rate limiting middleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple


class RateLimitMiddleware:
    """
    Rate limiting middleware.
    Middleware для ограничения частоты запросов.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute.
            requests_per_hour: Maximum requests per hour.
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.user_requests: Dict[int, list] = defaultdict(list)
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limit.
        Проверить превышен ли лимит запросов пользователем.
        
        Args:
            user_id: User ID.
        
        Returns:
            tuple: (is_allowed, error_message)
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Get user's requests
        requests = self.user_requests[user_id]
        
        # Remove old requests
        requests = [req_time for req_time in requests if req_time > hour_ago]
        self.user_requests[user_id] = requests
        
        # Check minute limit
        recent_requests = [req_time for req_time in requests if req_time > minute_ago]
        if len(recent_requests) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        
        # Check hour limit
        if len(requests) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
        
        # Add current request
        requests.append(now)
        
        return True, None
    
    def get_rate_limit_status(self, user_id: int) -> Dict[str, int]:
        """
        Get rate limit status for user.
        Получить статус лимита для пользователя.
        
        Args:
            user_id: User ID.
        
        Returns:
            dict: Rate limit status.
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        requests = self.user_requests[user_id]
        
        recent_requests = [req for req in requests if req > minute_ago]
        hour_requests = [req for req in requests if req > hour_ago]
        
        return {
            'requests_last_minute': len(recent_requests),
            'requests_last_hour': len(hour_requests),
            'minute_limit': self.requests_per_minute,
            'hour_limit': self.requests_per_hour,
            'minute_remaining': self.requests_per_minute - len(recent_requests),
            'hour_remaining': self.requests_per_hour - len(hour_requests)
        }


# Permission checker
class PermissionChecker:
    """
    Permission checking utilities.
    Утилиты проверки прав доступа.
    """
    
    @staticmethod
    def require_permission(user: User, permission: str) -> bool:
        """
        Check if user has specific permission.
        Проверить есть ли у пользователя конкретное право.
        
        Args:
            user: User to check.
            permission: Permission name.
        
        Returns:
            bool: True if user has permission.
        """
        # Admin has all permissions
        if user.is_admin:
            return True
        
        # Add custom permission logic here
        # For now, basic users have limited permissions
        basic_permissions = [
            'read:own_data',
            'write:own_data',
            'use:api'
        ]
        
        return permission in basic_permissions
    
    @staticmethod
    def require_admin(user: User):
        """
        Require admin privileges.
        Требовать права администратора.
        
        Args:
            user: User to check.
        
        Raises:
            HTTPException: If user is not admin.
        """
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )


# Global instances
_security_middleware = None
_rate_limit_middleware = None


def get_security_middleware() -> SecurityMiddleware:
    """Get global security middleware instance."""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityMiddleware()
    return _security_middleware


def get_rate_limit_middleware() -> RateLimitMiddleware:
    """Get global rate limit middleware instance."""
    global _rate_limit_middleware
    if _rate_limit_middleware is None:
        _rate_limit_middleware = RateLimitMiddleware()
    return _rate_limit_middleware


# Dependency functions for FastAPI
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> User:
    """
    FastAPI dependency to get current user from JWT token.
    
    Usage in FastAPI route:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user": user.username}
    """
    middleware = get_security_middleware()
    return await middleware.get_current_user_from_token(credentials)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> Optional[User]:
    """
    FastAPI dependency to get current user (optional).
    Returns None if no authentication provided.
    """
    if not credentials:
        return None
    
    try:
        middleware = get_security_middleware()
        return await middleware.get_current_user_from_token(credentials)
    except HTTPException:
        return None


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency to get current admin user.
    
    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: int,
            admin: User = Depends(get_current_admin)
        ):
            # Only admins can access this
            pass
    """
    middleware = get_security_middleware()
    return await middleware.get_current_admin_user(current_user)


async def check_rate_limit(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency to check rate limits.
    
    Usage:
        @app.post("/api/request")
        async def make_request(
            user: User = Depends(check_rate_limit)
        ):
            # Rate limit checked automatically
            pass
    """
    rate_limiter = get_rate_limit_middleware()
    is_allowed, error = rate_limiter.check_rate_limit(current_user.id)
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error
        )
    
    return current_user


# Example FastAPI integration
from fastapi import FastAPI, Body
from pydantic import BaseModel, EmailStr

app = FastAPI(title="OneFlow.AI Secured API")


# Request/Response models
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool


# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register new user.
    Зарегистрировать нового пользователя.
    """
    auth = get_auth_service()
    
    user, error = auth.register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return user.to_dict()


@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login and get JWT tokens.
    Войти и получить JWT токены.
    """
    auth = get_auth_service()
    
    token_data = auth.login(request.username, request.password)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


@app.post("/auth/refresh", response_model=dict)
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    """
    Refresh access token.
    Обновить токен доступа.
    """
    auth = get_auth_service()
    
    token_data = auth.refresh_access_token(refresh_token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return token_data


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    Получить информацию о текущем пользователе.
    """
    return current_user.to_dict()


@app.get("/auth/api-key")
async def get_api_key(current_user: User = Depends(get_current_user)):
    """
    Get user's API key.
    Получить API ключ пользователя.
    """
    return {
        "api_key": current_user.api_key,
        "user_id": current_user.id
    }


@app.post("/auth/api-key/regenerate")
async def regenerate_api_key(current_user: User = Depends(get_current_user)):
    """
    Regenerate user's API key.
    Перегенерировать API ключ пользователя.
    """
    auth = get_auth_service()
    new_api_key = auth.regenerate_api_key(current_user.id)
    
    return {
        "api_key": new_api_key,
        "message": "API key regenerated successfully"
    }


# Protected endpoints
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Protected route requiring authentication.
    Защищённый маршрут требующий аутентификации.
    """
    return {
        "message": f"Hello, {current_user.username}!",
        "user_id": current_user.id
    }


@app.get("/admin/users")
async def list_users(admin: User = Depends(get_current_admin)):
    """
    Admin-only route to list all users.
    Маршрут только для администраторов - список пользователей.
    """
    auth = get_auth_service()
    users = [user.to_dict() for user in auth.users_db.values()]
    return {"users": users}


@app.get("/rate-limit/status")
async def get_rate_limit_status(current_user: User = Depends(get_current_user)):
    """
    Get rate limit status for current user.
    Получить статус лимита для текущего пользователя.
    """
    rate_limiter = get_rate_limit_middleware()
    status = rate_limiter.get_rate_limit_status(current_user.id)
    return status


# Rate-limited endpoint
@app.post("/api/limited-request")
async def limited_request(user: User = Depends(check_rate_limit)):
    """
    Rate-limited endpoint.
    Endpoint с ограничением частоты запросов.
    """
    return {
        "message": "Request processed successfully",
        "user": user.username
    }


# Health check (no authentication required)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == '__main__':
    import uvicorn
    
    print("=" * 60)
    print("🔐 Starting Secured OneFlow.AI API")
    print("=" * 60)
    print("\nEndpoints:")
    print("  POST /auth/register     - Register new user")
    print("  POST /auth/login        - Login and get tokens")
    print("  POST /auth/refresh      - Refresh access token")
    print("  GET  /auth/me           - Get current user info")
    print("  GET  /auth/api-key      - Get API key")
    print("  POST /auth/api-key/regenerate - Regenerate API key")
    print("  GET  /protected         - Protected route")
    print("  GET  /admin/users       - Admin only")
    print("  GET  /rate-limit/status - Rate limit status")
    print("\nDocs: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)