"""
OneFlow.AI - Authentication Module
Модуль аутентификации OneFlow.AI

Complete JWT-based authentication system with user management.
Полная система аутентификации на основе JWT с управлением пользователями.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import jwt
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


@dataclass
class User:
    """User data model."""
    id: int
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    api_key: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'api_key': self.api_key,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PasswordHasher:
    """
    Password hashing utilities.
    Утилиты для хеширования паролей.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password.
        Хешировать пароль.
        
        Args:
            password: Plain text password.
        
        Returns:
            str: Hashed password.
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        Проверить пароль против хеша.
        
        Args:
            plain_password: Plain text password.
            hashed_password: Hashed password.
        
        Returns:
            bool: True if password matches.
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def is_password_strong(password: str) -> tuple[bool, Optional[str]]:
        """
        Check if password meets strength requirements.
        Проверить соответствие пароля требованиям.
        
        Args:
            password: Password to check.
        
        Returns:
            tuple: (is_strong, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
        
        return True, None


class TokenManager:
    """
    JWT token management.
    Управление JWT токенами.
    """
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.
        Создать JWT токен доступа.
        
        Args:
            data: Data to encode in token.
            expires_delta: Token expiration time.
        
        Returns:
            str: Encoded JWT token.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Create JWT refresh token.
        Создать refresh токен.
        
        Args:
            data: Data to encode in token.
        
        Returns:
            str: Encoded JWT refresh token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.
        Проверить и декодировать JWT токен.
        
        Args:
            token: JWT token to verify.
            token_type: Expected token type ('access' or 'refresh').
        
        Returns:
            dict: Decoded token data, or None if invalid.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for inspection).
        Декодировать токен без проверки (для инспекции).
        
        Args:
            token: JWT token.
        
        Returns:
            dict: Decoded payload or None.
        """
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        except:
            return None


class APIKeyManager:
    """
    API key management for users.
    Управление API ключами пользователей.
    """
    
    @staticmethod
    def generate_api_key(user_id: int, prefix: str = "ofai") -> str:
        """
        Generate unique API key.
        Сгенерировать уникальный API ключ.
        
        Args:
            user_id: User ID.
            prefix: Key prefix.
        
        Returns:
            str: Generated API key.
        """
        # Format: ofai_<user_id>_<random_32_chars>
        random_part = secrets.token_hex(16)
        api_key = f"{prefix}_{user_id}_{random_part}"
        return api_key
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash API key for storage.
        Хешировать API ключ для хранения.
        
        Args:
            api_key: API key to hash.
        
        Returns:
            str: Hashed API key.
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str) -> bool:
        """
        Verify API key against hash.
        Проверить API ключ против хеша.
        
        Args:
            api_key: API key to verify.
            hashed_key: Stored hashed key.
        
        Returns:
            bool: True if key matches.
        """
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed_key
    
    @staticmethod
    def parse_api_key(api_key: str) -> Optional[Dict[str, Any]]:
        """
        Parse API key to extract information.
        Распарсить API ключ для извлечения информации.
        
        Args:
            api_key: API key.
        
        Returns:
            dict: Parsed information or None.
        """
        try:
            parts = api_key.split('_')
            if len(parts) != 3:
                return None
            
            return {
                'prefix': parts[0],
                'user_id': int(parts[1]),
                'random': parts[2]
            }
        except:
            return None


