"""
OpenTelemetry трассировка для OneFlow.AI
Поддержка распределённого трейсинга с OTLP экспортом
"""

import os
from typing import Optional, Dict, Any
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.trace import Status, StatusCode, SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio


class TelemetryManager:
    """Менеджер для управления OpenTelemetry трассировкой"""
    
    def __init__(
        self,
        service_name: str = "oneflow-ai",
        service_version: str = "2.0.0",
        environment: str = "production",
        otlp_endpoint: Optional[str] = None,
        sample_rate: float = 1.0
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.otlp_endpoint = otlp_endpoint or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "localhost:4317"
        )
        self.sample_rate = sample_rate
        self.tracer: Optional[trace.Tracer] = None
        self._initialized = False
    
    def setup(self):
        """Инициализация OpenTelemetry"""
        if self._initialized:
            return
        
        # Создание Resource с метаданными сервиса
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            "deployment.environment": self.environment,
            "service.namespace": "oneflow",
        })
        
        # Настройка семплирования
        sampler = ParentBasedTraceIdRatio(self.sample_rate)
        
        # TracerProvider
        provider = TracerProvider(
            resource=resource,
            sampler=sampler
        )
        
        # OTLP экспортер
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.otlp_endpoint,
            insecure=True  # Использовать TLS в продакшене
        )
        
        # Batch processor для эффективной отправки
        span_processor = BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000
        )
        provider.add_span_processor(span_processor)
        
        # Console exporter для разработки
        if self.environment == "development":
            console_processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(console_processor)
        
        # Установка глобального TracerProvider
        trace.set_tracer_provider(provider)
        
        # Получение tracer
        self.tracer = trace.get_tracer(
            instrumenting_module_name=__name__,
            instrumenting_library_version=self.service_version
        )
        
        self._initialized = True
    
    def instrument_app(self, app):
        """Инструментация FastAPI приложения"""
        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls="/health,/metrics"  # Исключить health check endpoints
        )
    
    def instrument_db(self, engine):
        """Инструментация SQLAlchemy"""
        SQLAlchemyInstrumentor().instrument(
            engine=engine,
            enable_commenter=True,  # Добавлять trace context в SQL комментарии
        )
    
    def instrument_http_clients(self):
        """Инструментация HTTP клиентов"""
        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
    
    def get_tracer(self) -> trace.Tracer:
        """Получить tracer"""
        if not self._initialized:
            raise RuntimeError("TelemetryManager not initialized. Call setup() first.")
        return self.tracer
    
    @contextmanager
    def span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager для создания span
        
        Usage:
            with telemetry.span("process_request", attributes={"user_id": "123"}):
                # your code
                pass
        """
        span = self.tracer.start_span(name, kind=kind)
        
        if attributes:
            span.set_attributes(attributes)
        
        try:
            yield span
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
        finally:
            span.end()
    
    def trace_provider_call(
        self,
        provider: str,
        model: str,
        operation: str
    ):
        """
        Декоратор для трейсинга вызовов к провайдерам
        
        Usage:
            @telemetry.trace_provider_call("openai", "gpt-4", "completion")
            async def call_openai(prompt):
                pass
        """
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                with self.span(
                    f"{provider}.{operation}",
                    kind=SpanKind.CLIENT,
                    attributes={
                        "ai.provider": provider,
                        "ai.model": model,
                        "ai.operation": operation,
                    }
                ) as span:
                    try:
                        result = await func(*args, **kwargs)
                        
                        # Добавить информацию о результате
                        if isinstance(result, dict):
                            if 'tokens' in result:
                                span.set_attribute("ai.tokens.total", result['tokens'])
                            if 'cost' in result:
                                span.set_attribute("ai.cost", result['cost'])
                        
                        span.set_status(Status(StatusCode.OK))
                        return result
                    
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            
            def sync_wrapper(*args, **kwargs):
                with self.span(
                    f"{provider}.{operation}",
                    kind=SpanKind.CLIENT,
                    attributes={
                        "ai.provider": provider,
                        "ai.model": model,
                        "ai.operation": operation,
                    }
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        
                        if isinstance(result, dict):
                            if 'tokens' in result:
                                span.set_attribute("ai.tokens.total", result['tokens'])
                            if 'cost' in result:
                                span.set_attribute("ai.cost", result['cost'])
                        
                        span.set_status(Status(StatusCode.OK))
                        return result
                    
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def add_span_attributes(self, attributes: Dict[str, Any]):
        """Добавить атрибуты к текущему span"""
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.set_attributes(attributes)
    
    def add_span_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Добавить событие к текущему span"""
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.add_event(name, attributes=attributes or {})
    
    def get_trace_context(self) -> Dict[str, str]:
        """Получить trace context для передачи между сервисами"""
        propagator = TraceContextTextMapPropagator()
        carrier = {}
        propagator.inject(carrier)
        return carrier
    
    def inject_trace_context(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Инжектировать trace context в HTTP headers"""
        propagator = TraceContextTextMapPropagator()
        propagator.inject(headers)
        return headers
    
    def extract_trace_context(self, headers: Dict[str, str]):
        """Извлечь trace context из HTTP headers"""
        propagator = TraceContextTextMapPropagator()
        return propagator.extract(headers)
    
    def shutdown(self):
        """Корректное завершение работы"""
        if self._initialized:
            trace.get_tracer_provider().shutdown()


# Глобальный экземпляр
_telemetry_manager: Optional[TelemetryManager] = None


def get_telemetry() -> TelemetryManager:
    """Получить глобальный экземпляр TelemetryManager"""
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
        _telemetry_manager.setup()
    return _telemetry_manager


def init_telemetry(
    service_name: str = "oneflow-ai",
    service_version: str = "2.0.0",
    environment: str = "production",
    otlp_endpoint: Optional[str] = None,
    sample_rate: float = 1.0
) -> TelemetryManager:
    """
    Инициализация телеметрии
    
    Args:
        service_name: Имя сервиса
        service_version: Версия сервиса
        environment: Окружение (development, staging, production)
        otlp_endpoint: OTLP endpoint (default: localhost:4317)
        sample_rate: Процент трейсов для семплирования (0.0-1.0)
    
    Returns:
        TelemetryManager instance
    """
    global _telemetry_manager
    _telemetry_manager = TelemetryManager(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        otlp_endpoint=otlp_endpoint,
        sample_rate=sample_rate
    )
    _telemetry_manager.setup()
    return _telemetry_manager


# Convenience exports
tracer = lambda: get_telemetry().get_tracer()
span = lambda *args, **kwargs: get_telemetry().span(*args, **kwargs)
trace_provider_call = lambda *args, **kwargs: get_telemetry().trace_provider_call(*args, **kwargs)
