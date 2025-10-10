"""
Role-Based Access Control (RBAC)
Ролевая модель доступа с детальными разрешениями
"""

from enum import Enum
from typing import List, Optional, Set
from functools import wraps
from fastapi import HTTPException, Depends, status

from src.observability.structured_logging import get_logger

log = get_logger(__name__)


# ============================================================================
# ROLES AND PERMISSIONS
# ============================================================================

class Role(Enum):
    """Роли пользователей"""
    SUPER_ADMIN = "super_admin"     # Полный доступ ко всему
    ADMIN = "admin"                 # Управление организацией
    DEVELOPER = "developer"         # Разработка и интеграция
    USER = "user"                   # Обычный пользователь
    VIEWER = "viewer"               # Только чтение
    API_CLIENT = "api_client"       # API клиент (машина-машина)


class Permission(Enum):
    """Детальные разрешения"""
    # Управление пользователями
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Управление API ключами
    API_KEY_CREATE = "api_key:create"
    API_KEY_READ = "api_key:read"
    API_KEY_REVOKE = "api_key:revoke"
    API_KEY_ROTATE = "api_key:rotate"
    API_KEY_LIST = "api_key:list"
    
    # AI запросы
    AI_REQUEST_EXECUTE = "ai:request:execute"
    AI_REQUEST_READ = "ai:request:read"
    AI_REQUEST_LIST = "ai:request:list"
    
    # Управление провайдерами
    PROVIDER_CONFIG_READ = "provider:config:read"
    PROVIDER_CONFIG_UPDATE = "provider:config:update"
    PROVIDER_STATS_READ = "provider:stats:read"
    
    # Управление бюджетом
    BUDGET_READ = "budget:read"
    BUDGET_UPDATE = "budget:update"
    BUDGET_ADMIN = "budget:admin"
    
    # Wallet
    WALLET_READ = "wallet:read"
    WALLET_TOPUP = "wallet:topup"
    WALLET_TRANSFER = "wallet:transfer"
    WALLET_ADMIN = "wallet:admin"
    
    # Аналитика
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_ADMIN = "analytics:admin"
    
    # Настройки системы
    SYSTEM_CONFIG_READ = "system:config:read"
    SYSTEM_CONFIG_UPDATE = "system:config:update"
    SYSTEM_MONITORING = "system:monitoring"
    
    # Административные операции
    ADMIN_AUDIT_LOG = "admin:audit_log"
    ADMIN_METRICS = "admin:metrics"
    ADMIN_HEALTH_CHECK = "admin:health_check"


# ============================================================================
# ROLE PERMISSIONS MAPPING
# ============================================================================

ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),  # Все разрешения
    
    Role.ADMIN: {
        # Пользователи
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.USER_LIST,
        # API ключи
        Permission.API_KEY_CREATE,
        Permission.API_KEY_READ,
        Permission.API_KEY_REVOKE,
        Permission.API_KEY_ROTATE,
        Permission.API_KEY_LIST,
        # AI запросы
        Permission.AI_REQUEST_EXECUTE,
        Permission.AI_REQUEST_READ,
        Permission.AI_REQUEST_LIST,
        # Провайдеры
        Permission.PROVIDER_CONFIG_READ,
        Permission.PROVIDER_CONFIG_UPDATE,
        Permission.PROVIDER_STATS_READ,
        # Бюджет
        Permission.BUDGET_READ,
        Permission.BUDGET_UPDATE,
        Permission.BUDGET_ADMIN,
        # Wallet
        Permission.WALLET_READ,
        Permission.WALLET_TOPUP,
        Permission.WALLET_TRANSFER,
        Permission.WALLET_ADMIN,
        # Аналитика
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXPORT,
        Permission.ANALYTICS_ADMIN,
        # Система
        Permission.SYSTEM_CONFIG_READ,
        Permission.SYSTEM_MONITORING,
        Permission.ADMIN_AUDIT_LOG,
        Permission.ADMIN_METRICS,
        Permission.ADMIN_HEALTH_CHECK,
    },
    
    Role.DEVELOPER: {
        # API ключи (свои)
        Permission.API_KEY_CREATE,
        Permission.API_KEY_READ,
        Permission.API_KEY_REVOKE,
        Permission.API_KEY_ROTATE,
        Permission.API_KEY_LIST,
        # AI запросы
        Permission.AI_REQUEST_EXECUTE,
        Permission.AI_REQUEST_READ,
        Permission.AI_REQUEST_LIST,
        # Провайдеры (только чтение)
        Permission.PROVIDER_CONFIG_READ,
        Permission.PROVIDER_STATS_READ,
        # Бюджет (свой)
        Permission.BUDGET_READ,
        Permission.BUDGET_UPDATE,
        # Wallet (свой)
        Permission.WALLET_READ,
        Permission.WALLET_TOPUP,
        # Аналитика (своя)
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXPORT,
        # Система (только чтение)
        Permission.SYSTEM_CONFIG_READ,
        Permission.ADMIN_HEALTH_CHECK,
    },
    
    Role.USER: {
        # API ключи (свои)
        Permission.API_KEY_READ,
        Permission.API_KEY_LIST,
        # AI запросы
        Permission.AI_REQUEST_EXECUTE,
        Permission.AI_REQUEST_READ,
        Permission.AI_REQUEST_LIST,
        # Провайдеры (только чтение)
        Permission.PROVIDER_CONFIG_READ,
        Permission.PROVIDER_STATS_READ,
        # Бюджет (свой)
        Permission.BUDGET_READ,
        # Wallet (свой)
        Permission.WALLET_READ,
        Permission.WALLET_TOPUP,
        # Аналитика (своя)
        Permission.ANALYTICS_READ,
    },
    
    Role.VIEWER: {
        # Только чтение
        Permission.USER_READ,
        Permission.API_KEY_READ,
        Permission.AI_REQUEST_READ,
        Permission.AI_REQUEST_LIST,
        Permission.PROVIDER_CONFIG_READ,
        Permission.PROVIDER_STATS_READ,
        Permission.BUDGET_READ,
        Permission.WALLET_READ,
        Permission.ANALYTICS_READ,
        Permission.SYSTEM_CONFIG_READ,
    },
    
    Role.API_CLIENT: {
        # Только выполнение AI запросов
        Permission.AI_REQUEST_EXECUTE,
        Permission.AI_REQUEST_READ,
        Permission.PROVIDER_STATS_READ,
    },
}


