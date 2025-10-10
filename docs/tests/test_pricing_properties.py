"""
Property-based тесты для системы ценообразования
Используем Hypothesis для генерации тестовых данных
"""
from decimal import Decimal
import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis import HealthCheck

import sys
sys.path.insert(0, '../src')

from pricing_v2 import (
    TokenPricing,
    PricingEngine,
    ProviderModel,
    PRICING_CATALOG,
    IntelligentRouter,
    RoutingStrategy
)


# ===== Property Tests для TokenPricing =====

@given(
    input_tokens=st.integers(min_value=0, max_value=1000000),
    output_tokens=st.integers(min_value=0, max_value=1000000)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_pricing_always_non_negative(input_tokens, output_tokens):
    """
    Property: Стоимость всегда >= 0
    """
    pricing = TokenPricing(
        model=ProviderModel.GPT_4,
        input_price_per_1m=Decimal("30.00"),
        output_price_per_1m=Decimal("60.00")
    )
    
    credits = pricing.calculate_credits(input_tokens, output_tokens)
    assert credits >= 0, f"Cost must be non-negative, got {credits}"


@given(
    tokens=st.integers(min_value=1, max_value=100000)
)
def test_pricing_monotonic_input(tokens):
    """
    Property: При увеличении input токенов стоимость не уменьшается
    """
    pricing = TokenPricing(
        model=ProviderModel.GPT_4,
        input_price_per_1m=Decimal("30.00"),
        output_price_per_1m=Decimal("60.00")
    )
    
    cost1 = pricing.calculate_credits(tokens, 100)
    cost2 = pricing.calculate_credits(tokens + 1, 100)
    
    assert cost2 >= cost1, "Cost must be monotonic with input tokens"


@given(
    tokens=st.integers(min_value=1, max_value=100000)
)
def test_pricing_monotonic_output(tokens):
    """
    Property: При увеличении output токенов стоимость не уменьшается
    """
    pricing = TokenPricing(
        model=ProviderModel.GPT_4,
        input_price_per_1m=Decimal("30.00"),
        output_price_per_1m=Decimal("60.00")
    )
    
    cost1 = pricing.calculate_credits(100, tokens)
    cost2 = pricing.calculate_credits(100, tokens + 1)
    
    assert cost2 >= cost1, "Cost must be monotonic with output tokens"


@given(
    input_tokens=st.integers(min_value=0, max_value=10000),
    output_tokens=st.integers(min_value=0, max_value=10000)
)
def test_pricing_additive(input_tokens, output_tokens):
    """
    Property: Стоимость аддитивна - cost(a+b) = cost(a) + cost(b)
    """
    pricing = TokenPricing(
        model=ProviderModel.GPT_4,
        input_price_per_1m=Decimal("30.00"),
        output_price_per_1m=Decimal("60.00")
    )
    
    # Разбиваем на два запроса
    split_point_input = input_tokens // 2
    split_point_output = output_tokens // 2
    
    # Стоимость полного запроса
    total_cost = pricing.calculate_credits(input_tokens, output_tokens)
    
    # Стоимость двух частей
    cost_part1 = pricing.calculate_credits(split_point_input, split_point_output)
    cost_part2 = pricing.calculate_credits(
        input_tokens - split_point_input,
        output_tokens - split_point_output
    )
    
    # Допускаем погрешность округления ±0.02 кредита
    assert abs(total_cost - (cost_part1 + cost_part2)) <= Decimal("0.02"), \
        "Pricing should be additive (within rounding error)"


@given(
    scale=st.integers(min_value=1, max_value=100)
)
def test_pricing_scaling(scale):
    """
    Property: Стоимость линейно масштабируется
    cost(n * tokens) = n * cost(tokens)
    """
    pricing = TokenPricing(
        model=ProviderModel.GPT_4,
        input_price_per_1m=Decimal("30.00"),
        output_price_per_1m=Decimal("60.00")
    )
    
    base_input, base_output = 100, 200
    
    single_cost = pricing.calculate_credits(base_input, base_output)
    scaled_cost = pricing.calculate_credits(base_input * scale, base_output * scale)
    expected_scaled = single_cost * scale
    
    # Допускаем погрешность округления
    assert abs(scaled_cost - expected_scaled) <= Decimal("0.02") * scale, \
        f"Scaling property failed: {scaled_cost} != {expected_scaled}"


def test_pricing_zero_tokens():
    """
    Property: Нулевые токены = нулевая стоимость
    """
    pricing = TokenPricing(
        model=ProviderModel.GPT_4,
        input_price_per_1m=Decimal("30.00"),
        output_price_per_1m=Decimal("60.00")
    )
    
    assert pricing.calculate_credits(0, 0) == 0
    assert pricing.calculate_credits(0, 100) >= 0
    assert pricing.calculate_credits(100, 0) >= 0


# ===== Property Tests для PricingEngine =====

@given(
    input_tokens=st.integers(min_value=1, max_value=10000),
    output_tokens=st.integers(min_value=1, max_value=10000)
)
def test_compare_models_ordering(input_tokens, output_tokens):
    """
    Property: compare_models возвращает модели в порядке возрастания цены
    """
    engine = PricingEngine()
    
    text_models = [
        m for m, p in PRICING_CATALOG.items()
        if p.modality == "text"
    ]
    
    if len(text_models) < 2:
        pytest.skip("Need at least 2 text models")
    
    comparison = engine.compare_models(input_tokens, output_tokens, text_models)
    costs = list(comparison.values())
    
    # Проверка, что список отсортирован по возрастанию
    assert costs == sorted(costs), "Models should be ordered by cost"


@given(
    input_tokens=st.integers(min_value=1, max_value=10000),
    output_tokens=st.integers(min_value=1, max_value=10000)
)
def test_cheapest_model_is_actually_cheapest(input_tokens, output_tokens):
    """
    Property: get_cheapest_model действительно возвращает самую дешёвую модель
    """
    engine = PricingEngine()
    
    cheapest_model, cheapest_cost = engine.get_cheapest_model(
        input_tokens, output_tokens, modality="text"
    )
    
    # Проверяем все текстовые модели
    text_models = [
        m for m, p in PRICING_CATALOG.items()
        if p.modality == "text"
    ]
    
    for model in text_models:
        cost = engine.estimate_cost(model, input_tokens, output_tokens)
        assert cheapest_cost <= cost, \
            f"Found cheaper model {model}: {cost} < {cheapest_cost}"


# ===== Property Tests для IntelligentRouter =====

@given(
    input_tokens=st.integers(min_value=100, max_value=10000),
    output_tokens=st.integers(min_value=100, max_value=10000),
    strategy=st.sampled_from(list(RoutingStrategy))
)
def test_router_always_returns_valid_decision(input_tokens, output_tokens, strategy):
    """
    Property: Роутер всегда возвращает валидное решение
    """
    engine = PricingEngine()
    router = IntelligentRouter(engine)
    
    decision = router.route(input_tokens, output_tokens, strategy, modality="text")
    
    # Проверки валидности
    assert decision.primary_model is not None
    assert isinstance(decision.fallback_chain, list)
    assert decision.estimated_credits >= 0
    assert decision.strategy == strategy
    assert len(decision.reasoning) > 0
    
    # Primary model не должен быть в fallback chain
    assert decision.primary_model not in decision.fallback_chain


@given(
    input_tokens=st.integers(min_value=100, max_value=5000),
    output_tokens=st.integers(min_value=100, max_value=5000)
)
def test_cost_strategy_picks_cheapest(input_tokens, output_tokens):
    """
    Property: COST_OPTIMIZED стратегия выбирает самую дешёвую модель
    """
    engine = PricingEngine()
    router = IntelligentRouter(engine)
    
    decision = router.route(
        input_tokens, 
        output_tokens,
        RoutingStrategy.COST_OPTIMIZED,
        modality="text"
    )
    
    # Проверяем, что выбрана действительно самая дешёвая
    cheapest_model, cheapest_cost = engine.get_cheapest_model(
        input_tokens, output_tokens, modality="text"
    )
    
    assert decision.primary_model == cheapest_model
    assert decision.estimated_credits == cheapest_cost


# ===== Regression Tests =====

def test_known_pricing_gpt4():
    """
    Regression test: Известные значения для GPT-4
    """
    pricing = PRICING_CATALOG[ProviderModel.GPT_4]
    
    # 1000 input + 1000 output токенов
    # input: 1000/1M * $30 = $0.03
    # output: 1000/1M * $60 = $0.06
    # total: $0.09 * 100 credits/USD = 9 credits
    
    cost = pricing.calculate_credits(1000, 1000)
    assert cost == Decimal("9.00"), f"Expected 9.00 credits, got {cost}"


def test_known_pricing_gpt35():
    """
    Regression test: Известные значения для GPT-3.5-turbo
    """
    pricing = PRICING_CATALOG[ProviderModel.GPT_35_TURBO]
    
    # 10000 input + 5000 output токенов
    # input: 10000/1M * $0.50 = $0.005
    # output: 5000/1M * $1.50 = $0.0075
    # total: $0.0125 * 100 = 1.25 credits
    
    cost = pricing.calculate_credits(10000, 5000)
    assert cost == Decimal("1.25"), f"Expected 1.25 credits, got {cost}"


def test_known_pricing_claude_opus():
    """
    Regression test: Claude-3 Opus
    """
    pricing = PRICING_CATALOG[ProviderModel.CLAUDE_3_OPUS]
    
    # 5000 input + 2000 output
    # input: 5000/1M * $15 = $0.075
    # output: 2000/1M * $75 = $0.15
    # total: $0.225 * 100 = 22.50 credits
    
    cost = pricing.calculate_credits(5000, 2000)
    assert cost == Decimal("22.50"), f"Expected 22.50 credits, got {cost}"


# ===== Edge Cases =====

def test_very_large_token_counts():
    """
    Edge case: Очень большие количества токенов
    """
    pricing = PRICING_CATALOG[ProviderModel.GPT_4]
    
    # 10M токенов (больше context window, но математика должна работать)
    cost = pricing.calculate_credits(10_000_000, 10_000_000)
    
    # 10M input: 10 * $30 = $300
    # 10M output: 10 * $60 = $600
    # total: $900 * 100 = 90,000 credits
    
    assert cost == Decimal("90000.00")


def test_asymmetric_token_distribution():
    """
    Edge case: Асимметричное распределение токенов
    """
    pricing = PRICING_CATALOG[ProviderModel.GPT_4]
    
    # Много input, мало output
    cost1 = pricing.calculate_credits(10000, 100)
    
    # Мало input, много output
    cost2 = pricing.calculate_credits(100, 10000)
    
    # Output дороже, поэтому cost2 должен быть больше
    assert cost2 > cost1


def test_decimal_precision():
    """
    Edge case: Проверка точности Decimal
    """
    pricing = PRICING_CATALOG[ProviderModel.GPT_35_TURBO]
    
    # Малое количество токенов
    cost = pricing.calculate_credits(1, 1)
    
    # Должно быть округлено до 2 знаков
    assert cost.as_tuple().exponent == -2


# ===== Integration Tests =====

def test_full_workflow():
    """
    Integration test: Полный workflow от запроса до расчёта
    """
    engine = PricingEngine()
    router = IntelligentRouter(engine)
    
    # Симуляция запроса
    input_tokens = 1500
    output_tokens = 500
    
    # Получение решения о маршрутизации
    decision = router.route(
        input_tokens,
        output_tokens,
        RoutingStrategy.BALANCED,
        modality="text"
    )
    
    # Проверка, что оценка соответствует реальной стоимости
    actual_cost = engine.estimate_cost(
        decision.primary_model,
        input_tokens,
        output_tokens
    )
    
    assert decision.estimated_credits == actual_cost


def test_fallback_chain_uniqueness():
    """
    Integration test: Fallback chain не содержит дубликатов
    """
    engine = PricingEngine()
    router = IntelligentRouter(engine)
    
    decision = router.route(1000, 1000, RoutingStrategy.BALANCED, "text")
    
    all_models = [decision.primary_model] + decision.fallback_chain
    assert len(all_models) == len(set(all_models)), "Fallback chain contains duplicates"


# ===== Parametrized Tests =====

@pytest.mark.parametrize("model", [
    ProviderModel.GPT_4,
    ProviderModel.GPT_4O,
    ProviderModel.GPT_35_TURBO,
    ProviderModel.CLAUDE_3_OPUS,
    ProviderModel.CLAUDE_3_SONNET,
    ProviderModel.CLAUDE_3_HAIKU,
])
def test_all_models_in_catalog(model):
    """
    Parametrized test: Все модели присутствуют в каталоге
    """
    assert model in PRICING_CATALOG
    pricing = PRICING_CATALOG[model]
    assert pricing.input_price_per_1m >= 0
    assert pricing.output_price_per_1m >= 0


@pytest.mark.parametrize("tokens,expected", [
    (0, Decimal("0")),
    (1000, Decimal("9.00")),  # GPT-4: 1k in + 1k out
    (10000, Decimal("90.00")),
    (100000, Decimal("900.00")),
])
def test_gpt4_known_values(tokens, expected):
    """
    Parametrized test: Известные значения для GPT-4
    """
    pricing = PRICING_CATALOG[ProviderModel.GPT_4]
    cost = pricing.calculate_credits(tokens, tokens)
    assert cost == expected


# ===== Performance Tests =====

def test_pricing_calculation_performance():
    """
    Performance test: Расчёт должен быть быстрым
    """
    import time
    
    pricing = PRICING_CATALOG[ProviderModel.GPT_4]
    
    start = time.time()
    for _ in range(10000):
        pricing.calculate_credits(1000, 1000)
    elapsed = time.time() - start
    
    # 10k расчётов должны занимать < 1 секунды
    assert elapsed < 1.0, f"Pricing calculation too slow: {elapsed}s for 10k calculations"


def test_router_decision_performance():
    """
    Performance test: Решение о маршрутизации должно быть быстрым
    """
    import time
    
    engine = PricingEngine()
    router = IntelligentRouter(engine)
    
    start = time.time()
    for _ in range(1000):
        router.route(1000, 1000, RoutingStrategy.BALANCED, "text")
    elapsed = time.time() - start
    
    # 1k решений должны занимать < 1 секунды
    assert elapsed < 1.0, f"Routing too slow: {elapsed}s for 1k decisions"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
