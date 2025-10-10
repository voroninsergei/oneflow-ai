"""
Rate Limiting и Quota Management
Лимиты на провайдера, пользователя и проект
"""

import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from aiolimiter import AsyncLimiter

from src.observability.structured_logging import get_logger
from src.observability.metrics import (
    rate_limit_exceeded_total,
    quota_exceeded_total
)

log = get_logger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class RateLimitExceededError(Exception):
    """Rate limit превышен"""
    
    def __init__(self, message: str, retry_after: Optional[float] = None):
        self.retry_after = retry_after
        super().__init__(message)


class QuotaExceededError(Exception):
    """Квота превышена"""
    
    def __init__(self, message: str, quota_type: str, reset_time: Optional[datetime] = None):
        self.quota_type = quota_type
        self.reset_time = reset_time
        super().__init__(message)


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Rate limiter с поддержкой различных лимитов"""
    
    def __init__(self):
        # Лимиты по провайдеру (запросов в минуту)
        self.provider_limits = {
            'openai': AsyncLimiter(60, 60),        # 60 req/min
            'anthropic': AsyncLimiter(50, 60),     # 50 req/min
            'stability': AsyncLimiter(30, 60),     # 30 req/min
            'elevenlabs': AsyncLimiter(40, 60),    # 40 req/min
        }
        
        # Лимиты по пользователю (запросов в час)
        self.user_limiters: Dict[str, Dict[str, AsyncLimiter]] = defaultdict(dict)
        
        # Глобальный лимит
        self.global_limiter = AsyncLimiter(1000, 60)  # 1000 req/min глобально
    
    async def check_provider_limit(self, provider: str) -> bool:
        """
        Проверить лимит провайдера
        
        Args:
            provider: Имя провайдера
        
        Returns:
            True если лимит не превышен
        
        Raises:
            RateLimitExceededError: Если лимит превышен
        """
        if provider not in self.provider_limits:
            log.warning(
                "unknown_provider_rate_limit",
                provider=provider
            )
            return True
        
        limiter = self.provider_limits[provider]
        
        if not limiter.has_capacity():
            rate_limit_exceeded_total.labels(
                user_id="system",
                endpoint=f"provider:{provider}"
            ).inc()
            
            retry_after = 60.0  # Retry after 1 minute
            
            log.warning(
                "provider_rate_limit_exceeded",
                provider=provider,
                retry_after=retry_after
            )
            
            raise RateLimitExceededError(
                f"Rate limit exceeded for provider {provider}",
                retry_after=retry_after
            )
        
        async with limiter:
            return True
    
    async def check_user_limit(
        self,
        user_id: str,
        provider: str,
        requests_per_hour: int = 100
    ) -> bool:
        """
        Проверить лимит пользователя
        
        Args:
            user_id: ID пользователя
            provider: Провайдер
            requests_per_hour: Лимит запросов в час
        
        Returns:
            True если лимит не превышен
        
        Raises:
            RateLimitExceededError: Если лимит превышен
        """
        key = f"{user_id}:{provider}"
        
        if key not in self.user_limiters[user_id]:
            self.user_limiters[user_id][key] = AsyncLimiter(requests_per_hour, 3600)
        
        limiter = self.user_limiters[user_id][key]
        
        if not limiter.has_capacity():
            rate_limit_exceeded_total.labels(
                user_id=user_id,
                endpoint=f"user:{provider}"
            ).inc()
            
            retry_after = 3600.0  # Retry after 1 hour
            
            log.warning(
                "user_rate_limit_exceeded",
                user_id=user_id,
                provider=provider,
                retry_after=retry_after
            )
            
            raise RateLimitExceededError(
                f"User rate limit exceeded for {user_id} on {provider}",
                retry_after=retry_after
            )
        
        async with limiter:
            return True
    
    async def check_global_limit(self) -> bool:
        """Проверить глобальный лимит системы"""
        if not self.global_limiter.has_capacity():
            rate_limit_exceeded_total.labels(
                user_id="system",
                endpoint="global"
            ).inc()
            
            log.error(
                "global_rate_limit_exceeded",
                message="System-wide rate limit exceeded"
            )
            
            raise RateLimitExceededError(
                "System-wide rate limit exceeded",
                retry_after=60.0
            )
        
        async with self.global_limiter:
            return True
    
    async def acquire(
        self,
        provider: str,
        user_id: str,
        requests_per_hour: int = 100
    ) -> bool:
        """
        Проверить все лимиты перед выполнением запроса
        
        Args:
            provider: Провайдер
            user_id: ID пользователя
            requests_per_hour: Лимит пользователя
        
        Returns:
            True если все лимиты пройдены
        """
        await self.check_global_limit()
        await self.check_provider_limit(provider)
        await self.check_user_limit(user_id, provider, requests_per_hour)
        return True


# ============================================================================
# QUOTA MANAGER
# ============================================================================

class QuotaManager:
    """Управление квотами пользователей и проектов"""
    
    def __init__(self):
        # Использование квот: {user_id: {provider: {period: usage}}}
        self.usage: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(float))
        )
        
        # Конфигурация квот: {user_id: {provider: {period: limit}}}
        self.quotas: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {
                'hourly': 100.0,   # 100 credits per hour
                'daily': 1000.0,   # 1000 credits per day
                'weekly': 5000.0,  # 5000 credits per week
                'monthly': 20000.0 # 20000 credits per month
            })
        )
        
        # Время последнего сброса
        self.last_reset: Dict[str, Dict[str, datetime]] = defaultdict(
            lambda: defaultdict(lambda: datetime.now())
        )
    
    def set_quota(
        self,
        user_id: str,
        provider: str,
        period: str,
        limit: float
    ):
        """
        Установить квоту
        
        Args:
            user_id: ID пользователя
            provider: Провайдер (или 'all' для всех)
            period: Период (hourly, daily, weekly, monthly)
            limit: Лимит в кредитах
        """
        self.quotas[user_id][provider][period] = limit
        
        log.info(
            "quota_set",
            user_id=user_id,
            provider=provider,
            period=period,
            limit=limit
        )
    
    def _should_reset(self, last_reset: datetime, period: str) -> bool:
        """Проверить, нужно ли сбросить счётчик"""
        now = datetime.now()
        
        if period == 'hourly':
            return (now - last_reset) >= timedelta(hours=1)
        elif period == 'daily':
            return (now - last_reset) >= timedelta(days=1)
        elif period == 'weekly':
            return (now - last_reset) >= timedelta(weeks=1)
        elif period == 'monthly':
            return (now - last_reset) >= timedelta(days=30)
        
        return False
    
    def _reset_if_needed(self, user_id: str, provider: str, period: str):
        """Сбросить счётчик если нужно"""
        key = f"{user_id}:{provider}:{period}"
        last_reset = self.last_reset[user_id].get(key, datetime.now())
        
        if self._should_reset(last_reset, period):
            self.usage[user_id][provider][period] = 0.0
            self.last_reset[user_id][key] = datetime.now()
            
            log.debug(
                "quota_reset",
                user_id=user_id,
                provider=provider,
                period=period
            )
    
    def check_quota(
        self,
        user_id: str,
        provider: str,
        cost: float
    ) -> bool:
        """
        Проверить квоту перед выполнением запроса
        
        Args:
            user_id: ID пользователя
            provider: Провайдер
            cost: Стоимость запроса в кредитах
        
        Returns:
            True если квота не превышена
        
        Raises:
            QuotaExceededError: Если квота превышена
        """
        # Проверить все периоды
        for period in ['hourly', 'daily', 'weekly', 'monthly']:
            self._reset_if_needed(user_id, provider, period)
            
            current_usage = self.usage[user_id][provider][period]
            quota_limit = self.quotas[user_id][provider].get(period, float('inf'))
            
            if current_usage + cost > quota_limit:
                quota_exceeded_total.labels(
                    user_id=user_id,
                    provider=provider,
                    quota_type=period
                ).inc()
                
                # Вычислить время сброса
                key = f"{user_id}:{provider}:{period}"
                last_reset = self.last_reset[user_id].get(key, datetime.now())
                
                if period == 'hourly':
                    reset_time = last_reset + timedelta(hours=1)
                elif period == 'daily':
                    reset_time = last_reset + timedelta(days=1)
                elif period == 'weekly':
                    reset_time = last_reset + timedelta(weeks=1)
                else:  # monthly
                    reset_time = last_reset + timedelta(days=30)
                
                log.warning(
                    "quota_exceeded",
                    user_id=user_id,
                    provider=provider,
                    period=period,
                    current_usage=current_usage,
                    limit=quota_limit,
                    reset_time=reset_time.isoformat()
                )
                
                raise QuotaExceededError(
                    f"{period.capitalize()} quota exceeded for user {user_id} on {provider}",
                    quota_type=period,
                    reset_time=reset_time
                )
        
        return True
    
    def record_usage(
        self,
        user_id: str,
        provider: str,
        cost: float
    ):
        """
        Записать использование квоты
        
        Args:
            user_id: ID пользователя
            provider: Провайдер
            cost: Стоимость в кредитах
        """
        for period in ['hourly', 'daily', 'weekly', 'monthly']:
            self.usage[user_id][provider][period] += cost
        
        log.debug(
            "quota_usage_recorded",
            user_id=user_id,
            provider=provider,
            cost=cost
        )
    
    def get_usage(
        self,
        user_id: str,
        provider: Optional[str] = None
    ) -> Dict:
        """
        Получить текущее использование квот
        
        Args:
            user_id: ID пользователя
            provider: Провайдер (опционально)
        
        Returns:
            Словарь с информацией об использовании
        """
        if provider:
            return {
                period: {
                    'usage': self.usage[user_id][provider][period],
                    'limit': self.quotas[user_id][provider].get(period, float('inf')),
                    'remaining': self.quotas[user_id][provider].get(period, float('inf')) - 
                                self.usage[user_id][provider][period]
                }
                for period in ['hourly', 'daily', 'weekly', 'monthly']
            }
        else:
            # Вернуть для всех провайдеров
            result = {}
            for prov in self.usage[user_id].keys():
                result[prov] = self.get_usage(user_id, prov)
            return result


# ============================================================================
# ГЛОБАЛЬНЫЕ ЭКЗЕМПЛЯРЫ
# ============================================================================

_rate_limiter: Optional[RateLimiter] = None
_quota_manager: Optional[QuotaManager] = None


def get_rate_limiter() -> RateLimiter:
    """Получить глобальный экземпляр RateLimiter"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_quota_manager() -> QuotaManager:
    """Получить глобальный экземпляр QuotaManager"""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager()
    return _quota_manager