class AuthenticationService:
    """
    Main authentication service.
    Основной сервис аутентификации.
    """
    
    def __init__(self):
        """Initialize authentication service."""
        self.password_hasher = PasswordHasher()
        self.token_manager = TokenManager()
        self.api_key_manager = APIKeyManager()
        self.users_db = {}  # In-memory storage (replace with real DB)
        self.next_user_id = 1
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> tuple[Optional[User], Optional[str]]:
        """
        Register new user.
        Зарегистрировать нового пользователя.
        
        Args:
            username: Username.
            email: Email address.
            password: Password.
            full_name: Full name (optional).
        
        Returns:
            tuple: (User, error_message)
        """
        # Validate password strength
        is_strong, error = self.password_hasher.is_password_strong(password)
        if not is_strong:
            return None, error
        
        # Check if username exists
        if any(u.username == username for u in self.users_db.values()):
            return None, "Username already exists"
        
        # Check if email exists
        if any(u.email == email for u in self.users_db.values()):
            return None, "Email already exists"
        
        # Create user
        user_id = self.next_user_id
        self.next_user_id += 1
        
        hashed_password = self.password_hasher.hash_password(password)
        api_key = self.api_key_manager.generate_api_key(user_id)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            api_key=api_key
        )
        
        self.users_db[user_id] = user
        return user, None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        Аутентифицировать пользователя по имени и паролю.
        
        Args:
            username: Username.
            password: Password.
        
        Returns:
            User: User object if authenticated, None otherwise.
        """
        # Find user by username
        user = None
        for u in self.users_db.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return None
        
        # Verify password
        if not self.password_hasher.verify_password(password, user.hashed_password):
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        return user
    
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Login user and generate tokens.
        Войти в систему и сгенерировать токены.
        
        Args:
            username: Username.
            password: Password.
        
        Returns:
            dict: Token data or None if authentication failed.
        """
        user = self.authenticate_user(username, password)
        
        if not user:
            return None
        
        # Create tokens
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        }
        
        access_token = self.token_manager.create_access_token(token_data)
        refresh_token = self.token_manager.create_refresh_token({"sub": user.username, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user.to_dict()
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token.
        Обновить токен доступа используя refresh токен.
        
        Args:
            refresh_token: Refresh token.
        
        Returns:
            dict: New token data or None.
        """
        payload = self.token_manager.verify_token(refresh_token, token_type="refresh")
        
        if not payload:
            return None
        
        # Get user
        user_id = payload.get("user_id")
        user = self.users_db.get(user_id)
        
        if not user or not user.is_active:
            return None
        
        # Create new access token
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        }
        
        access_token = self.token_manager.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def verify_access_token(self, token: str) -> Optional[User]:
        """
        Verify access token and return user.
        Проверить токен доступа и вернуть пользователя.
        
        Args:
            token: Access token.
        
        Returns:
            User: User object or None.
        """
        payload = self.token_manager.verify_token(token, token_type="access")
        
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        return self.users_db.get(user_id)
    
    def verify_api_key(self, api_key: str) -> Optional[User]:
        """
        Verify API key and return user.
        Проверить API ключ и вернуть пользователя.
        
        Args:
            api_key: API key.
        
        Returns:
            User: User object or None.
        """
        # Find user by API key
        for user in self.users_db.values():
            if user.api_key == api_key and user.is_active:
                return user
        
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.users_db.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users_db.values():
            if user.username == username:
                return user
        return None
    
    def update_user(self, user_id: int, **updates) -> Optional[User]:
        """
        Update user information.
        Обновить информацию пользователя.
        
        Args:
            user_id: User ID.
            **updates: Fields to update.
        
        Returns:
            User: Updated user or None.
        """
        user = self.users_db.get(user_id)
        
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['full_name', 'email', 'is_active']
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> tuple[bool, Optional[str]]:
        """
        Change user password.
        Изменить пароль пользователя.
        
        Args:
            user_id: User ID.
            old_password: Current password.
            new_password: New password.
        
        Returns:
            tuple: (success, error_message)
        """
        user = self.users_db.get(user_id)
        
        if not user:
            return False, "User not found"
        
        # Verify old password
        if not self.password_hasher.verify_password(old_password, user.hashed_password):
            return False, "Invalid current password"
        
        # Check new password strength
        is_strong, error = self.password_hasher.is_password_strong(new_password)
        if not is_strong:
            return False, error
        
        # Update password
        user.hashed_password = self.password_hasher.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        return True, None
    
    def regenerate_api_key(self, user_id: int) -> Optional[str]:
        """
        Regenerate API key for user.
        Перегенерировать API ключ для пользователя.
        
        Args:
            user_id: User ID.
        
        Returns:
            str: New API key or None.
        """
        user = self.users_db.get(user_id)
        
        if not user:
            return None
        
        new_api_key = self.api_key_manager.generate_api_key(user_id)
        user.api_key = new_api_key
        user.updated_at = datetime.utcnow()
        
        return new_api_key


# Global instance
_auth_service = None


def get_auth_service() -> AuthenticationService:
    """
    Get global authentication service instance.
    Получить глобальный экземпляр сервиса аутентификации.
    
    Returns:
        AuthenticationService: Global auth service.
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService()
    return _auth_service


def reset_auth_service():
    """Reset global authentication service."""
    global _auth_service
    _auth_service = None


# Demo
if __name__ == '__main__':
    print("=" * 60)
    print("OneFlow.AI Authentication Module - Demo")
    print("=" * 60)
    
    auth = get_auth_service()
    
    # Register user
    print("\n1. Registering user...")
    user, error = auth.register_user(
        username="john_doe",
        email="john@example.com",
        password="SecurePass123!",
        full_name="John Doe"
    )
    
    if user:
        print(f"✓ User registered: {user.username}")
        print(f"  API Key: {user.api_key}")
    else:
        print(f"✗ Registration failed: {error}")
    
    # Login
    print("\n2. Logging in...")
    token_data = auth.login("john_doe", "SecurePass123!")
    
    if token_data:
        print(f"✓ Login successful")
        print(f"  Access Token: {token_data['access_token'][:50]}...")
        print(f"  Refresh Token: {token_data['refresh_token'][:50]}...")
    else:
        print("✗ Login failed")
    
    # Verify token
    print("\n3. Verifying access token...")
    verified_user = auth.verify_access_token(token_data['access_token'])
    
    if verified_user:
        print(f"✓ Token valid for user: {verified_user.username}")
    else:
        print("✗ Token invalid")
    
    print("\n" + "=" * 60)
    print("✓ Demo completed!")
    print("=" * 60)