# ============================================================================
# RBAC MANAGER
# ============================================================================

class RBACManager:
    """Менеджер RBAC"""
    
    @staticmethod
    def get_role_permissions(role: Role) -> Set[Permission]:
        """Получить разрешения роли"""
        return ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def has_permission(role: Role, permission: Permission) -> bool:
        """Проверить, есть ли у роли разрешение"""
        return permission in ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def has_any_permission(role: Role, permissions: List[Permission]) -> bool:
        """Проверить, есть ли у роли хотя бы одно из разрешений"""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return any(perm in role_perms for perm in permissions)
    
    @staticmethod
    def has_all_permissions(role: Role, permissions: List[Permission]) -> bool:
        """Проверить, есть ли у роли все разрешения"""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return all(perm in role_perms for perm in permissions)
    
    @staticmethod
    def check_resource_access(
        role: Role,
        resource_owner_id: str,
        current_user_id: str,
        permission: Permission
    ) -> bool:
        """
        Проверить доступ к ресурсу с учётом владения
        
        Args:
            role: Роль пользователя
            resource_owner_id: ID владельца ресурса
            current_user_id: ID текущего пользователя
            permission: Требуемое разрешение
        
        Returns:
            True если доступ разрешён
        """
        # Проверить наличие разрешения
        if not RBACManager.has_permission(role, permission):
            return False
        
        # Admin и Super Admin имеют доступ ко всему
        if role in [Role.SUPER_ADMIN, Role.ADMIN]:
            return True
        
        # Пользователь имеет доступ только к своим ресурсам
        return resource_owner_id == current_user_id


# ============================================================================
# DECORATORS ДЛЯ FASTAPI
# ============================================================================

def require_permission(permission: Permission):
    """
    Декоратор для проверки разрешения
    
    Usage:
        @app.get("/api/users")
        @require_permission(Permission.USER_LIST)
        async def list_users(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = Role(current_user.role)
            
            if not RBACManager.has_permission(user_role, permission):
                log.warning(
                    "permission_denied",
                    user_id=current_user.id,
                    role=user_role.value,
                    required_permission=permission.value,
                    endpoint=func.__name__
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission {permission.value} required"
                )
            
            log.debug(
                "permission_granted",
                user_id=current_user.id,
                role=user_role.value,
                permission=permission.value,
                endpoint=func.__name__
            )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(permissions: List[Permission]):
    """
    Декоратор для проверки хотя бы одного из разрешений
    
    Usage:
        @app.get("/api/stats")
        @require_any_permission([Permission.ANALYTICS_READ, Permission.ADMIN_METRICS])
        async def get_stats(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = Role(current_user.role)
            
            if not RBACManager.has_any_permission(user_role, permissions):
                log.warning(
                    "permission_denied",
                    user_id=current_user.id,
                    role=user_role.value,
                    required_permissions=[p.value for p in permissions],
                    endpoint=func.__name__
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of permissions {[p.value for p in permissions]} required"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Декоратор для проверки роли
    
    Usage:
        @app.post("/api/admin/config")
        @require_role(Role.ADMIN)
        async def update_config(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = Role(current_user.role)
            
            if user_role != role and user_role != Role.SUPER_ADMIN:
                log.warning(
                    "role_denied",
                    user_id=current_user.id,
                    current_role=user_role.value,
                    required_role=role.value,
                    endpoint=func.__name__
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role {role.value} required"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def require_resource_owner(resource_id_param: str = "resource_id"):
    """
    Декоратор для проверки владения ресурсом
    
    Usage:
        @app.get("/api/users/{user_id}/profile")
        @require_resource_owner("user_id")
        async def get_profile(
            user_id: str,
            current_user: User = Depends(get_current_user)
        ):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = Role(current_user.role)
            resource_owner_id = kwargs.get(resource_id_param)
            
            # Admin и Super Admin имеют доступ ко всему
            if user_role in [Role.SUPER_ADMIN, Role.ADMIN]:
                return await func(*args, current_user=current_user, **kwargs)
            
            # Проверить владение
            if resource_owner_id != current_user.id:
                log.warning(
                    "resource_access_denied",
                    user_id=current_user.id,
                    resource_owner=resource_owner_id,
                    endpoint=func.__name__
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access to this resource is denied"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator
