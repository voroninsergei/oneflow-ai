"""
Test module for the PricingCalculator class in OneFlow.AI.

English:
This module contains unit tests for the PricingCalculator class, verifying registration of rates and cost estimation across multiple providers.

Русская версия:
Этот модуль содержит юниттесты для класса PricingCalculator: проверяет регистрацию тарифов и расчет стоимости для нескольких провайдеров.
"""

import os
import sys
import pytest

# Ensure that src modules can be imported when running tests directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from pricing import PricingCalculator


def test_register_and_estimate_multiple_providers():
    """English: Test registering rates for multiple providers and estimating cost.

    Русская версия:
    Тест регистрации тарифов для нескольких провайдеров и расчёта стоимости.
    """
    pc = PricingCalculator()
    # Register two providers: GPT (cost per word) and image (cost per image)
    pc.register_rate("gpt", 0.05)
    pc.register_rate("image", 10)

    # Test cost estimation for GPT: 100 words -> 100 * 0.05 = 5.0
    assert pc.estimate_cost("gpt", 100) == pytest.approx(5.0)
    # Test cost estimation for image provider: 3 images -> 3 * 10 = 30
    assert pc.estimate_cost("image", 3) == pytest.approx(30.0)


def test_unknown_provider_returns_none():
    """English: Ensure that requesting cost for an unregistered provider returns None.

    Русская версия:
    Убедитесь, что запрос стоимости для незарегистрированного провайдера возвращает None.
    """
    pc = PricingCalculator()
    pc.register_rate("gpt", 0.05)
    # Request cost for a provider that has not been registered
    assert pc.estimate_cost("unknown", 50) is None
