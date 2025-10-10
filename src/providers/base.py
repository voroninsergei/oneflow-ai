"""
Базовый интерфейс для всех AI провайдеров
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

@dataclass
class ProviderConfig:
    """Конфигурация провайдера"""
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True

@dataclass
class ProviderResponse:
    """Унифицированный ответ от провайдера"""
    content: str
    cost: float
    tokens_used: int
    model_used: str
    latency_ms: float
    provider_name: str

class Provider(ABC):
    """Абстрактный базовый класс для всех провайдеров"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> ProviderResponse:
        """
        Генерация контента
        
        Raises:
            ProviderError: при ошибке вызова API
        """
        pass
    
    @abstractmethod
    async def estimate_cost(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> float:
        """Оценка стоимости запроса ДО его выполнения"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ProviderStatus:
        """Проверка доступности провайдера"""
        pass
    
    def _validate_config(self):
        """Валидация конфигурации"""
        if not self.config.api_key:
            raise ValueError(f"API key required for {self.__class__.__name__}")

class ProviderError(Exception):
    """Базовое исключение для ошибок провайдера"""
    pass
