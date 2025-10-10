"""
Unit tests for Budget and Pricing modules
Юнит-тесты для модулей бюджета и ценообразования
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from budget import Budget, BudgetPeriod
from pricing_tables import (
    calculate_cost_in_credits,
    get_model_info,
    estimate_tokens_from_text,
    convert_legacy_request,
    PROVIDER_PRICING
)


@pytest.mark.unit
@pytest.mark.budget
class TestBudgetIntegration:
    """Integration tests for budget with pricing"""

    def test_budget_with_pricing_calculation(self):
        """Test budget integration with real pricing"""
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 1000.0)
        
        # Calculate cost for GPT-3.5 request
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 1000, 500)
        
        can_spend, reason = budget.can_spend(cost)
        assert can_spend is True
        
        budget.record_spending(cost)
        assert budget.get_spent(BudgetPeriod.DAILY) == cost

    def test_budget_prevents_overspending(self):
        """Test budget prevents overspending based on pricing"""
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 100.0)
        
        # Try to spend more than limit
        expensive_cost = calculate_cost_in_credits("anthropic", "claude-3-opus", 10000, 5000)
        
        can_spend, reason = budget.can_spend(expensive_cost)
        assert can_spend is False
        assert "limit exceeded" in reason.lower()

    def test_provider_budget_with_pricing(self):
        """Test provider-specific budget with pricing"""
        budget = Budget()
        budget.set_provider_limit('openai', 500.0)
        
        # Calculate multiple GPT costs
        cost1 = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 1000, 500)
        cost2 = calculate_cost_in_credits("openai", "gpt-4", 1000, 500)
        
        budget.record_spending(cost1, provider='openai')
        can_spend, _ = budget.can_spend(cost2, provider='openai')
        
        # Check if within limit
        total = cost1 + cost2
        assert can_spend == (total <= 500.0)

    def test_multi_provider_budget_tracking(self):
        """Test tracking budgets across multiple providers"""
        budget = Budget()
        budget.set_provider_limit('openai', 1000.0)
        budget.set_provider_limit('anthropic', 2000.0)
        
        gpt_cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 2000, 1000)
        claude_cost = calculate_cost_in_credits("anthropic", "claude-3-haiku", 2000, 1000)
        
        budget.record_spending(gpt_cost, provider='openai')
        budget.record_spending(claude_cost, provider='anthropic')
        
        assert budget.get_provider_spent('openai') == gpt_cost
        assert budget.get_provider_spent('anthropic') == claude_cost

    def test_budget_reset_with_accumulated_costs(self):
        """Test budget reset after accumulating costs"""
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 1000.0)
        
        # Accumulate multiple requests
        for _ in range(5):
            cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 500, 250)
            budget.record_spending(cost)
        
        spent = budget.get_spent(BudgetPeriod.DAILY)
        assert spent > 0
        
        budget.reset_period(BudgetPeriod.DAILY)
        assert budget.get_spent(BudgetPeriod.DAILY) == 0.0

    def test_budget_with_legacy_conversion(self):
        """Test budget with legacy request conversion"""
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 500.0)
        
        # Convert legacy request
        provider, model, tokens = convert_legacy_request("gpt", "Hello world test")
        cost = calculate_cost_in_credits(provider, model, tokens, tokens // 2)
        
        can_spend, _ = budget.can_spend(cost)
        assert can_spend is True
        
        budget.record_spending(cost, provider=provider)


@pytest.mark.unit
@pytest.mark.budget
class TestBudgetPeriods:
    """Tests for budget period management"""

    def test_daily_budget_isolation(self):
        """Test daily budget is isolated from weekly"""
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 100.0)
        budget.set_limit(BudgetPeriod.WEEKLY, 500.0)
        
        budget.record_spending(80.0)
        
        assert budget.get_spent(BudgetPeriod.DAILY) == 80.0
        assert budget.get_spent(BudgetPeriod.WEEKLY) == 80.0
        
        # Can't spend 30 more (daily limit)
        can_spend, _ = budget.can_spend(30.0)
        assert can_spend is False

    def test_weekly_budget_accumulation(self):
        """Test weekly budget accumulates daily spending"""
        budget = Budget()
        budget.set_limit(BudgetPeriod.WEEKLY, 500.0)
        
        # Simulate 7 days of spending
        for day in range(7):
            budget.record_spending(50.0)
        
        assert budget.get_spent(BudgetPeriod.WEEKLY) == 350.0

    def test_monthly_budget_tracking(self):
        """Test monthly budget tracking"""
        budget = Budget()
        budget.set_limit(BudgetPeriod.MONTHLY, 2000.0)
        
        # Add spending throughout month
        for _ in range(20):
            budget.record_spending(75.0)
        
        assert budget.get_spent(BudgetPeriod.MONTHLY) == 1500.0
        remaining = budget.get_remaining(BudgetPeriod.MONTHLY)
        assert remaining == 500.0

    def test_total_budget_never_resets(self):
        """Test total budget accumulates forever"""
        budget = Budget()
        
        budget.record_spending(100.0)
        initial_total = budget.get_spent(BudgetPeriod.TOTAL)
        
        budget.reset_period(BudgetPeriod.DAILY)
        budget.reset_period(BudgetPeriod.WEEKLY)
        budget.reset_period(BudgetPeriod.MONTHLY)
        
        assert budget.get_spent(BudgetPeriod.TOTAL) == initial_total


@pytest.mark.unit
@pytest.mark.budget
class TestPricingAccuracy:
    """Tests for pricing calculation accuracy"""

    def test_token_cost_precision(self):
        """Test token cost maintains precision"""
        # Very small number of tokens
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 1, 1)
        assert cost > 0
        assert isinstance(cost, float)

    def test_large_token_cost(self):
        """Test cost calculation for large token counts"""
        cost = calculate_cost_in_credits("openai", "gpt-4-turbo", 100000, 50000)
        assert cost > 1000  # Should be significant
        assert cost < 100000  # But reasonable

    def test_pricing_consistency_across_models(self):
        """Test pricing consistency"""
        models = [
            ("openai", "gpt-3.5-turbo"),
            ("openai", "gpt-4"),
            ("anthropic", "claude-3-haiku"),
            ("anthropic", "claude-3-sonnet")
        ]
        
        tokens_in = 1000
        tokens_out = 500
        
        costs = []
        for provider, model in models:
            cost = calculate_cost_in_credits(provider, model, tokens_in, tokens_out)
            costs.append(cost)
            assert cost > 0
        
        # GPT-3.5 should be cheapest
        assert costs[0] < costs[1]  # 3.5 < 4

    def test_zero_output_tokens(self):
        """Test cost with zero output tokens"""
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 1000, 0)
        assert cost > 0  # Input still costs

    def test_zero_input_tokens(self):
        """Test cost with zero input tokens"""
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 0, 1000)
        assert cost > 0  # Output still costs

    def test_both_zero_tokens(self):
        """Test cost with both zero"""
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 0, 0)
        assert cost == 0.0


@pytest.mark.unit
@pytest.mark.budget
class TestTokenEstimation:
    """Tests for token estimation"""

    def test_estimate_tokens_basic(self):
        """Test basic token estimation"""
        text = "Hello world"
        tokens = estimate_tokens_from_text(text)
        assert tokens > 0
        assert tokens < 10  # Should be ~2-3 tokens

    def test_estimate_tokens_long_text(self):
        """Test token estimation for long text"""
        text = " ".join(["word"] * 1000)
        tokens = estimate_tokens_from_text(text)
        assert tokens > 100
        assert tokens < 2000

    def test_estimate_tokens_empty(self):
        """Test token estimation for empty string"""
        tokens = estimate_tokens_from_text("")
        assert tokens == 0

    def test_estimate_tokens_special_chars(self):
        """Test token estimation with special characters"""
        text = "Hello! How are you? I'm fine."
        tokens = estimate_tokens_from_text(text)
        assert tokens > 5

    def test_estimate_tokens_unicode(self):
        """Test token estimation with unicode"""
        text = "Hello мир 世界"
        tokens = estimate_tokens_from_text(text)
        assert tokens > 0


@pytest.mark.unit
@pytest.mark.budget
class TestLegacyConversion:
    """Tests for legacy request conversion"""

    def test_convert_gpt_legacy(self):
        """Test converting legacy GPT request"""
        provider, model, tokens = convert_legacy_request("gpt", "Test prompt")
        
        assert provider == "openai"
        assert "gpt" in model.lower()
        assert tokens > 0

    def test_convert_image_legacy(self):
        """Test converting legacy image request"""
        provider, model, tokens = convert_legacy_request("image", "A cat")
        
        assert provider == "openai"
        assert "dall-e" in model.lower()
        assert tokens == 1  # Images use 1 token

    def test_convert_audio_legacy(self):
        """Test converting legacy audio request"""
        provider, model, tokens = convert_legacy_request("audio", "Text to speech")
        
        assert provider == "elevenlabs"
        assert tokens == 1

    def test_convert_video_legacy(self):
        """Test converting legacy video request"""
        provider, model, tokens = convert_legacy_request("video", "Video prompt")
        
        assert provider in ["runway", "pika"]
        assert tokens == 1

    def test_convert_invalid_legacy(self):
        """Test converting invalid legacy type"""
        with pytest.raises(ValueError, match="Unknown legacy provider"):
            convert_legacy_request("invalid_type", "content")


@pytest.mark.unit
@pytest.mark.budget
class TestModelInfo:
    """Tests for model information retrieval"""

    def test_get_model_info_gpt(self):
        """Test getting GPT model info"""
        info = get_model_info("openai", "gpt-4")
        
        assert info["provider"] == "openai"
        assert info["model"] == "gpt-4"
        assert "context_window" in info
        assert info["supports_function_calling"] is True

    def test_get_model_info_claude(self):
        """Test getting Claude model info"""
        info = get_model_info("anthropic", "claude-3-opus")
        
        assert info["provider"] == "anthropic"
        assert info["supports_vision"] is True
        assert info["context_window"] == 200000

    def test_get_model_info_vision(self):
        """Test vision-capable models"""
        gpt4o_info = get_model_info("openai", "gpt-4o")
        assert gpt4o_info["supports_vision"] is True
        
        gpt35_info = get_model_info("openai", "gpt-3.5-turbo")
        assert gpt35_info["supports_vision"] is False

    def test_get_model_info_invalid(self):
        """Test getting info for invalid model"""
        with pytest.raises(ValueError):
            get_model_info("openai", "invalid-model")
