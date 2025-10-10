"""
Retry механизм с экспоненциальной задержкой и джиттером
Таймауты для всех внешних вызовов
"""

import asyncio
import random
from typing import Optional, Callable, Any, Type, Tuple
from functools import wraps
import time

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    retry_if_result,
    before_sleep_log,
    after_log,
    RetryError
)

from src.observability.structured_logging import get_logger
from src.observability.metrics import retry_attempts_total

log = get_logger(__name__)


# ============================================================================
# TIMEOUT CONFIGURATION
# ============================================================================

class TimeoutConfig:
    """Конфигурация таймаутов для различных операций"""
    
    # Таймауты для API запросов к провайдерам
    PROVIDER_CONNECT_TIMEOUT = 5.0      # Подключение
    PROVIDER_READ_TIMEOUT = 30.0        # Чтение ответа
    PROVIDER_WRITE_TIMEOUT = 10.0       # Отправка запроса
    PROVIDER_POOL_TIMEOUT = 5.0         # Получение из пула
    
    # Таймауты для БД
    DB_QUERY_TIMEOUT = 5.0
    DB_TRANSACTION_TIMEOUT = 10.0
    
    # Таймауты для внутренних операций
    ROUTING_DECISION_TIMEOUT = 1.0
    CACHE_OPERATION_TIMEOUT = 0.5
    
    @classmethod
    def get_provider_timeout(cls) -> httpx.Timeout:
        """Получить timeout конфигурацию для провайдеров"""
        return httpx.Timeout(
            connect=cls.PROVIDER_CONNECT_TIMEOUT,
            read=cls.PROVIDER_READ_TIMEOUT,
            write=cls.PROVIDER_WRITE_TIMEOUT,
            pool=cls.PROVIDER_POOL_TIMEOUT
        )


# ============================================================================
# RETRY STRATEGIES
# ============================================================================

class RetryStrategy:
    """Стратегии retry для различных сценариев"""
    
    @staticmethod
    def aggressive():
        """Агрессивная стратегия: быстрые retry, много попыток"""
        return {
            'stop': stop_after_attempt(7),
            'wait': wait_exponential_jitter(
                initial=0.5,
                max=10,
                jitter=2
            )
        }
    
    @staticmethod
    def moderate():
        """Умеренная стратегия: баланс между скоростью и нагрузкой"""
        return {
            'stop': stop_after_attempt(5),
            'wait': wait_exponential_jitter(
                initial=1,
                max=30,
                jitter=5
            )
        }
    
    @staticmethod
    def conservative():
        """Консервативная стратегия: медленные retry, мало попыток"""
        return {
            'stop': stop_after_attempt(3),
            'wait': wait_exponential_jitter(
                initial=2,
                max=60,
                jitter=10
            )
        }
    
    @staticmethod
    def for_provider(provider: str):
        """Стратегия в зависимости от провайдера"""
        # Разные провайдеры могут иметь разные лимиты
        provider_strategies = {
            'openai': RetryStrategy.moderate(),
            'anthropic': RetryStrategy.moderate(),
            'stability': RetryStrategy.conservative(),
            'elevenlabs': RetryStrategy.conservative(),
        }
        return provider_strategies.get(provider, RetryStrategy.moderate())


# ============================================================================
# RETRYABLE EXCEPTIONS
# ============================================================================

RETRYABLE_HTTP_STATUS_CODES = {
    408,  # Request Timeout
    425,  # Too Early
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}

RETRYABLE_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.PoolTimeout,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    ConnectionError,
    asyncio.TimeoutError,
)


def is_retryable_http_error(exception: Exception) -> bool:
    """Проверка, является ли HTTP ошибка retriable"""
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in RETRYABLE_HTTP_STATUS_CODES
    return False


def should_retry_exception(exception: Exception) -> bool:
    """Определить, нужно ли повторять запрос при данном исключении"""
    return (
        isinstance(exception, RETRYABLE_EXCEPTIONS) or
        is_retryable_http_error(exception)
    )


# ============================================================================
# RETRY DECORATOR
# ============================================================================

