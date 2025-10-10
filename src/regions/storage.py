"""
Региональное хранилище с резидентностью данных
"""
from enum import Enum
from typing import Optional
from dataclasses import dataclass

class Region(Enum):
    US = "us"
    EU = "eu"
    RU = "ru"

@dataclass
class StorageConfig:
    """Конфигурация хранилища для региона"""
    region: Region
    database_url: str
    encryption_key: str
    s3_bucket: Optional[str] = None
    
    # Политики данных
    data_retention_days: int = 90
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    
    # Очереди
    queue_url: Optional[str] = None
    
    # Compliance
    gdpr_compliant: bool = False
    ccpa_compliant: bool = False

class RegionalStorageManager:
    """Менеджер регионального хранилища"""
    
    def __init__(self):
        self.storages = {
            Region.US: StorageConfig(
                region=Region.US,
                database_url="postgresql://us-db:5432/oneflow",
                encryption_key="us-key",
                s3_bucket="oneflow-us",
                queue_url="https://sqs.us-east-1.amazonaws.com/...",
                ccpa_compliant=True
            ),
            Region.EU: StorageConfig(
                region=Region.EU,
                database_url="postgresql://eu-db:5432/oneflow",
                encryption_key="eu-key",
                s3_bucket="oneflow-eu",
                queue_url="https://sqs.eu-west-1.amazonaws.com/...",
                gdpr_compliant=True,
                data_retention_days=60  # GDPR requirement
            ),
            Region.RU: StorageConfig(
                region=Region.RU,
                database_url="postgresql://ru-db:5432/oneflow",
                encryption_key="ru-key",
                s3_bucket="oneflow-ru",
                queue_url="https://sqs.ru-central-1.amazonaws.com/...",
            ),
        }
    
    def get_storage(self, region: Region) -> StorageConfig:
        """Получение конфигурации хранилища для региона"""
        return self.storages[region]
    
    def validate_data_residency(self, user_region: Region, data_region: Region) -> bool:
        """Валидация резидентности данных"""
        # Данные должны храниться в регионе пользователя
        return user_region == data_region
