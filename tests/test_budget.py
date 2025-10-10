"""
Tests for Budget module.
Тесты для модуля бюджета.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from budget import Budget, BudgetPeriod


def test_budget_initialization():
    """Test budget initialization."""
    budget = Budget()
    assert budget.get_spent(BudgetPeriod.DAILY) == 0.0
    assert budget.get_spent(BudgetPeriod.WEEKLY) == 0.0
    assert budget.get_spent(BudgetPeriod.MONTHLY) == 0.0
    assert budget.get_spent(BudgetPeriod.TOTAL) == 0.0


def test_set_limit():
    """Test setting budget limit."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    
    assert budget.limits[BudgetPeriod.DAILY] == 100.0


def test_set_multiple_limits():
    """Test setting multiple budget limits."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 50.0)
    budget.set_limit(BudgetPeriod.WEEKLY, 300.0)
    budget.set_limit(BudgetPeriod.MONTHLY, 1000.0)
    
    assert budget.limits[BudgetPeriod.DAILY] == 50.0
    assert budget.limits[BudgetPeriod.WEEKLY] == 300.0
    assert budget.limits[BudgetPeriod.MONTHLY] == 1000.0


def test_negative_limit_raises_error():
    """Test negative limit raises error."""
    budget = Budget()
    
    with pytest.raises(ValueError):
        budget.set_limit(BudgetPeriod.DAILY, -50.0)


def test_zero_limit_allowed():
    """Test zero limit is allowed."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 0.0)
    
    assert budget.limits[BudgetPeriod.DAILY] == 0.0


def test_can_spend_within_limit():
    """Test checking if can spend within limit."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    
    can_spend, reason = budget.can_spend(50.0)
    assert can_spend is True
    assert reason is None


def test_can_spend_exactly_at_limit():
    """Test spending exactly at limit."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    
    can_spend, reason = budget.can_spend(100.0)
    assert can_spend is True
    assert reason is None


def test_cannot_spend_over_limit():
    """Test cannot spend over limit."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    
    can_spend, reason = budget.can_spend(150.0)
    assert can_spend is False
    assert "budget limit exceeded" in reason.lower()


def test_cannot_spend_over_limit_with_existing_spending():
    """Test cannot spend over limit with existing spending."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    budget.record_spending(80.0)
    
    can_spend, reason = budget.can_spend(30.0)
    assert can_spend is False
    assert "budget limit exceeded" in reason.lower()


def test_record_spending():
    """Test recording spending."""
    budget = Budget()
    budget.record_spending(50.0)
    
    assert budget.get_spent(BudgetPeriod.DAILY) == 50.0
    assert budget.get_spent(BudgetPeriod.WEEKLY) == 50.0
    assert budget.get_spent(BudgetPeriod.MONTHLY) == 50.0
    assert budget.get_spent(BudgetPeriod.TOTAL) == 50.0


def test_record_multiple_spending():
    """Test recording multiple spendings."""
    budget = Budget()
    budget.record_spending(20.0)
    budget.record_spending(30.0)
    budget.record_spending(10.0)
    
    assert budget.get_spent(BudgetPeriod.TOTAL) == 60.0


def test_negative_spending_raises_error():
    """Test negative spending raises error."""
    budget = Budget()
    
    with pytest.raises(ValueError):
        budget.record_spending(-10.0)


def test_provider_limit():
    """Test provider-specific limit."""
    budget = Budget()
    budget.set_provider_limit('gpt', 50.0)
    
    can_spend, reason = budget.can_spend(30.0, provider='gpt')
    assert can_spend is True
    assert reason is None


def test_provider_limit_exceeded():
    """Test provider limit exceeded."""
    budget = Budget()
    budget.set_provider_limit('gpt', 50.0)
    budget.record_spending(40.0, provider='gpt')
    
    can_spend, reason = budget.can_spend(20.0, provider='gpt')
    assert can_spend is False
    assert "provider" in reason.lower()


def test_provider_spending_tracked():
    """Test provider spending is tracked."""
    budget = Budget()
    budget.record_spending(30.0, provider='gpt')
    budget.record_spending(20.0, provider='image')
    
    assert budget.get_provider_spent('gpt') == 30.0
    assert budget.get_provider_spent('image') == 20.0


def test_negative_provider_limit_raises_error():
    """Test negative provider limit raises error."""
    budget = Budget()
    
    with pytest.raises(ValueError):
        budget.set_provider_limit('gpt', -100.0)


def test_get_remaining():
    """Test getting remaining budget."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    budget.record_spending(30.0)
    
    remaining = budget.get_remaining(BudgetPeriod.DAILY)
    assert remaining == 70.0


def test_get_remaining_no_limit():
    """Test getting remaining when no limit set."""
    budget = Budget()
    budget.record_spending(30.0)
    
    remaining = budget.get_remaining(BudgetPeriod.DAILY)
    assert remaining is None


def test_get_remaining_over_limit():
    """Test getting remaining when over limit."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    budget.record_spending(120.0)
    
    remaining = budget.get_remaining(BudgetPeriod.DAILY)
    assert remaining == 0.0


