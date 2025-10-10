"""
Circuit Breaker для защиты от каскадных сбоев
Использует pybreaker с метриками и логированием
"""

from typing import Dict, Optional, Callable, Any
from functools import wraps
import asyncio

from pybreaker import CircuitBreaker, CircuitBreakerError, CircuitBreakerListener, STATE_OPEN, STATE_CLOSED, STATE_HALF_OPEN

from src.observability.structured_logging import get_logger
from src.observability.metrics import (
    circuit_breaker_state,
    circuit_breaker_failures,
    circuit_breaker_successes,
    provider_health_status
)

log = get_logger(__name__)


# ============================================================================
# CIRCUIT BREAKER LISTENER ДЛЯ МЕТРИК И ЛОГИРОВАНИЯ
# ============================================================================

class MetricsCircuitBreakerListener(CircuitBreakerListener):
    """Слушатель для отслеживания состояния Circuit Breaker"""
    
    def __init__(self, provider: str):
        self.provider = provider
    
    def state_change(self, cb, old_state, new_state):
        """Изменение состояния Circuit Breaker"""
        
        # Обновление метрик
        state_value = {
            STATE_CLOSED: 0,
            STATE_OPEN: 1,
            STATE_HALF_OPEN: 2
        }
        circuit_breaker_state.labels(provider=self.provider).set(state_value[new_state])
        
        # Обновление health status
        is_healthy = new_state == STATE_CLOSED
        provider_health_status.labels(provider=self.provider).set(1 if is_healthy else 0)
        
        # Логирование
        log.warning(
            "circuit_breaker_state_changed",
            provider=self.provider,
            old_state=old_state.name,
            new_state=new_state.name,
            is_healthy=is_healthy
        )
    
    def before_call(self, cb, func, *args, **kwargs):
        """Перед вызовом функции"""
        log.debug(
            "circuit_breaker_before_call",
            provider=self.provider,
            func=func.__name__,
            state=cb.current_state.name
        )
    
    def success(self, cb):
        """Успешный вызов"""
        circuit_breaker_successes.labels(provider=self.provider).inc()
        
        log.debug(
            "circuit_breaker_success",
            provider=self.provider,
            failure_count=cb.fail_counter
        )
    
    def failure(self, cb, exception):
        """Неудачный вызов"""
        circuit_breaker_failures.labels(provider=self.provider).inc()
        
        log.warning(
            "circuit_breaker_failure",
            provider=self.provider,
            failure_count=cb.fail_counter,
            error=str(exception)
        )


# ============================================================================
# МЕНЕДЖЕР CIRCUIT BREAKERS
# ============================================================================

class CircuitBreakerManager:
    """Менеджер Circuit Breakers для провайдеров"""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._configs = {
            # Конфигурация по умолчанию
            'default': {
                'fail_max': 5,           # Максимум ошибок перед открытием
                'timeout_duration': 60,   # Время в open state (секунды)
                'reset_timeout': 30,      # Время для возврата в closed после успеха
                'expected_exception': Exception
            },
            # Конфигурация для OpenAI
            'openai': {
                'fail_max': 5,
                'timeout_duration': 60,
                'reset_timeout': 30,
                'expected_exception': Exception
            },
            # Конфигурация для Anthropic
            'anthropic': {
                'fail_max': 5,
                'timeout_duration': 60,
                'reset_timeout': 30,
                'expected_exception': Exception
            },
            # Конфигурация для Stability AI (более консервативная)
            'stability': {
                'fail_max': 3,
                'timeout_duration': 120,
                'reset_timeout': 45,
                'expected_exception': Exception
            },
            # Конфигурация для ElevenLabs
            'elevenlabs': {
                'fail_max': 3,
                'timeout_duration': 120,
                'reset_timeout': 45,
                'expected_exception': Exception
            },
        }
    
    def get_breaker(self, provider: str) -> CircuitBreaker:
        """
        Получить Circuit Breaker для провайдера
        
        Args:
            provider: Имя провайдера
        
        Returns:
            CircuitBreaker instance
        """
        if provider not in self._breakers:
            config = self._configs.get(provider, self._configs['default'])
            
            breaker = CircuitBreaker(
                fail_max=config['fail_max'],
                timeout_duration=config['timeout_duration'],
                reset_timeout=config['reset_timeout'],
                expected_exception=config['expected_exception'],
                name=f"{provider}_breaker",
                listeners=[MetricsCircuitBreakerListener(provider)]
            )
            
            self._breakers[provider] = breaker
            
            log.info(
                "circuit_breaker_created",
                provider=provider,
                fail_max=config['fail_max'],
                timeout_duration=config['timeout_duration']
            )
        
        return self._breakers[provider]
    
    def get_state(self, provider: str) -> str:
        """Получить текущее состояние Circuit Breaker"""
        if provider in self._breakers:
            return self._breakers[provider].current_state.name
        return "UNKNOWN"
    
    def is_available(self, provider: str) -> bool:
        """Проверить, доступен ли провайдер (Circuit Breaker не открыт)"""
        if provider not in self._breakers:
            return True
        return self._breakers[provider].current_state != STATE_OPEN
    
    def reset(self, provider: str):
        """Сбросить Circuit Breaker"""
        if provider in self._breakers:
            self._breakers[provider].reset()
            log.info(
                "circuit_breaker_reset",
                provider=provider
            )
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Получить состояние всех Circuit Breakers"""
        states = {}
        for provider, breaker in self._breakers.items():
            states[provider] = {
                'state': breaker.current_state.name,
                'fail_counter': breaker.fail_counter,
                'fail_max': breaker.fail_max,
                'is_available': breaker.current_state != STATE_OPEN
            }
        return states


# Глобальный экземпляр
_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Получить глобальный экземпляр CircuitBreakerManager"""
    global _circuit_breaker_manager
    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = CircuitBreakerManager()
    return _circuit_breaker_manager


