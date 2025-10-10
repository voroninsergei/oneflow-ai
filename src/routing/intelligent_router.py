"""
Интеллектуальная маршрутизация с формализованными стратегиями
Поддержка latency-aware, cost-aware, quality-aware и balanced routing
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import time
from collections import defaultdict

from src.observability.structured_logging import get_logger
from src.observability.metrics import (
    routing_decisions_total,
    routing_decision_duration_seconds
)
from src.resilience.circuit_breaker import get_circuit_breaker_manager

log = get_logger(__name__)


# ============================================================================
# ROUTING STRATEGIES
# ============================================================================

class RoutingStrategy(Enum):
    """Стратегии маршрутизации"""
    LATENCY_AWARE = "latency"      # Минимизация задержки
    COST_AWARE = "cost"            # Минимизация стоимости
    QUALITY_AWARE = "quality"      # Максимизация качества
    BALANCED = "balanced"          # Сбалансированный подход
    AVAILABILITY = "availability"  # Только доступные провайдеры


@dataclass
class ProviderScore:
    """Оценка провайдера для маршрутизации"""
    provider: str
    score: float
    latency: float
    cost: float
    quality: float
    availability: float
    reason: str
    metadata: Dict


@dataclass
class ProviderStats:
    """Статистика провайдера"""
    avg_latency: float           # Средняя задержка (секунды)
    p95_latency: float           # 95-й перцентиль задержки
    p99_latency: float           # 99-й перцентиль задержки
    cost_per_request: float      # Средняя стоимость запроса
    quality_score: float         # Оценка качества (0-1)
    availability: float          # Доступность (0-1)
    error_rate: float            # Частота ошибок (0-1)
    total_requests: int          # Всего запросов
    successful_requests: int     # Успешных запросов
    failed_requests: int         # Неудачных запросов
    last_success_time: float     # Время последнего успеха
    last_failure_time: float     # Время последней ошибки


# ============================================================================
# PROVIDER STATS TRACKER
# ============================================================================

class ProviderStatsTracker:
    """Отслеживание статистики провайдеров"""
    
    def __init__(self):
        self.stats: Dict[str, ProviderStats] = {}
        self.latency_history: Dict[str, List[float]] = defaultdict(list)
        self.cost_history: Dict[str, List[float]] = defaultdict(list)
        self.max_history_size = 1000
    
    def record_request(
        self,
        provider: str,
        latency: float,
        cost: float,
        success: bool,
        quality_score: Optional[float] = None
    ):
        """Записать результат запроса"""
        
        # Инициализация если нужно
        if provider not in self.stats:
            self.stats[provider] = ProviderStats(
                avg_latency=latency,
                p95_latency=latency,
                p99_latency=latency,
                cost_per_request=cost,
                quality_score=quality_score or 0.8,
                availability=1.0 if success else 0.0,
                error_rate=0.0 if success else 1.0,
                total_requests=1,
                successful_requests=1 if success else 0,
                failed_requests=0 if success else 1,
                last_success_time=time.time() if success else 0,
                last_failure_time=0 if success else time.time()
            )
            return
        
        # Обновление статистики
        stats = self.stats[provider]
        stats.total_requests += 1
        
        if success:
            stats.successful_requests += 1
            stats.last_success_time = time.time()
        else:
            stats.failed_requests += 1
            stats.last_failure_time = time.time()
        
        # Добавить в историю
        self.latency_history[provider].append(latency)
        self.cost_history[provider].append(cost)
        
        # Ограничить размер истории
        if len(self.latency_history[provider]) > self.max_history_size:
            self.latency_history[provider] = self.latency_history[provider][-self.max_history_size:]
        if len(self.cost_history[provider]) > self.max_history_size:
            self.cost_history[provider] = self.cost_history[provider][-self.max_history_size:]
        
        # Пересчитать метрики
        latencies = self.latency_history[provider]
        costs = self.cost_history[provider]
        
        stats.avg_latency = sum(latencies) / len(latencies)
        stats.p95_latency = self._percentile(latencies, 95)
        stats.p99_latency = self._percentile(latencies, 99)
        stats.cost_per_request = sum(costs) / len(costs)
        stats.error_rate = stats.failed_requests / stats.total_requests
        stats.availability = stats.successful_requests / stats.total_requests
        
        if quality_score is not None:
            # Exponential moving average для качества
            alpha = 0.1
            stats.quality_score = alpha * quality_score + (1 - alpha) * stats.quality_score
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Вычислить перцентиль"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100.0))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_stats(self, provider: str) -> Optional[ProviderStats]:
        """Получить статистику провайдера"""
        return self.stats.get(provider)
    
    def get_all_stats(self) -> Dict[str, ProviderStats]:
        """Получить статистику всех провайдеров"""
        return self.stats.copy()


# ============================================================================
# INTELLIGENT ROUTER
# ============================================================================

class IntelligentRouter:
    """Интеллектуальный роутер с поддержкой различных стратегий"""
    
    def __init__(
        self,
        strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        stats_tracker: Optional[ProviderStatsTracker] = None
    ):
        self.strategy = strategy
        self.stats_tracker = stats_tracker or ProviderStatsTracker()
        self.circuit_breaker_manager = get_circuit_breaker_manager()
        
        # Веса для balanced стратегии
        self.balanced_weights = {
            'latency': 0.30,
            'cost': 0.30,
            'quality': 0.25,
            'availability': 0.15
        }
    
    def set_strategy(self, strategy: RoutingStrategy):
        """Изменить стратегию маршрутизации"""
        self.strategy = strategy
        log.info("routing_strategy_changed", strategy=strategy.value)
    
    async def select_provider(
        self,
        providers: List[str],
        request_type: str,
        user_preferences: Optional[Dict] = None
    ) -> Tuple[str, List[ProviderScore]]:
        """
        Выбрать провайдера на основе стратегии
        
        Args:
            providers: Список доступных провайдеров
            request_type: Тип запроса (text, image, audio, video)
            user_preferences: Пользовательские предпочтения
        
        Returns:
            Tuple[выбранный провайдер, список всех оценок]
        """
        start_time = time.time()
        
        # Фильтровать только доступные провайдеры
        available_providers = [
            p for p in providers
            if self.circuit_breaker_manager.is_available(p)
        ]
        
        if not available_providers:
            log.error(
                "no_available_providers",
                requested_providers=providers
            )
            raise Exception("No available providers")
        
        # Вычислить оценки для каждого провайдера
        scores = []
        for provider in available_providers:
            stats = self.stats_tracker.get_stats(provider)
            
            # Использовать дефолтные значения если нет статистики
            if stats is None:
                stats = ProviderStats(
                    avg_latency=1.0,
                    p95_latency=2.0,
                    p99_latency=3.0,
                    cost_per_request=0.1,
                    quality_score=0.8,
                    availability=1.0,
                    error_rate=0.0,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    last_success_time=time.time(),
                    last_failure_time=0
                )
            
            # Вычислить score по выбранной стратегии
            if self.strategy == RoutingStrategy.LATENCY_AWARE:
                score = self._calculate_latency_score(stats)
                reason = f"Low latency: {stats.avg_latency:.2f}s"
            
            elif self.strategy == RoutingStrategy.COST_AWARE:
                score = self._calculate_cost_score(stats)
                reason = f"Low cost: ${stats.cost_per_request:.4f}"
            
            elif self.strategy == RoutingStrategy.QUALITY_AWARE:
                score = self._calculate_quality_score(stats)
                reason = f"High quality: {stats.quality_score:.2f}"
            
            elif self.strategy == RoutingStrategy.AVAILABILITY:
                score = stats.availability
                reason = f"Availability: {stats.availability:.2%}"
            
            else:  # BALANCED
                score = self._calculate_balanced_score(stats)
                reason = self._get_balanced_reason(stats)
            
            scores.append(ProviderScore(
                provider=provider,
                score=score,
                latency=stats.avg_latency,
                cost=stats.cost_per_request,
                quality=stats.quality_score,
                availability=stats.availability,
                reason=reason,
                metadata={
                    'p95_latency': stats.p95_latency,
                    'p99_latency': stats.p99_latency,
                    'error_rate': stats.error_rate,
                    'total_requests': stats.total_requests
                }
            ))
        
        # Сортировать по score (descending)
        scores.sort(key=lambda x: x.score, reverse=True)
        selected = scores[0]
        
        # Записать метрики
        duration = time.time() - start_time
        routing_decision_duration_seconds.labels(
            strategy=self.strategy.value
        ).observe(duration)
        
        routing_decisions_total.labels(
            strategy=self.strategy.value,
            selected_provider=selected.provider
        ).inc()
        
        # Логировать решение и альтернативы
        log.info(
            "routing_decision",
            strategy=self.strategy.value,
            selected_provider=selected.provider,
            score=selected.score,
            reason=selected.reason,
            latency=selected.latency,
            cost=selected.cost,
            quality=selected.quality,
            availability=selected.availability,
            alternatives=[
                {
                    "provider": s.provider,
                    "score": s.score,
                    "reason": s.reason,
                    "latency": s.latency,
                    "cost": s.cost
                }
                for s in scores[1:3]  # Топ-2 альтернативы
            ],
            duration_ms=duration * 1000
        )
        
        return selected.provider, scores
    
    def _calculate_latency_score(self, stats: ProviderStats) -> float:
        """Вычислить score для latency-aware стратегии"""
        # Чем меньше latency, тем выше score
        # Используем p95 latency для более стабильной оценки
        max_acceptable_latency = 10.0  # секунд
        normalized_latency = min(stats.p95_latency / max_acceptable_latency, 1.0)
        
        # Инвертировать (меньше = лучше)
        latency_score = 1.0 - normalized_latency
        
        # Учесть availability
        return latency_score * stats.availability
    
    def _calculate_cost_score(self, stats: ProviderStats) -> float:
        """Вычислить score для cost-aware стратегии"""
        # Чем меньше стоимость, тем выше score
        max_cost = 1.0  # максимальная стоимость за запрос
        normalized_cost = min(stats.cost_per_request / max_cost, 1.0)
        
        # Инвертировать (меньше = лучше)
        cost_score = 1.0 - normalized_cost
        
        # Учесть availability и quality (минимальные требования)
        if stats.availability < 0.95 or stats.quality_score < 0.7:
            cost_score *= 0.5  # Штраф за низкую доступность/качество
        
        return cost_score
    
    def _calculate_quality_score(self, stats: ProviderStats) -> float:
        """Вычислить score для quality-aware стратегии"""
        # Качество напрямую = score
        quality_score = stats.quality_score
        
        # Штраф за высокую latency
        if stats.avg_latency > 5.0:
            quality_score *= 0.9
        
        # Учесть availability
        return quality_score * stats.availability
    
    def _calculate_balanced_score(self, stats: ProviderStats) -> float:
        """Вычислить score для balanced стратегии"""
        weights = self.balanced_weights
        
        # Нормализовать все метрики в диапазон [0, 1]
        normalized_latency = 1.0 - min(stats.avg_latency / 10.0, 1.0)  # Меньше = лучше
        normalized_cost = 1.0 - min(stats.cost_per_request / 1.0, 1.0)  # Меньше = лучше
        normalized_quality = stats.quality_score  # Уже в [0, 1]
        normalized_availability = stats.availability  # Уже в [0, 1]
        
        # Взвешенная сумма
        score = (
            normalized_latency * weights['latency'] +
            normalized_cost * weights['cost'] +
            normalized_quality * weights['quality'] +
            normalized_availability * weights['availability']
        )
        
        return score
    
    def _get_balanced_reason(self, stats: ProviderStats) -> str:
        """Получить объяснение для balanced стратегии"""
        reasons = []
        
        if stats.avg_latency < 1.0:
            reasons.append("fast")
        if stats.cost_per_request < 0.05:
            reasons.append("cheap")
        if stats.quality_score > 0.9:
            reasons.append("high-quality")
        if stats.availability > 0.99:
            reasons.append("reliable")
        
        if not reasons:
            reasons.append("balanced")
        
        return f"Balanced: {', '.join(reasons)}"
    
    def record_result(
        self,
        provider: str,
        latency: float,
        cost: float,
        success: bool,
        quality_score: Optional[float] = None
    ):
        """
        Записать результат запроса для обновления статистики
        
        Args:
            provider: Провайдер
            latency: Задержка в секундах
            cost: Стоимость запроса
            success: Успешно ли выполнен запрос
            quality_score: Оценка качества (опционально)
        """
        self.stats_tracker.record_request(
            provider=provider,
            latency=latency,
            cost=cost,
            success=success,
            quality_score=quality_score
        )
        
        log.debug(
            "routing_result_recorded",
            provider=provider,
            latency=latency,
            cost=cost,
            success=success,
            quality_score=quality_score
        )


# ============================================================================
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ============================================================================

_intelligent_router: Optional[IntelligentRouter] = None


def get_intelligent_router(
    strategy: RoutingStrategy = RoutingStrategy.BALANCED
) -> IntelligentRouter:
    """Получить глобальный экземпляр IntelligentRouter"""
    global _intelligent_router
    if _intelligent_router is None:
        _intelligent_router = IntelligentRouter(strategy=strategy)
    return _intelligent_router
