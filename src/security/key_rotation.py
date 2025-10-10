"""
Ротация и версионирование API ключей
Автоматическая ротация с grace period
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

from src.observability.structured_logging import get_logger

log = get_logger(__name__)


# ============================================================================
# KEY STATUS
# ============================================================================

class KeyStatus(Enum):
    """Статус API ключа"""
    ACTIVE = "active"           # Активен
    ROTATING = "rotating"       # В процессе ротации
    DEPRECATED = "deprecated"   # Устарел, но ещё работает (grace period)
    REVOKED = "revoked"        # Отозван
    EXPIRED = "expired"        # Истёк срок действия


@dataclass
class APIKeyVersion:
    """Версия API ключа"""
    key_id: str                      # ID ключа
    key_hash: str                    # Hash ключа (для хранения)
    version: int                     # Номер версии
    status: KeyStatus                # Статус
    created_at: datetime             # Дата создания
    expires_at: Optional[datetime]   # Дата истечения
    deprecated_at: Optional[datetime] # Дата deprecation
    revoked_at: Optional[datetime]   # Дата отзыва
    last_used_at: Optional[datetime] # Последнее использование
    usage_count: int                 # Количество использований
    metadata: Dict                   # Дополнительная информация


# ============================================================================
# KEY ROTATION MANAGER
# ============================================================================

class KeyRotationManager:
    """Менеджер ротации API ключей"""
    
    def __init__(
        self,
        rotation_period_days: int = 90,
        grace_period_days: int = 7,
        warning_period_days: int = 14
    ):
        """
        Args:
            rotation_period_days: Период ротации ключей (дни)
            grace_period_days: Grace period после deprecation (дни)
            warning_period_days: Период для предупреждения о ротации (дни)
        """
        self.rotation_period_days = rotation_period_days
        self.grace_period_days = grace_period_days
        self.warning_period_days = warning_period_days
        
        # Хранилище ключей: {key_id: [APIKeyVersion]}
        self.keys: Dict[str, List[APIKeyVersion]] = {}
    
    def generate_key(
        self,
        key_id: str,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> tuple[str, APIKeyVersion]:
        """
        Сгенерировать новый API ключ
        
        Args:
            key_id: ID ключа
            user_id: ID пользователя
            metadata: Дополнительная информация
        
        Returns:
            Tuple[raw_key, APIKeyVersion]
        """
        # Генерация случайного ключа
        raw_key = self._generate_raw_key()
        key_hash = self._hash_key(raw_key)
        
        # Версия ключа
        if key_id in self.keys:
            version = max(k.version for k in self.keys[key_id]) + 1
        else:
            version = 1
        
        # Дата истечения
        expires_at = datetime.now() + timedelta(days=self.rotation_period_days)
        
        # Создание версии
        key_version = APIKeyVersion(
            key_id=key_id,
            key_hash=key_hash,
            version=version,
            status=KeyStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=expires_at,
            deprecated_at=None,
            revoked_at=None,
            last_used_at=None,
            usage_count=0,
            metadata=metadata or {"user_id": user_id}
        )
        
        # Сохранить
        if key_id not in self.keys:
            self.keys[key_id] = []
        self.keys[key_id].append(key_version)
        
        log.info(
            "api_key_generated",
            key_id=key_id,
            version=version,
            user_id=user_id,
            expires_at=expires_at.isoformat()
        )
        
        return raw_key, key_version
    
    def rotate_key(
        self,
        key_id: str,
        user_id: str
    ) -> tuple[str, APIKeyVersion]:
        """
        Ротация ключа (создание новой версии и deprecation старой)
        
        Args:
            key_id: ID ключа
            user_id: ID пользователя
        
        Returns:
            Tuple[new_raw_key, new_key_version]
        """
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        
        # Найти текущую активную версию
        current_versions = [
            k for k in self.keys[key_id]
            if k.status == KeyStatus.ACTIVE
        ]
        
        if not current_versions:
            raise ValueError(f"No active version for key {key_id}")
        
        # Сгенерировать новую версию
        new_raw_key, new_version = self.generate_key(
            key_id=key_id,
            user_id=user_id,
            metadata={"user_id": user_id, "rotated_from_version": current_versions[0].version}
        )
        
        # Deprecate старую версию
        for old_version in current_versions:
            old_version.status = KeyStatus.DEPRECATED
            old_version.deprecated_at = datetime.now()
            old_version.expires_at = datetime.now() + timedelta(days=self.grace_period_days)
        
        log.info(
            "api_key_rotated",
            key_id=key_id,
            old_version=current_versions[0].version,
            new_version=new_version.version,
            grace_period_expires=old_version.expires_at.isoformat()
        )
        
        return new_raw_key, new_version
    
    def revoke_key(self, key_id: str, version: Optional[int] = None):
        """
        Отозвать ключ или конкретную версию
        
        Args:
            key_id: ID ключа
            version: Версия (если None, отзываются все версии)
        """
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        
        versions_to_revoke = (
            [k for k in self.keys[key_id] if k.version == version]
            if version is not None
            else self.keys[key_id]
        )
        
        for key_version in versions_to_revoke:
            key_version.status = KeyStatus.REVOKED
            key_version.revoked_at = datetime.now()
        
        log.warning(
            "api_key_revoked",
            key_id=key_id,
            versions_revoked=[k.version for k in versions_to_revoke]
        )
    
    def validate_key(self, raw_key: str) -> Optional[APIKeyVersion]:
        """
        Валидировать API ключ
        
        Args:
            raw_key: Сырой ключ
        
        Returns:
            APIKeyVersion если ключ валиден, иначе None
        """
        key_hash = self._hash_key(raw_key)
        
        # Найти ключ по hash
        for key_id, versions in self.keys.items():
            for version in versions:
                if version.key_hash == key_hash:
                    # Проверить статус и срок действия
                    if version.status in [KeyStatus.REVOKED, KeyStatus.EXPIRED]:
                        log.warning(
                            "api_key_invalid_status",
                            key_id=key_id,
                            version=version.version,
                            status=version.status.value
                        )
                        return None
                    
                    # Проверить истечение срока
                    if version.expires_at and datetime.now() > version.expires_at:
                        version.status = KeyStatus.EXPIRED
                        log.warning(
                            "api_key_expired",
                            key_id=key_id,
                            version=version.version,
                            expired_at=version.expires_at.isoformat()
                        )
                        return None
                    
                    # Обновить метрики использования
                    version.last_used_at = datetime.now()
                    version.usage_count += 1
                    
                    # Предупреждение о скором истечении
                    if version.expires_at:
                        days_until_expiry = (version.expires_at - datetime.now()).days
                        if days_until_expiry <= self.warning_period_days:
                            log.warning(
                                "api_key_expiring_soon",
                                key_id=key_id,
                                version=version.version,
                                days_until_expiry=days_until_expiry
                            )
                    
                    return version
        
        log.warning("api_key_not_found")
        return None
    
    def get_key_info(self, key_id: str) -> List[APIKeyVersion]:
        """Получить информацию о всех версиях ключа"""
        return self.keys.get(key_id, [])
    
    def get_keys_requiring_rotation(self) -> List[tuple[str, APIKeyVersion]]:
        """
        Получить список ключей, требующих ротации
        
        Returns:
            List[(key_id, APIKeyVersion)]
        """
        keys_to_rotate = []
        now = datetime.now()
        warning_threshold = now + timedelta(days=self.warning_period_days)
        
        for key_id, versions in self.keys.items():
            for version in versions:
                if version.status != KeyStatus.ACTIVE:
                    continue
                
                if version.expires_at and version.expires_at <= warning_threshold:
                    keys_to_rotate.append((key_id, version))
        
        return keys_to_rotate
    
    def cleanup_expired_keys(self):
        """Очистить истёкшие deprecated ключи"""
        now = datetime.now()
        cleaned_count = 0
        
        for key_id, versions in self.keys.items():
            for version in versions:
                if (
                    version.status == KeyStatus.DEPRECATED and
                    version.expires_at and
                    now > version.expires_at
                ):
                    version.status = KeyStatus.EXPIRED
                    cleaned_count += 1
        
        if cleaned_count > 0:
            log.info(
                "expired_keys_cleaned",
                count=cleaned_count
            )
    
    def _generate_raw_key(self) -> str:
        """Генерация сырого API ключа"""
        # Формат: oneflow_<random_32_bytes_hex>
        random_bytes = secrets.token_bytes(32)
        return f"oneflow_{random_bytes.hex()}"
    
    def _hash_key(self, raw_key: str) -> str:
        """Хеширование ключа для безопасного хранения"""
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def get_statistics(self) -> Dict:
        """Получить статистику по ключам"""
        total_keys = len(self.keys)
        total_versions = sum(len(versions) for versions in self.keys.values())
        
        status_counts = {status: 0 for status in KeyStatus}
        for versions in self.keys.values():
            for version in versions:
                status_counts[version.status] += 1
        
        return {
            "total_keys": total_keys,
            "total_versions": total_versions,
            "status_counts": {
                status.value: count
                for status, count in status_counts.items()
            },
            "keys_requiring_rotation": len(self.get_keys_requiring_rotation())
        }
