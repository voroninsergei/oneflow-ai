"""
Authentication v2 с ротацией API ключей и улучшенной безопасностью
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass

import structlog
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class APIKey:
    """API ключ с метаданными"""
    key_id: str
    key_hash: str
    user_id: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    name: str  # Человекочитаемое имя ключа
    permissions: list[str]  # Список разрешений


@dataclass
class User:
    """Пользователь системы"""
    user_id: str
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime
    api_keys: list[APIKey]


class APIKeyManager:
    """
    Менеджер API ключей с поддержкой ротации
    """
    
    # Формат: oneflow_live_<40 символов>
    KEY_PREFIX = "oneflow_live_"
    KEY_LENGTH = 40
    
    @staticmethod
    def generate_api_key() -> Tuple[str, str]:
        """
        Генерация нового API ключа
        
        Returns:
            (plain_key, key_hash) - открытый ключ и его хэш
        """
        # Генерация криптостойкого случайного ключа
        random_part = secrets.token_urlsafe(30)[:APIKeyManager.KEY_LENGTH]
        plain_key = f"{APIKeyManager.KEY_PREFIX}{random_part}"
        
        # Хэширование ключа для хранения
        key_hash = APIKeyManager._hash_key(plain_key)
        
        logger.info(
            "api_key_generated",
            key_prefix=plain_key[:20] + "..."
        )
        
        return plain_key, key_hash
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Хэширование ключа SHA-256"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def verify_key(plain_key: str, key_hash: str) -> bool:
        """
        Проверка API ключа
        
        Args:
            plain_key: Открытый ключ от пользователя
            key_hash: Хэш из базы данных
        """
        computed_hash = APIKeyManager._hash_key(plain_key)
        return secrets.compare_digest(computed_hash, key_hash)
    
    @staticmethod
    def generate_key_id() -> str:
        """Генерация уникального ID для ключа"""
        return f"key_{secrets.token_hex(16)}"
    
    @staticmethod
    def create_api_key(
        user_id: str,
        name: str = "Default Key",
        expires_in_days: Optional[int] = None,
        permissions: Optional[list[str]] = None
    ) -> Tuple[str, APIKey]:
        """
        Создание нового API ключа для пользователя
        
        Args:
            user_id: ID пользователя
            name: Название ключа
            expires_in_days: Срок действия в днях (None = бессрочный)
            permissions: Список разрешений
        
        Returns:
            (plain_key, APIKey object)
        """
        plain_key, key_hash = APIKeyManager.generate_api_key()
        key_id = APIKeyManager.generate_key_id()
        
        now = datetime.utcnow()
        expires_at = None
        if expires_in_days:
            expires_at = now + timedelta(days=expires_in_days)
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            user_id=user_id,
            created_at=now,
            expires_at=expires_at,
            last_used_at=None,
            is_active=True,
            name=name,
            permissions=permissions or ["read", "write"]
        )
        
        logger.info(
            "api_key_created",
            user_id=user_id,
            key_id=key_id,
            name=name,
            expires_at=expires_at
        )
        
        return plain_key, api_key
    
    @staticmethod
    def rotate_key(
        old_api_key: APIKey,
        grace_period_days: int = 7
    ) -> Tuple[str, APIKey, datetime]:
        """
        Ротация API ключа с grace period
        
        Args:
            old_api_key: Старый ключ для ротации
            grace_period_days: Период, в течение которого старый ключ ещё работает
        
        Returns:
            (new_plain_key, new_APIKey, old_key_expiry_date)
        """
        # Создание нового ключа
        new_plain_key, new_api_key = APIKeyManager.create_api_key(
            user_id=old_api_key.user_id,
            name=f"{old_api_key.name} (Rotated)",
            expires_in_days=None,
            permissions=old_api_key.permissions
        )
        
        # Установка grace period для старого ключа
        old_key_expiry = datetime.utcnow() + timedelta(days=grace_period_days)
        
        logger.info(
            "api_key_rotated",
            user_id=old_api_key.user_id,
            old_key_id=old_api_key.key_id,
            new_key_id=new_api_key.key_id,
            grace_period_until=old_key_expiry
        )
        
        return new_plain_key, new_api_key, old_key_expiry
    
    @staticmethod
    def revoke_key(api_key: APIKey) -> None:
        """Немедленный отзыв API ключа"""
        api_key.is_active = False
        
        logger.warning(
            "api_key_revoked",
            key_id=api_key.key_id,
            user_id=api_key.user_id
        )
    
    @staticmethod
    def check_key_validity(api_key: APIKey) -> Tuple[bool, Optional[str]]:
        """
        Проверка валидности ключа
        
        Returns:
            (is_valid, reason_if_invalid)
        """
        if not api_key.is_active:
            return False, "Key is revoked"
        
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            return False, "Key has expired"
        
        return True, None


class JWTManager:
    """
    Менеджер JWT токенов
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(
        self,
        user_id: str,
        permissions: Optional[list[str]] = None
    ) -> str:
        """
        Создание access токена
        
        Args:
            user_id: ID пользователя
            permissions: Список разрешений
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "type": "access",
            "iat": now,
            "exp": expire,
            "permissions": permissions or []
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(
            "access_token_created",
            user_id=user_id,
            expires_at=expire
        )
        
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """Создание refresh токена"""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": expire
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(
            "refresh_token_created",
            user_id=user_id,
            expires_at=expire
        )
        
        return token
    
    def verify_token(self, token: str, expected_type: str = "access") -> Optional[dict]:
        """
        Верификация JWT токена
        
        Args:
            token: JWT токен
            expected_type: Ожидаемый тип токена (access/refresh)
        
        Returns:
            Payload токена или None если невалиден
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            if payload.get("type") != expected_type:
                logger.warning(
                    "token_type_mismatch",
                    expected=expected_type,
                    actual=payload.get("type")
                )
                return None
            
            return payload
        
        except InvalidTokenError as e:
            logger.warning("token_verification_failed", error=str(e))
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Обновление access токена используя refresh токен
        
        Returns:
            Новый access токен или None
        """
        payload = self.verify_token(refresh_token, expected_type="refresh")
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        return self.create_access_token(user_id)


class PasswordManager:
    """Менеджер паролей"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хэширование пароля"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def check_password_strength(password: str) -> Tuple[bool, list[str]]:
        """
        Проверка надёжности пароля
        
        Returns:
            (is_strong, list_of_issues)
        """
        issues = []
        
        if len(password) < 12:
            issues.append("Password must be at least 12 characters long")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain at least one special character")
        
        return len(issues) == 0, issues


