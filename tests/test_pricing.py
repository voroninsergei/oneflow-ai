"""
Unit tests for the PricingCalculator class in OneFlow.AI.

English:
This test module verifies the basic functionality of the PricingCalculator class, including registering rates and estimating cost in tokens.

Русская версия:
Данный модуль тестирует функциональность класса PricingCalculator, включая регистрацию тарифов и оценку стоимости в токенах.
"""

import os
import sys
import pytest

# Adjust the path so that src modules can be imported when running tests directly
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pricing import PricingCalculator


def test_pricing_register_and_estimate():
    """Test registering rates and estimating costs."""
    pricing = PricingCalculator()
    # Register rates: 0.5 token per word for GPT and 10 tokens per image
    pricing.register_rate("gpt", 0.5)
    pricing.register_rate("image", 10)
    # GPT cost: 5 words -> 2.5 tokens
    assert pricing.estimate_cost("gpt", 5) == pytest.approx(2.5)
    # Image cost: 2 images -> 20 tokens
    assert pricing.estimate_cost("image", 2) == 20
    # Unknown model should return 0 cost
    assert pricing.estimate_cost("unknown", 1) == 0