def test_get_provider_remaining():
    """Test getting provider remaining budget."""
    budget = Budget()
    budget.set_provider_limit('gpt', 100.0)
    budget.record_spending(40.0, provider='gpt')
    
    remaining = budget.get_provider_remaining('gpt')
    assert remaining == 60.0


def test_get_provider_remaining_no_limit():
    """Test getting provider remaining when no limit set."""
    budget = Budget()
    budget.record_spending(40.0, provider='gpt')
    
    remaining = budget.get_provider_remaining('gpt')
    assert remaining is None


def test_get_spent():
    """Test getting spent amount."""
    budget = Budget()
    budget.record_spending(50.0)
    
    assert budget.get_spent(BudgetPeriod.DAILY) == 50.0
    assert budget.get_spent(BudgetPeriod.WEEKLY) == 50.0
    assert budget.get_spent(BudgetPeriod.MONTHLY) == 50.0
    assert budget.get_spent(BudgetPeriod.TOTAL) == 50.0


def test_get_provider_spent():
    """Test getting provider spent amount."""
    budget = Budget()
    budget.record_spending(30.0, provider='gpt')
    
    assert budget.get_provider_spent('gpt') == 30.0


def test_get_provider_spent_not_used():
    """Test getting spent for unused provider."""
    budget = Budget()
    
    assert budget.get_provider_spent('gpt') == 0.0


def test_reset_period():
    """Test resetting period."""
    budget = Budget()
    budget.record_spending(50.0)
    
    assert budget.get_spent(BudgetPeriod.DAILY) == 50.0
    
    budget.reset_period(BudgetPeriod.DAILY)
    
    assert budget.get_spent(BudgetPeriod.DAILY) == 0.0
    assert budget.get_spent(BudgetPeriod.TOTAL) == 50.0  # Total not reset


def test_reset_provider():
    """Test resetting provider spending."""
    budget = Budget()
    budget.record_spending(50.0, provider='gpt')
    
    assert budget.get_provider_spent('gpt') == 50.0
    
    budget.reset_provider('gpt')
    
    assert budget.get_provider_spent('gpt') == 0.0


def test_multiple_period_limits():
    """Test multiple period limits enforced."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 50.0)
    budget.set_limit(BudgetPeriod.WEEKLY, 200.0)
    budget.record_spending(40.0)
    
    # Can spend 10 more (daily limit)
    can_spend, reason = budget.can_spend(10.0)
    assert can_spend is True
    
    # Cannot spend 20 more (would exceed daily limit)
    can_spend, reason = budget.can_spend(20.0)
    assert can_spend is False


def test_budget_summary():
    """Test budget summary generation."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    budget.set_limit(BudgetPeriod.WEEKLY, 500.0)
    budget.set_provider_limit('gpt', 50.0)
    budget.record_spending(30.0, provider='gpt')
    
    summary = budget.get_budget_summary()
    
    assert 'Budget Summary' in summary or 'Сводка по бюджету' in summary
    assert 'gpt' in summary
    assert '30.00' in summary


def test_budget_summary_no_limits():
    """Test budget summary with no limits set."""
    budget = Budget()
    summary = budget.get_budget_summary()
    
    assert 'No period limits' in summary or 'Нет установленных лимитов' in summary


def test_spending_with_provider_and_period_limits():
    """Test spending with both provider and period limits."""
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 100.0)
    budget.set_provider_limit('gpt', 40.0)
    
    budget.record_spending(30.0, provider='gpt')
    
    # Can spend 10 more (provider limit)
    can_spend, reason = budget.can_spend(10.0, provider='gpt')
    assert can_spend is True
    
    # Cannot spend 20 more (would exceed provider limit)
    can_spend, reason = budget.can_spend(20.0, provider='gpt')
    assert can_spend is False


def test_different_providers_separate_budgets():
    """Test different providers have separate budgets."""
    budget = Budget()
    budget.set_provider_limit('gpt', 50.0)
    budget.set_provider_limit('image', 100.0)
    
    budget.record_spending(40.0, provider='gpt')
    budget.record_spending(80.0, provider='image')
    
    # GPT can spend 10 more
    can_spend, _ = budget.can_spend(10.0, provider='gpt')
    assert can_spend is True
    
    # Image can spend 20 more
    can_spend, _ = budget.can_spend(20.0, provider='image')
    assert can_spend is True


def test_import():
    """Test that budget module can be imported."""
    import budget
    assert budget is not None
    assert hasattr(budget, 'Budget')
    assert hasattr(budget, 'BudgetPeriod')