# ============================================================================
# ДЕКОРАТОР ДЛЯ ИСПОЛЬЗОВАНИЯ CIRCUIT BREAKER
# ============================================================================

def with_circuit_breaker(provider: str):
    """
    Декоратор для защиты функции Circuit Breaker
    
    Args:
        provider: Имя провайдера
    
    Usage:
        @with_circuit_breaker("openai")
        async def call_openai_api():
            # your code
            pass
    
    Raises:
        CircuitBreakerError: Если Circuit Breaker открыт
    """
    def decorator(func: Callable) -> Callable:
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            manager = get_circuit_breaker_manager()
            breaker = manager.get_breaker(provider)
            
            try:
                # Вызов через Circuit Breaker
                if asyncio.iscoroutinefunction(func):
                    result = await breaker.call_async(func, *args, **kwargs)
                else:
                    result = breaker.call(func, *args, **kwargs)
                
                return result
            
            except CircuitBreakerError as e:
                log.error(
                    "circuit_breaker_open",
                    provider=provider,
                    state=breaker.current_state.name,
                    fail_counter=breaker.fail_counter,
                    error=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            manager = get_circuit_breaker_manager()
            breaker = manager.get_breaker(provider)
            
            try:
                result = breaker.call(func, *args, **kwargs)
                return result
            
            except CircuitBreakerError as e:
                log.error(
                    "circuit_breaker_open",
                    provider=provider,
                    state=breaker.current_state.name,
                    error=str(e)
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================================================
# ИНТЕГРАЦИЯ С FALLBACK МЕХАНИЗМОМ
# ============================================================================

class CircuitBreakerAwareFallback:
    """Fallback механизм с учётом состояния Circuit Breakers"""
    
    def __init__(self, fallback_chain: list[str]):
        """
        Args:
            fallback_chain: Список провайдеров в порядке приоритета
        """
        self.fallback_chain = fallback_chain
        self.manager = get_circuit_breaker_manager()
    
    async def execute_with_fallback(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Выполнить функцию с fallback на другие провайдеры
        
        Args:
            func: Функция для выполнения (принимает provider как первый аргумент)
            *args, **kwargs: Аргументы для функции
        
        Returns:
            Результат выполнения функции
        
        Raises:
            Exception: Если все провайдеры недоступны
        """
        errors = []
        
        for provider in self.fallback_chain:
            # Проверить, доступен ли провайдер
            if not self.manager.is_available(provider):
                log.warning(
                    "provider_unavailable_skip",
                    provider=provider,
                    state=self.manager.get_state(provider)
                )
                continue
            
            try:
                log.info(
                    "attempting_provider",
                    provider=provider
                )
                
                result = await func(provider, *args, **kwargs)
                
                log.info(
                    "provider_success",
                    provider=provider
                )
                
                return result
            
            except CircuitBreakerError as e:
                errors.append((provider, e))
                log.warning(
                    "provider_circuit_breaker_open",
                    provider=provider,
                    error=str(e)
                )
                continue
            
            except Exception as e:
                errors.append((provider, e))
                log.error(
                    "provider_failed",
                    provider=provider,
                    error=str(e)
                )
                continue
        
        # Все провайдеры недоступны
        log.error(
            "all_providers_failed",
            fallback_chain=self.fallback_chain,
            errors=[(p, str(e)) for p, e in errors]
        )
        
        raise Exception(
            f"All providers failed. Errors: {[(p, str(e)) for p, e in errors]}"
        )
