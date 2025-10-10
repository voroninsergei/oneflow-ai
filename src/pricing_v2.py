"""
Token-based Pricing System v2
Точное биллингование на основе токенов (input/output) с нормализацией к кредитам
"""
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP

import structlog

logger = structlog.get_logger()


class ProviderModel(Enum):
    """Модели провайдеров"""
    # OpenAI
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    
    # Stability AI
    STABLE_DIFFUSION_XL = "stable-diffusion-xl"
    STABLE_DIFFUSION_3 = "stable-diffusion-3"
    
    # ElevenLabs
    ELEVEN_MULTILINGUAL_V2 = "eleven-multilingual-v2"


@dataclass
class TokenPricing:
    """
    Ценообразование на основе токенов
    
    Цены указаны в USD за 1M токенов согласно официальным прайсам провайдеров
    """
    model: ProviderModel
    input_price_per_1m: Decimal  # USD за 1M input токенов
    output_price_per_1m: Decimal  # USD за 1M output токенов
    credits_per_usd: Decimal = Decimal("100")  # 1 USD = 100 кредитов
    
    # Метаданные
    provider: str = ""
    modality: Literal["text", "image", "audio", "video"] = "text"
    context_window: int = 0
    
    def __post_init__(self):
        """Конвертация в Decimal для точности"""
        self.input_price_per_1m = Decimal(str(self.input_price_per_1m))
        self.output_price_per_1m = Decimal(str(self.output_price_per_1m))
        self.credits_per_usd = Decimal(str(self.credits_per_usd))
    
    def calculate_credits(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> Decimal:
        """
        Расчёт кредитов на основе токенов
        
        Formula: 
        cost_usd = (input_tokens / 1M * input_price) + (output_tokens / 1M * output_price)
        credits = cost_usd * credits_per_usd
        """
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token counts must be non-negative")
        
        # Расчёт стоимости в USD
        input_cost = (Decimal(input_tokens) / Decimal("1000000")) * self.input_price_per_1m
        output_cost = (Decimal(output_tokens) / Decimal("1000000")) * self.output_price_per_1m
        total_cost_usd = input_cost + output_cost
        
        # Конвертация в кредиты
        credits = (total_cost_usd * self.credits_per_usd).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
        
        logger.debug(
            "token_pricing_calculated",
            model=self.model.value,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=float(total_cost_usd),
            credits=float(credits)
        )
        
        return credits


# ===== Pricing Catalog =====
# Цены актуальны на январь 2025, источник: официальные сайты провайдеров

PRICING_CATALOG: Dict[ProviderModel, TokenPricing] = {
    # OpenAI Models
    ProviderModel.GPT_4O: TokenPricing(
        model=ProviderModel.GPT_4O,
        input_price_per_1m=Decimal("2.50"),
        output_price_per_1m=Decimal("10.00"),
        provider="openai",
        modality="text",
        context_window=128000
    ),
    ProviderModel.GPT_4_TURBO: TokenPricing(
        model=ProviderModel.GPT_4_TURBO,
        input_price_per_1m=Decimal("10.00"),
        output_price_per_1m=Decimal("30.00"),
        provider="openai",
        modality="text",
        context_window=128000
    ),
    ProviderModel.GPT_4: TokenPricing(
        model=ProviderModel.GPT_4,
        input_price_per_1m=Decimal("30.00"),
        output_price_per_1m=Decimal("60.00"),
        provider="openai",
        modality="text",
        context_window=8192
    ),
    ProviderModel.GPT_35_TURBO: TokenPricing(
        model=ProviderModel.GPT_35_TURBO,
        input_price_per_1m=Decimal("0.50"),
        output_price_per_1m=Decimal("1.50"),
        provider="openai",
        modality="text",
        context_window=16385
    ),
    
    # Anthropic Claude
    ProviderModel.CLAUDE_3_OPUS: TokenPricing(
        model=ProviderModel.CLAUDE_3_OPUS,
        input_price_per_1m=Decimal("15.00"),
        output_price_per_1m=Decimal("75.00"),
        provider="anthropic",
        modality="text",
        context_window=200000
    ),
    ProviderModel.CLAUDE_3_SONNET: TokenPricing(
        model=ProviderModel.CLAUDE_3_SONNET,
        input_price_per_1m=Decimal("3.00"),
        output_price_per_1m=Decimal("15.00"),
        provider="anthropic",
        modality="text",
        context_window=200000
    ),
    ProviderModel.CLAUDE_3_HAIKU: TokenPricing(
        model=ProviderModel.CLAUDE_3_HAIKU,
        input_price_per_1m=Decimal("0.25"),
        output_price_per_1m=Decimal("1.25"),
        provider="anthropic",
        modality="text",
        context_window=200000
    ),
    
    # Image Models (используем эквивалент токенов)
    ProviderModel.STABLE_DIFFUSION_XL: TokenPricing(
        model=ProviderModel.STABLE_DIFFUSION_XL,
        input_price_per_1m=Decimal("0"),  # Фиксированная цена за изображение
        output_price_per_1m=Decimal("4000"),  # $0.004 per image = $4 per 1000 images
        provider="stability",
        modality="image",
        context_window=0
    ),
    
    # Audio Models
    ProviderModel.ELEVEN_MULTILINGUAL_V2: TokenPricing(
        model=ProviderModel.ELEVEN_MULTILINGUAL_V2,
        input_price_per_1m=Decimal("0"),
        output_price_per_1m=Decimal("30000"),  # $0.30 per 1000 chars = $30 per 1M chars
        provider="elevenlabs",
        modality="audio",
        context_window=0
    ),
}


class PricingEngine:
    """
    Движок для расчёта стоимости запросов
    """
    
    def __init__(self, catalog: Dict[ProviderModel, TokenPricing] = PRICING_CATALOG):
        self.catalog = catalog
    
    def estimate_cost(
        self,
        model: ProviderModel,
        input_tokens: int,
        output_tokens: int
    ) -> Decimal:
        """
        Оценка стоимости запроса в кредитах
        
        Returns:
            Decimal: стоимость в кредитах
        """
        if model not in self.catalog:
            raise ValueError(f"Unknown model: {model}")
        
        pricing = self.catalog[model]
        return pricing.calculate_credits(input_tokens, output_tokens)
    
    def compare_models(
        self,
        input_tokens: int,
        output_tokens: int,
        models: Optional[list[ProviderModel]] = None
    ) -> Dict[ProviderModel, Decimal]:
        """
        Сравнение стоимости для разных моделей
        
        Returns:
            Dict с моделями и их стоимостью в порядке возрастания
        """
        if models is None:
            models = list(self.catalog.keys())
        
        costs = {}
        for model in models:
            if model in self.catalog:
                costs[model] = self.estimate_cost(model, input_tokens, output_tokens)
        
        # Сортировка по стоимости
        return dict(sorted(costs.items(), key=lambda x: x[1]))
    
    def get_cheapest_model(
        self,
        input_tokens: int,
        output_tokens: int,
        modality: Literal["text", "image", "audio", "video"] = "text"
    ) -> tuple[ProviderModel, Decimal]:
        """
        Найти самую дешёвую модель для заданной модальности
        
        Returns:
            (модель, стоимость в кредитах)
        """
        relevant_models = [
            m for m, p in self.catalog.items()
            if p.modality == modality
        ]
        
        if not relevant_models:
            raise ValueError(f"No models found for modality: {modality}")
        
        costs = self.compare_models(input_tokens, output_tokens, relevant_models)
        cheapest_model = min(costs, key=costs.get)
        
        return cheapest_model, costs[cheapest_model]


class RoutingStrategy(Enum):
    """Стратегии маршрутизации"""
    COST_OPTIMIZED = "cost"        # Минимизация стоимости
    LATENCY_OPTIMIZED = "latency"  # Минимизация задержки
    QUALITY_OPTIMIZED = "quality"  # Максимум качества
    BALANCED = "balanced"           # Баланс между всеми факторами


@dataclass
class RoutingDecision:
    """Решение о маршрутизации запроса"""
    primary_model: ProviderModel
    fallback_chain: list[ProviderModel]
    estimated_credits: Decimal
    strategy: RoutingStrategy
    reasoning: str


class IntelligentRouter:
    """
    Умный роутер с выбором провайдера на основе стратегии
    """
    
    # Латентность моделей (среднее время ответа в секундах)
    LATENCY_MAP = {
        ProviderModel.GPT_35_TURBO: 1.5,
        ProviderModel.GPT_4O: 2.0,
        ProviderModel.CLAUDE_3_HAIKU: 1.8,
        ProviderModel.CLAUDE_3_SONNET: 2.5,
        ProviderModel.GPT_4_TURBO: 3.0,
        ProviderModel.CLAUDE_3_OPUS: 4.0,
        ProviderModel.GPT_4: 4.5,
    }
    
    # Качество моделей (субъективная оценка 1-10)
    QUALITY_MAP = {
        ProviderModel.GPT_4: 10,
        ProviderModel.CLAUDE_3_OPUS: 10,
        ProviderModel.GPT_4_TURBO: 9,
        ProviderModel.GPT_4O: 9,
        ProviderModel.CLAUDE_3_SONNET: 8,
        ProviderModel.CLAUDE_3_HAIKU: 7,
        ProviderModel.GPT_35_TURBO: 6,
    }
    
    def __init__(self, pricing_engine: PricingEngine):
        self.pricing_engine = pricing_engine
    
    def route(
        self,
        input_tokens: int,
        output_tokens: int,
        strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        modality: Literal["text", "image", "audio", "video"] = "text"
    ) -> RoutingDecision:
        """
        Выбор оптимальной модели и fallback chain
        """
        
        if strategy == RoutingStrategy.COST_OPTIMIZED:
            return self._route_by_cost(input_tokens, output_tokens, modality)
        
        elif strategy == RoutingStrategy.LATENCY_OPTIMIZED:
            return self._route_by_latency(input_tokens, output_tokens, modality)
        
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            return self._route_by_quality(input_tokens, output_tokens, modality)
        
        else:  # BALANCED
            return self._route_balanced(input_tokens, output_tokens, modality)
    
    def _route_by_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        modality: str
    ) -> RoutingDecision:
        """Оптимизация по стоимости"""
        models = [
            m for m, p in self.pricing_engine.catalog.items()
            if p.modality == modality
        ]
        
        costs = self.pricing_engine.compare_models(input_tokens, output_tokens, models)
        sorted_models = list(costs.keys())
        
        return RoutingDecision(
            primary_model=sorted_models[0],
            fallback_chain=sorted_models[1:3],
            estimated_credits=costs[sorted_models[0]],
            strategy=RoutingStrategy.COST_OPTIMIZED,
            reasoning="Selected cheapest model"
        )
    
    def _route_by_latency(
        self,
        input_tokens: int,
        output_tokens: int,
        modality: str
    ) -> RoutingDecision:
        """Оптимизация по скорости"""
        models = [
            m for m in self.LATENCY_MAP.keys()
            if self.pricing_engine.catalog[m].modality == modality
        ]
        
        sorted_models = sorted(models, key=lambda m: self.LATENCY_MAP[m])
        primary = sorted_models[0]
        cost = self.pricing_engine.estimate_cost(primary, input_tokens, output_tokens)
        
        return RoutingDecision(
            primary_model=primary,
            fallback_chain=sorted_models[1:3],
            estimated_credits=cost,
            strategy=RoutingStrategy.LATENCY_OPTIMIZED,
            reasoning=f"Fastest model with {self.LATENCY_MAP[primary]}s latency"
        )
    
    def _route_by_quality(
        self,
        input_tokens: int,
        output_tokens: int,
        modality: str
    ) -> RoutingDecision:
        """Оптимизация по качеству"""
        models = [
            m for m in self.QUALITY_MAP.keys()
            if self.pricing_engine.catalog[m].modality == modality
        ]
        
        sorted_models = sorted(models, key=lambda m: self.QUALITY_MAP[m], reverse=True)
        primary = sorted_models[0]
        cost = self.pricing_engine.estimate_cost(primary, input_tokens, output_tokens)
        
        return RoutingDecision(
            primary_model=primary,
            fallback_chain=sorted_models[1:3],
            estimated_credits=cost,
            strategy=RoutingStrategy.QUALITY_OPTIMIZED,
            reasoning=f"Highest quality model (score: {self.QUALITY_MAP[primary]}/10)"
        )
    
    def _route_balanced(
        self,
        input_tokens: int,
        output_tokens: int,
        modality: str
    ) -> RoutingDecision:
        """Сбалансированный выбор"""
        # Нормализация метрик и взвешенная оценка
        models = [
            m for m in self.pricing_engine.catalog.keys()
            if self.pricing_engine.catalog[m].modality == modality
            and m in self.QUALITY_MAP
            and m in self.LATENCY_MAP
        ]
        
        scores = {}
        for model in models:
            cost = float(self.pricing_engine.estimate_cost(model, input_tokens, output_tokens))
            latency = self.LATENCY_MAP[model]
            quality = self.QUALITY_MAP[model]
            
            # Нормализация (0-1) и взвешенная сумма
            # Веса: cost=0.4, latency=0.3, quality=0.3
            normalized_score = (
                0.4 * (1 / (cost + 1)) +
                0.3 * (1 / latency) +
                0.3 * (quality / 10)
            )
            scores[model] = normalized_score
        
        sorted_models = sorted(models, key=lambda m: scores[m], reverse=True)
        primary = sorted_models[0]
        cost = self.pricing_engine.estimate_cost(primary, input_tokens, output_tokens)
        
        return RoutingDecision(
            primary_model=primary,
            fallback_chain=sorted_models[1:3],
            estimated_credits=cost,
            strategy=RoutingStrategy.BALANCED,
            reasoning="Balanced approach considering cost, latency, and quality"
        )
