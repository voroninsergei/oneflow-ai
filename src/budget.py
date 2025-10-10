"""
Budget management module for OneFlow.AI.
Модуль управления бюджетами для OneFlow.AI.

This module provides budget limits and controls for AI spending,
including daily, weekly, monthly limits, and per-provider budgets.

Этот модуль предоставляет лимиты и контроль бюджета для расходов на AI,
включая дневные, недельные, месячные лимиты и бюджеты для каждого провайдера.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from enum import Enum


class BudgetPeriod(Enum):
    """Budget period types / Типы периодов бюджета."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TOTAL = "total"


class Budget:
    """
    Manage spending limits and budget controls.
    Управление лимитами расходов и контролем бюджета.
    """
    
    def __init__(self):
        """
        Initialize budget manager.
        Инициализация менеджера бюджета.
        """
        self.limits: Dict[BudgetPeriod, float] = {}
        self.provider_limits: Dict[str, float] = {}
        self.spent: Dict[BudgetPeriod, float] = {
            BudgetPeriod.DAILY: 0.0,
            BudgetPeriod.WEEKLY: 0.0,
            BudgetPeriod.MONTHLY: 0.0,
            BudgetPeriod.TOTAL: 0.0
        }
        self.provider_spent: Dict[str, float] = {}
        self.reset_times: Dict[BudgetPeriod, datetime] = {}
        self._initialize_reset_times()
    
    def _initialize_reset_times(self):
        """Initialize reset times for each period."""
        now = datetime.now()
        self.reset_times[BudgetPeriod.DAILY] = now + timedelta(days=1)
        self.reset_times[BudgetPeriod.WEEKLY] = now + timedelta(weeks=1)
        self.reset_times[BudgetPeriod.MONTHLY] = now + timedelta(days=30)
    
    def set_limit(self, period: BudgetPeriod, amount: float) -> None:
        """
        Set spending limit for a time period.
        Установить лимит расходов на период времени.
        
        Args:
            period: Budget period (daily, weekly, monthly, total).
            amount: Maximum spending amount.
        
        Raises:
            ValueError: If amount is negative.
        """
        if amount < 0:
            raise ValueError(f"Budget amount must be non-negative, got {amount}")
        self.limits[period] = amount
    
    def set_provider_limit(self, provider: str, amount: float) -> None:
        """
        Set spending limit for a specific provider.
        Установить лимит расходов для конкретного провайдера.
        
        Args:
            provider: Provider name.
            amount: Maximum spending amount for this provider.
        
        Raises:
            ValueError: If amount is negative.
        """
        if amount < 0:
            raise ValueError(f"Provider budget must be non-negative, got {amount}")
        self.provider_limits[provider] = amount
        if provider not in self.provider_spent:
            self.provider_spent[provider] = 0.0
    
    def _check_reset_needed(self) -> None:
        """Check if any periods need to be reset."""
        now = datetime.now()
        
        for period in [BudgetPeriod.DAILY, BudgetPeriod.WEEKLY, BudgetPeriod.MONTHLY]:
            if now >= self.reset_times[period]:
                self.spent[period] = 0.0
                if period == BudgetPeriod.DAILY:
                    self.reset_times[period] = now + timedelta(days=1)
                elif period == BudgetPeriod.WEEKLY:
                    self.reset_times[period] = now + timedelta(weeks=1)
                elif period == BudgetPeriod.MONTHLY:
                    self.reset_times[period] = now + timedelta(days=30)
    
    def can_spend(self, amount: float, provider: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Check if spending amount is within budget limits.
        Проверить, соответствует ли сумма расходов лимитам бюджета.
        
        Args:
            amount: Amount to spend.
            provider: Provider name (optional).
        
        Returns:
            tuple: (can_spend: bool, reason: str or None)
                   True if within budget, False otherwise with reason.
        """
        self._check_reset_needed()
        
        # Check period limits
        for period, limit in self.limits.items():
            if self.spent[period] + amount > limit:
                return False, f"{period.value} budget limit exceeded"
        
        # Check provider-specific limit
        if provider and provider in self.provider_limits:
            provider_total = self.provider_spent.get(provider, 0.0)
            if provider_total + amount > self.provider_limits[provider]:
                return False, f"Budget limit for provider '{provider}' exceeded"
        
        return True, None
    
    def record_spending(self, amount: float, provider: Optional[str] = None) -> None:
        """
        Record spending amount.
        Записать сумму расходов.
        
        Args:
            amount: Amount spent.
            provider: Provider name (optional).
        
        Raises:
            ValueError: If amount is negative.
        """
        if amount < 0:
            raise ValueError(f"Spending amount must be non-negative, got {amount}")
        
        self._check_reset_needed()
        
        # Update all period counters
        for period in self.spent.keys():
            self.spent[period] += amount
        
        # Update provider spending
        if provider:
            if provider not in self.provider_spent:
                self.provider_spent[provider] = 0.0
            self.provider_spent[provider] += amount
    
    def get_remaining(self, period: BudgetPeriod) -> Optional[float]:
        """
        Get remaining budget for a period.
        Получить остаток бюджета на период.
        
        Args:
            period: Budget period.
        
        Returns:
            float or None: Remaining amount, or None if no limit set.
        """
        self._check_reset_needed()
        
        if period not in self.limits:
            return None
        
        return max(0.0, self.limits[period] - self.spent[period])
    
    def get_provider_remaining(self, provider: str) -> Optional[float]:
        """
        Get remaining budget for a provider.
        Получить остаток бюджета для провайдера.
        
        Args:
            provider: Provider name.
        
        Returns:
            float or None: Remaining amount, or None if no limit set.
        """
        if provider not in self.provider_limits:
            return None
        
        spent = self.provider_spent.get(provider, 0.0)
        return max(0.0, self.provider_limits[provider] - spent)
    
    def get_spent(self, period: BudgetPeriod) -> float:
        """
        Get total spent for a period.
        Получить общие расходы за период.
        
        Args:
            period: Budget period.
        
        Returns:
            float: Amount spent.
        """
        self._check_reset_needed()
        return self.spent[period]
    
    def get_provider_spent(self, provider: str) -> float:
        """
        Get total spent for a provider.
        Получить общие расходы для провайдера.
        
        Args:
            provider: Provider name.
        
        Returns:
            float: Amount spent.
        """
        return self.provider_spent.get(provider, 0.0)
    
    def reset_period(self, period: BudgetPeriod) -> None:
        """
        Manually reset spending for a period.
        Вручную сбросить расходы за период.
        
        Args:
            period: Budget period to reset.
        """
        self.spent[period] = 0.0
        if period in self.reset_times:
            now = datetime.now()
            if period == BudgetPeriod.DAILY:
                self.reset_times[period] = now + timedelta(days=1)
            elif period == BudgetPeriod.WEEKLY:
                self.reset_times[period] = now + timedelta(weeks=1)
            elif period == BudgetPeriod.MONTHLY:
                self.reset_times[period] = now + timedelta(days=30)
    
    def reset_provider(self, provider: str) -> None:
        """
        Manually reset spending for a provider.
        Вручную сбросить расходы для провайдера.
        
        Args:
            provider: Provider name.
        """
        if provider in self.provider_spent:
            self.provider_spent[provider] = 0.0
    
    def get_budget_summary(self) -> str:
        """
        Generate budget summary report.
        Сгенерировать сводный отчёт по бюджету.
        
        Returns:
            str: Formatted budget summary.
        """
        self._check_reset_needed()
        
        report = []
        report.append("=" * 60)
        report.append("Budget Summary | Сводка по бюджету")
        report.append("=" * 60)
        
        # Period budgets
        if self.limits:
            report.append("\nPeriod Limits | Лимиты по периодам:")
            report.append("-" * 60)
            for period, limit in self.limits.items():
                spent = self.spent[period]
                remaining = limit - spent
                percentage = (spent / limit * 100) if limit > 0 else 0
                report.append(f"  {period.value.capitalize()}:")
                report.append(f"    Limit | Лимит: {limit:.2f} credits")
                report.append(f"    Spent | Потрачено: {spent:.2f} credits ({percentage:.1f}%)")
                report.append(f"    Remaining | Остаток: {remaining:.2f} credits")
        else:
            report.append("\nNo period limits set | Нет установленных лимитов по периодам")
        
        # Provider budgets
        if self.provider_limits:
            report.append("\nProvider Limits | Лимиты провайдеров:")
            report.append("-" * 60)
            for provider, limit in self.provider_limits.items():
                spent = self.provider_spent.get(provider, 0.0)
                remaining = limit - spent
                percentage = (spent / limit * 100) if limit > 0 else 0
                report.append(f"  {provider}:")
                report.append(f"    Limit | Лимит: {limit:.2f} credits")
                report.append(f"    Spent | Потрачено: {spent:.2f} credits ({percentage:.1f}%)")
                report.append(f"    Remaining | Остаток: {remaining:.2f} credits")
        else:
            report.append("\nNo provider limits set | Нет установленных лимитов провайдеров")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
