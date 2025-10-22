"""
Circuit Breaker и Retry логика для надёжных интеграций с AI провайдерами
"""
import asyncio
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

import structlog
from circuitbreaker import circuit
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import httpx
import logging

logger = structlog.get_logger()


class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Цепь разорвана, запросы блокируются
    HALF_OPEN = "half_open"  # Проверка восстановления


class ProviderCircuitBreaker:
    """
    Circuit Breaker для каждого AI провайдера
    
    Параметры:
    - failure_threshold: количество ошибок до открытия цепи
    - recovery_timeout: время до попытки восстановления (секунды)
    - expected_exception: тип исключений, которые считаются ошибками
    """
    
    def __init__(
        self,
        provider_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.provider_name = provider_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def __call__(self, func: Callable) -> Callable:
        """Декоратор для применения circuit breaker"""
        async def wrapper(*args, **kwargs):
            # Проверка состояния цепи
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(
                        "circuit_breaker_half_open",
                        provider=self.provider_name
                    )
                    self.state = CircuitState.HALF_OPEN
                else:
                    logger.warning(
                        "circuit_breaker_open",
                        provider=self.provider_name,
                        failure_count=self.failure_count
                    )
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN for {self.provider_name}"
                    )
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            
            except self.expected_exception as e:
                self._on_failure()
                logger.error(
                    "circuit_breaker_failure",
                    provider=self.provider_name,
                    error=str(e),
                    failure_count=self.failure_count,
                    state=self.state.value
                )
                raise
        
        return wrapper
    
    def _on_success(self):
        """Обработка успешного запроса"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(
                "circuit_breaker_recovered",
                provider=self.provider_name
            )
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Обработка неудачного запроса"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                "circuit_breaker_opened",
                provider=self.provider_name,
                failure_count=self.failure_count
            )
    
    def _should_attempt_reset(self) -> bool:
        """Проверка, можно ли попытаться восстановить цепь"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.utcnow() - self.last_failure_time
        return time_since_failure > timedelta(seconds=self.recovery_timeout)


class CircuitBreakerOpenError(Exception):
    """Исключение, когда circuit breaker открыт"""
    pass


class ResilientHTTPClient:
    """
    HTTP клиент с retry, circuit breaker и таймаутами
    """
    
    def __init__(
        self,
        provider_name: str,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 5
    ):
        self.provider_name = provider_name
        self.timeout = httpx.Timeout(
            timeout=timeout,
            connect=connect_timeout
        )
        self.max_retries = max_retries
        
        # Circuit breaker для этого провайдера
        self.circuit_breaker = ProviderCircuitBreaker(
            provider_name=provider_name,
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=60
        )
        
        # HTTP клиент
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100
            )
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def post(
        self,
        url: str,
        json: dict,
        headers: Optional[dict] = None,
        idempotency_key: Optional[str] = None
    ) -> dict:
        """
        POST запрос с retry и circuit breaker
        
        Args:
            url: URL для запроса
            json: JSON данные
            headers: HTTP заголовки
            idempotency_key: Ключ идемпотентности
        """
        
        @self.circuit_breaker
        async def _make_request():
            request_headers = headers or {}
            
            # Добавление idempotency key
            if idempotency_key:
                request_headers["Idempotency-Key"] = idempotency_key
            
            logger.info(
                "http_request_start",
                provider=self.provider_name,
                url=url,
                idempotency_key=idempotency_key
            )
            
            try:
                response = await self.client.post(
                    url=url,
                    json=json,
                    headers=request_headers
                )
                response.raise_for_status()
                
                logger.info(
                    "http_request_success",
                    provider=self.provider_name,
                    status_code=response.status_code
                )
                
                return response.json()
            
            except httpx.TimeoutException as e:
                logger.error(
                    "http_request_timeout",
                    provider=self.provider_name,
                    error=str(e)
                )
                raise
            
            except httpx.HTTPStatusError as e:
                logger.error(
                    "http_request_error",
                    provider=self.provider_name,
                    status_code=e.response.status_code,
                    error=str(e)
                )
                
                # Не делать retry для 4xx ошибок (кроме 429)
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    raise ValueError(f"Client error: {e.response.status_code}")
                
                raise
        
        return await _make_request()
    
    async def close(self):
        """Закрытие HTTP клиента"""
        await self.client.aclose()


# ===== Использование =====

async def call_openai_with_resilience(prompt: str, api_key: str) -> dict:
    """
    Пример использования ResilientHTTPClient для OpenAI
    """
    client = ResilientHTTPClient(
        provider_name="openai",
        timeout=30.0,
        max_retries=3
    )
    
    try:
        response = await client.post(
            url="https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}]
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            idempotency_key=f"req-{hash(prompt)}"  # Простой пример
        )
        return response
    
    except CircuitBreakerOpenError:
        logger.error("openai_circuit_breaker_open")
        # Fallback на другого провайдера
        raise
    
    except Exception as e:
        logger.error("openai_request_failed", error=str(e))
        raise
    
    finally:
        await client.close()


# ===== Quota Management =====

from redis import Redis
from limits import strategies
from limits.storage import RedisStorage

class QuotaManager:
    """
    Управление квотами per-user/per-project/per-provider
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.storage = RedisStorage(redis_url)
        self.limiter = strategies.MovingWindowRateLimiter(self.storage)
    
    async def check_quota(
        self,
        user_id: str,
        provider: str,
        limit: str = "100/hour"
    ) -> bool:
        """
        Проверка квоты для пользователя
        
        Args:
            user_id: ID пользователя
            provider: Название провайдера
            limit: Лимит (например, "100/hour", "1000/day")
        
        Returns:
            True если квота не превышена
        """
        key = f"quota:{user_id}:{provider}"
        
        from limits.aio.strategies import MovingWindowRateLimiter as AsyncLimiter
        
        async_limiter = AsyncLimiter(self.storage)
        
        allowed = await async_limiter.hit(
            limit,
            key
        )
        
        if not allowed:
            logger.warning(
                "quota_exceeded",
                user_id=user_id,
                provider=provider,
                limit=limit
            )
        
        return allowed
