"""
Структурное логирование для OneFlow.AI с защитой от утечки секретов
"""

import logging
import logging.config
import sys
import re
from typing import Any, Dict, Optional
from datetime import datetime

import structlog
from opentelemetry import trace


# ============================================================================
# ФИЛЬТРЫ ДЛЯ ЗАЩИТЫ ОТ УТЕЧКИ СЕКРЕТОВ
# ============================================================================

SENSITIVE_PATTERNS = [
    # API ключи
    (re.compile(r'(sk-[a-zA-Z0-9]{20,})', re.IGNORECASE), '***API_KEY***'),
    (re.compile(r'(sk-ant-[a-zA-Z0-9]{20,})', re.IGNORECASE), '***ANTHROPIC_KEY***'),
    # Bearer токены
    (re.compile(r'Bearer\s+([a-zA-Z0-9\-._~+/]+=*)', re.IGNORECASE), 'Bearer ***TOKEN***'),
    # JWT токены
    (re.compile(r'(eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)'), '***JWT***'),
    # Пароли
    (re.compile(r'("password"\s*:\s*")([^"]+)(")'), r'\1***PASSWORD***\3'),
    (re.compile(r'("passwd"\s*:\s*")([^"]+)(")'), r'\1***PASSWORD***\3'),
    (re.compile(r'("pwd"\s*:\s*")([^"]+)(")'), r'\1***PASSWORD***\3'),
    # Секретные ключи
    (re.compile(r'("secret"\s*:\s*")([^"]+)(")'), r'\1***SECRET***\3'),
    (re.compile(r'("api_key"\s*:\s*")([^"]+)(")'), r'\1***API_KEY***\3'),
    (re.compile(r'("access_token"\s*:\s*")([^"]+)(")'), r'\1***TOKEN***\3'),
    (re.compile(r'("refresh_token"\s*:\s*")([^"]+)(")'), r'\1***TOKEN***\3'),
    # Credit card numbers
    (re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'), '***CARD***'),
]

SENSITIVE_KEYS = {
    'password', 'passwd', 'pwd', 'secret', 'api_key', 'apikey',
    'access_token', 'refresh_token', 'auth_token', 'authorization',
    'private_key', 'client_secret', 'session_key', 'cookie'
}


def sanitize_value(value: Any) -> Any:
    """Очистка значения от секретных данных"""
    if isinstance(value, str):
        sanitized = value
        for pattern, replacement in SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized
    elif isinstance(value, dict):
        return sanitize_dict(value)
    elif isinstance(value, (list, tuple)):
        return [sanitize_value(item) for item in value]
    return value


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Очистка словаря от секретных данных"""
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
            sanitized[key] = '***REDACTED***'
        else:
            sanitized[key] = sanitize_value(value)
    return sanitized


class SensitiveDataFilter(logging.Filter):
    """Фильтр логов для защиты от утечки секретов"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_value(record.msg)
        
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = sanitize_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(sanitize_value(arg) for arg in record.args)
        
        return True


# ============================================================================
# PROCESSORS ДЛЯ STRUCTLOG
# ============================================================================

def add_trace_context(logger, method_name, event_dict):
    """Добавление trace context из OpenTelemetry"""
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict['trace_id'] = format(ctx.trace_id, '032x')
        event_dict['span_id'] = format(ctx.span_id, '016x')
    return event_dict


def add_timestamp(logger, method_name, event_dict):
    """Добавление timestamp в ISO формате"""
    event_dict['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    return event_dict


def sanitize_event_dict(logger, method_name, event_dict):
    """Очистка event_dict от секретных данных"""
    return sanitize_dict(event_dict)


def add_service_context(logger, method_name, event_dict):
    """Добавление контекста сервиса"""
    event_dict.setdefault('service', 'oneflow-ai')
    event_dict.setdefault('version', '2.0.0')
    return event_dict


# ============================================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================================

def setup_logging(
    level: str = "INFO",
    json_logs: bool = True,
    environment: str = "production"
):
    """
    Настройка структурного логирования
    
    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Использовать JSON формат (True для production)
        environment: Окружение (development, staging, production)
    """
    
    # Уровень логирования
    log_level = getattr(logging, level.upper())
    
    # Процессоры для structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_timestamp,
        add_service_context,
        add_trace_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        sanitize_event_dict,  # ВАЖНО: Очистка секретов
    ]
    
    # Финальный рендерер
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Конфигурация structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Конфигурация стандартного logging
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'sensitive_data': {
                '()': SensitiveDataFilter,
            },
        },
        'formatters': {
            'json': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.processors.JSONRenderer(),
                'foreign_pre_chain': processors[:-1],
            },
            'colored': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(colors=True),
                'foreign_pre_chain': processors[:-1],
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'json' if json_logs else 'colored',
                'filters': ['sensitive_data'],
            },
            'error_file': {
                'level': logging.ERROR,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'json',
                'filters': ['sensitive_data'],
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'error_file'],
                'level': log_level,
                'propagate': True,
            },
            'uvicorn': {
                'handlers': ['default'],
                'level': logging.INFO,
                'propagate': False,
            },
            'uvicorn.access': {
                'handlers': ['default'],
                'level': logging.WARNING,  # Уменьшить verbosity
                'propagate': False,
            },
        },
    })


# ============================================================================
# ПОЛУЧЕНИЕ LOGGER
# ============================================================================

def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Получить структурный logger
    
    Args:
        name: Имя логгера (обычно __name__)
    
    Returns:
        structlog.BoundLogger instance
    
    Usage:
        log = get_logger(__name__)
        log.info("request_processed", 
                 user_id="123",
                 duration_ms=1234,
                 provider="openai")
    """
    return structlog.get_logger(name)


# ============================================================================
# CONTEXT MANAGER ДЛЯ ДОБАВЛЕНИЯ КОНТЕКСТА
# ============================================================================

class log_context:
    """
    Context manager для добавления контекста в логи
    
    Usage:
        with log_context(user_id="123", request_id="abc"):
            log.info("processing_request")  # автоматически добавит user_id и request_id
    """
    
    def __init__(self, **kwargs):
        self.context = kwargs
    
    def __enter__(self):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.clear_contextvars()


# ============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

"""
Example usage:

from src.observability.structured_logging import setup_logging, get_logger, log_context

# Настройка при старте приложения
setup_logging(level="INFO", json_logs=True, environment="production")

# Получение логгера
log = get_logger(__name__)

# Простое логирование
log.info("server_started", port=8000)

# Логирование с контекстом
with log_context(user_id="user123", request_id="req-abc"):
    log.info("processing_request", provider="openai", model="gpt-4")
    
    try:
        # your code
        result = process_request()
        log.info("request_completed", 
                 duration_ms=123,
                 tokens=456,
                 cost=0.05)
    except Exception as e:
        log.error("request_failed", 
                  error=str(e),
                  exc_info=True)

# Логирование с автоматической очисткой секретов
log.info("api_call", 
         api_key="sk-1234567890",  # Будет заменено на ***API_KEY***
         response={"data": "result"})

Output (JSON):
{
    "event": "processing_request",
    "level": "info",
    "timestamp": "2025-10-10T12:00:00.000000Z",
    "service": "oneflow-ai",
    "version": "2.0.0",
    "user_id": "user123",
    "request_id": "req-abc",
    "provider": "openai",
    "model": "gpt-4",
    "trace_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "span_id": "a1b2c3d4e5f6g7h8"
}
"""
