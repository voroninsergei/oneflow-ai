"""
Prometheus metrics для OneFlow.AI
Endpoint: /metrics
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
from fastapi import Response
import time
from typing import Optional
from functools import wraps
import asyncio


# ============================================================================
# МЕТРИКИ ЗАПРОСОВ
# ============================================================================

requests_total = Counter(
    'oneflow_requests_total',
    'Total number of AI requests',
    ['provider', 'model', 'status', 'user_id']
)

request_duration_seconds = Histogram(
    'oneflow_request_duration_seconds',
    'Request processing duration in seconds',
    ['provider', 'model', 'endpoint'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0)
)

request_size_bytes = Histogram(
    'oneflow_request_size_bytes',
    'Size of request payload in bytes',
    ['provider', 'model'],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000)
)

response_size_bytes = Histogram(
    'oneflow_response_size_bytes',
    'Size of response payload in bytes',
    ['provider', 'model'],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000)
)


# ============================================================================
# МЕТРИКИ СТОИМОСТИ
# ============================================================================

cost_total = Counter(
    'oneflow_cost_total_credits',
    'Total cost in credits',
    ['provider', 'user_id', 'project_id']
)

cost_per_request = Histogram(
    'oneflow_cost_per_request_credits',
    'Cost per request in credits',
    ['provider', 'model'],
    buckets=(0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0)
)


# ============================================================================
# МЕТРИКИ БЮДЖЕТА И БАЛАНСА
# ============================================================================

budget_remaining = Gauge(
    'oneflow_budget_remaining_credits',
    'Remaining budget in credits',
    ['user_id', 'period']
)

wallet_balance = Gauge(
    'oneflow_wallet_balance_credits',
    'Current wallet balance in credits',
    ['user_id']
)

budget_utilization_percent = Gauge(
    'oneflow_budget_utilization_percent',
    'Budget utilization percentage',
    ['user_id', 'period']
)


# ============================================================================
# МЕТРИКИ ПРОВАЙДЕРОВ
# ============================================================================

provider_health_status = Gauge(
    'oneflow_provider_health_status',
    'Provider health status (1=healthy, 0=unhealthy)',
    ['provider']
)

provider_latency_seconds = Gauge(
    'oneflow_provider_latency_seconds',
    'Average provider latency in seconds',
    ['provider']
)

provider_error_rate = Gauge(
    'oneflow_provider_error_rate',
    'Provider error rate (0-1)',
    ['provider']
)

provider_availability = Gauge(
    'oneflow_provider_availability_percent',
    'Provider availability percentage',
    ['provider']
)

provider_requests_active = Gauge(
    'oneflow_provider_requests_active',
    'Number of active requests to provider',
    ['provider']
)


# ============================================================================
# МЕТРИКИ CIRCUIT BREAKER
# ============================================================================

circuit_breaker_state = Gauge(
    'oneflow_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['provider']
)

circuit_breaker_failures = Counter(
    'oneflow_circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['provider']
)

circuit_breaker_successes = Counter(
    'oneflow_circuit_breaker_successes_total',
    'Total circuit breaker successes',
    ['provider']
)


# ============================================================================
# МЕТРИКИ RETRY И FALLBACK
# ============================================================================

retry_attempts_total = Counter(
    'oneflow_retry_attempts_total',
    'Total retry attempts',
    ['provider', 'reason']
)

fallback_activations_total = Counter(
    'oneflow_fallback_activations_total',
    'Total fallback activations',
    ['from_provider', 'to_provider', 'reason']
)


# ============================================================================
# МЕТРИКИ МАРШРУТИЗАЦИИ
# ============================================================================

routing_decisions_total = Counter(
    'oneflow_routing_decisions_total',
    'Total routing decisions',
    ['strategy', 'selected_provider']
)

routing_decision_duration_seconds = Histogram(
    'oneflow_routing_decision_duration_seconds',
    'Time taken to make routing decision',
    ['strategy'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)


# ============================================================================
# МЕТРИКИ БАЗЫ ДАННЫХ
# ============================================================================

db_query_duration_seconds = Histogram(
    'oneflow_db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

db_connection_pool_size = Gauge(
    'oneflow_db_connection_pool_size',
    'Database connection pool size',
    []
)

db_connection_pool_active = Gauge(
    'oneflow_db_connection_pool_active',
    'Active database connections',
    []
)


# ============================================================================
# МЕТРИКИ АУТЕНТИФИКАЦИИ
# ============================================================================

auth_attempts_total = Counter(
    'oneflow_auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']
)

active_sessions = Gauge(
    'oneflow_active_sessions',
    'Number of active user sessions',
    []
)


# ============================================================================
# МЕТРИКИ RATE LIMITING
# ============================================================================

rate_limit_exceeded_total = Counter(
    'oneflow_rate_limit_exceeded_total',
    'Total rate limit exceeded events',
    ['user_id', 'endpoint']
)

quota_exceeded_total = Counter(
    'oneflow_quota_exceeded_total',
    'Total quota exceeded events',
    ['user_id', 'provider', 'quota_type']
)


# ============================================================================
# СИСТЕМНЫЕ МЕТРИКИ
# ============================================================================

system_info = Info(
    'oneflow_system',
    'OneFlow system information'
)

uptime_seconds = Gauge(
    'oneflow_uptime_seconds',
    'System uptime in seconds'
)


# ============================================================================
# ДЕКОРАТОРЫ ДЛЯ АВТОМАТИЧЕСКОГО УЧЁТА МЕТРИК
# ============================================================================

def track_request_metrics(provider: str, model: str):
    """Декоратор для трекинга метрик запросов"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            provider_requests_active.labels(provider=provider).inc()
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                
                requests_total.labels(
                    provider=provider,
                    model=model,
                    status=status,
                    user_id=kwargs.get('user_id', 'unknown')
                ).inc()
                
                request_duration_seconds.labels(
                    provider=provider,
                    model=model,
                    endpoint=func.__name__
                ).observe(duration)
                
                provider_requests_active.labels(provider=provider).dec()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            provider_requests_active.labels(provider=provider).inc()
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                
                requests_total.labels(
                    provider=provider,
                    model=model,
                    status=status,
                    user_id=kwargs.get('user_id', 'unknown')
                ).inc()
                
                request_duration_seconds.labels(
                    provider=provider,
                    model=model,
                    endpoint=func.__name__
                ).observe(duration)
                
                provider_requests_active.labels(provider=provider).dec()
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def track_cost_metrics(provider: str, user_id: str, project_id: str = "default"):
    """Декоратор для трекинга метрик стоимости"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if isinstance(result, dict) and 'cost' in result:
                cost = result['cost']
                cost_total.labels(
                    provider=provider,
                    user_id=user_id,
                    project_id=project_id
                ).inc(cost)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if isinstance(result, dict) and 'cost' in result:
                cost = result['cost']
                cost_total.labels(
                    provider=provider,
                    user_id=user_id,
                    project_id=project_id
                ).inc(cost)
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================================================
# ENDPOINT ДЛЯ PROMETHEUS
# ============================================================================

async def metrics_endpoint():
    """FastAPI endpoint для Prometheus метрик"""
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )


# ============================================================================
# ИНИЦИАЛИЗАЦИЯ СИСТЕМНЫХ МЕТРИК
# ============================================================================

def init_metrics(version: str = "2.0.0", environment: str = "production"):
    """Инициализация системных метрик"""
    system_info.info({
        'version': version,
        'environment': environment
    })
    
    # Начальное время запуска
    import time
    _start_time = time.time()
    
    def update_uptime():
        uptime_seconds.set(time.time() - _start_time)
    
    return update_uptime