# ===== Database Interface (пример) =====

class AuthDatabase:
    """
    Интерфейс для работы с БД аутентификации
    В реальности использовать SQLAlchemy или другую ORM
    """
    
    def __init__(self):
        # В продакшене: подключение к реальной БД
        self.users = {}
        self.api_keys = {}
    
    def create_user(self, email: str, password: str) -> User:
        """Создание нового пользователя"""
        user_id = f"user_{secrets.token_hex(16)}"
        password_hash = PasswordManager.hash_password(password)
        
        user = User(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
            is_active=True,
            created_at=datetime.utcnow(),
            api_keys=[]
        )
        
        self.users[user_id] = user
        
        logger.info("user_created", user_id=user_id, email=email)
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.users.get(user_id)
    
    def store_api_key(self, api_key: APIKey) -> None:
        """Сохранение API ключа"""
        self.api_keys[api_key.key_id] = api_key
        
        # Добавление ключа к пользователю
        user = self.get_user_by_id(api_key.user_id)
        if user:
            user.api_keys.append(api_key)
    
    def get_api_key_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Поиск API ключа по хэшу"""
        for api_key in self.api_keys.values():
            if api_key.key_hash == key_hash:
                return api_key
        return None
    
    def update_api_key_last_used(self, key_id: str) -> None:
        """Обновление времени последнего использования ключа"""
        if key_id in self.api_keys:
            self.api_keys[key_id].last_used_at = datetime.utcnow()


# ===== Пример использования =====

def example_usage():
    """Пример полного workflow аутентификации"""
    
    # Инициализация
    db = AuthDatabase()
    jwt_manager = JWTManager(secret_key="your-secret-key-here")
    
    # 1. Регистрация пользователя
    user = db.create_user(
        email="user@example.com",
        password="SecureP@ssw0rd123"
    )
    
    # 2. Создание API ключа
    plain_key, api_key = APIKeyManager.create_api_key(
        user_id=user.user_id,
        name="Production Key",
        expires_in_days=365
    )
    db.store_api_key(api_key)
    
    print(f"Your API Key: {plain_key}")
    print("⚠️  Save this key securely - it won't be shown again!")
    
    # 3. Проверка API ключа при запросе
    provided_key = plain_key  # От клиента
    key_hash = APIKeyManager._hash_key(provided_key)
    stored_key = db.get_api_key_by_hash(key_hash)
    
    if stored_key:
        is_valid, reason = APIKeyManager.check_key_validity(stored_key)
        if is_valid:
            print("✅ API Key is valid")
            db.update_api_key_last_used(stored_key.key_id)
        else:
            print(f"❌ API Key is invalid: {reason}")
    
    # 4. Ротация ключа
    new_key, new_api_key, old_expiry = APIKeyManager.rotate_key(api_key)
    db.store_api_key(new_api_key)
    
    print(f"\n🔄 Key rotated!")
    print(f"New API Key: {new_key}")
    print(f"Old key valid until: {old_expiry}")
    
    # 5. JWT токены для web-интерфейса
    access_token = jwt_manager.create_access_token(user.user_id)
    refresh_token = jwt_manager.create_refresh_token(user.user_id)
    
    print(f"\n🔐 JWT Tokens generated")
    print(f"Access Token: {access_token[:50]}...")


if __name__ == "__main__":
    example_usage()