def with_retry(
    provider: str,
    operation: str,
    strategy: Optional[dict] = None,
    custom_retry_condition: Optional[Callable] = None
):
    """
    Декоратор для добавления retry логики с экспоненциальной задержкой и джиттером
    
    Args:
        provider: Имя провайдера (для логирования и метрик)
        operation: Название операции
        strategy: Стратегия retry (по умолчанию moderate)
        custom_retry_condition: Кастомное условие для retry
    
    Usage:
        @with_retry(provider="openai", operation="completion")
        async def call_openai(prompt: str):
            # your code
            pass
    """
    
    if strategy is None:
        strategy = RetryStrategy.for_provider(provider)
    
    def decorator(func: Callable) -> Callable:
        
        @retry(
            retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS) | 
                  retry_if_exception(should_retry_exception) |
                  (retry_if_result(custom_retry_condition) if custom_retry_condition else retry_if_result(lambda x: False)),
            stop=strategy['stop'],
            wait=strategy['wait'],
            before_sleep=before_sleep_log(log, logging.WARNING),
            after=after_log(log, logging.DEBUG),
            reraise=True
        )
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            attempt = 0
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Логирование успешного выполнения
                duration = time.time() - start_time
                log.info(
                    "retry_success",
                    provider=provider,
                    operation=operation,
                    attempts=attempt + 1,
                    duration_seconds=duration
                )
                
                return result
                
            except RetryError as e:
                # Все попытки исчерпаны
                duration = time.time() - start_time
                
                retry_attempts_total.labels(
                    provider=provider,
                    reason="max_attempts_exceeded"
                ).inc()
                
                log.error(
                    "retry_exhausted",
                    provider=provider,
                    operation=operation,
                    attempts=attempt + 1,
                    duration_seconds=duration,
                    error=str(e.last_attempt.exception())
                )
                
                raise e.last_attempt.exception()
            
            except Exception as e:
                duration = time.time() - start_time
                
                log.error(
                    "retry_failed",
                    provider=provider,
                    operation=operation,
                    attempts=attempt + 1,
                    duration_seconds=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
        
        @retry(
            retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS) | 
                  retry_if_exception(should_retry_exception),
            stop=strategy['stop'],
            wait=strategy['wait'],
            before_sleep=before_sleep_log(log, logging.WARNING),
            reraise=True
        )
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            attempt = 0
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                log.info(
                    "retry_success",
                    provider=provider,
                    operation=operation,
                    attempts=attempt + 1,
                    duration_seconds=duration
                )
                
                return result
                
            except RetryError as e:
                duration = time.time() - start_time
                
                retry_attempts_total.labels(
                    provider=provider,
                    reason="max_attempts_exceeded"
                ).inc()
                
                log.error(
                    "retry_exhausted",
                    provider=provider,
                    operation=operation,
                    attempts=attempt + 1,
                    duration_seconds=duration,
                    error=str(e.last_attempt.exception())
                )
                
                raise e.last_attempt.exception()
            
            except Exception as e:
                duration = time.time() - start_time
                
                log.error(
                    "retry_failed",
                    provider=provider,
                    operation=operation,
                    duration_seconds=duration,
                    error=str(e)
                )
                
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================================================
# HTTP CLIENT С RETRY
# ============================================================================

class ResilientHTTPClient:
    """HTTP клиент с встроенной retry логикой и таймаутами"""
    
    def __init__(
        self,
        provider: str,
        base_url: Optional[str] = None,
        timeout: Optional[httpx.Timeout] = None,
        retry_strategy: Optional[dict] = None
    ):
        self.provider = provider
        self.timeout = timeout or TimeoutConfig.get_provider_timeout()
        self.retry_strategy = retry_strategy or RetryStrategy.for_provider(provider)
        
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=self.timeout,
            http2=True,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
        )
    
    @with_retry(provider="http", operation="request")
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Выполнить HTTP запрос с retry"""
        
        log.debug(
            "http_request_start",
            provider=self.provider,
            method=method,
            url=url
        )
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            
            log.debug(
                "http_request_success",
                provider=self.provider,
                method=method,
                url=url,
                status_code=response.status_code
            )
            
            return response
            
        except httpx.HTTPStatusError as e:
            log.warning(
                "http_request_error",
                provider=self.provider,
                method=method,
                url=url,
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET запрос"""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST запрос"""
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        """PUT запрос"""
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """DELETE запрос"""
        return await self.request("DELETE", url, **kwargs)
    
    async def close(self):
        """Закрыть клиент"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ============================================================================
# UTILITIES
# ============================================================================

async def with_timeout(coro, timeout: float, operation: str = "operation"):
    """
    Выполнить корутину с таймаутом
    
    Args:
        coro: Корутина для выполнения
        timeout: Таймаут в секундах
        operation: Название операции (для логирования)
    
    Raises:
        asyncio.TimeoutError: Если операция превысила таймаут
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        log.error(
            "operation_timeout",
            operation=operation,
            timeout_seconds=timeout
        )
        raise


import logging
