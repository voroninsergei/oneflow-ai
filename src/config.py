"""
Configuration module for OneFlow.AI.
Модуль конфигурации для OneFlow.AI.

This module provides centralized configuration management for the OneFlow.AI system,
including provider rates, default budgets, and system settings.

Этот модуль предоставляет централизованное управление конфигурацией для системы OneFlow.AI,
включая тарифы провайдеров, бюджеты по умолчанию и системные настройки.
"""

from typing import Dict, Any
import json
import os


class Config:
    """
    Configuration manager for OneFlow.AI.
    Менеджер конфигурации для OneFlow.AI.
    """
    
    # Default provider rates (credits per unit)
    DEFAULT_RATES = {
        'gpt': 1.0,      # per word / за слово
        'image': 10.0,   # per image / за изображение
        'audio': 5.0,    # per audio file / за аудио-файл
        'video': 20.0    # per video / за видео
    }
    
    # Default wallet settings
    DEFAULT_WALLET_BALANCE = 100.0
    
    # Default budget limits (None means no limit)
    DEFAULT_BUDGET_LIMITS = {
        'daily': None,
        'weekly': None,
        'monthly': None,
        'total': None
    }
    
    # Default provider budget limits
    DEFAULT_PROVIDER_BUDGETS = {
        'gpt': None,
        'image': None,
        'audio': None,
        'video': None
    }
    
    # System settings
    ENABLE_ANALYTICS = True
    ENABLE_BUDGET_CONTROL = True
    
    # Region settings
    AVAILABLE_REGIONS = ['US', 'EU', 'RU']
    DEFAULT_REGION = 'US'
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration.
        Инициализировать конфигурацию.
        
        Args:
            config_file: Optional path to JSON configuration file.
        """
        self.rates = self.DEFAULT_RATES.copy()
        self.wallet_balance = self.DEFAULT_WALLET_BALANCE
        self.budget_limits = self.DEFAULT_BUDGET_LIMITS.copy()
        self.provider_budgets = self.DEFAULT_PROVIDER_BUDGETS.copy()
        self.region = self.DEFAULT_REGION
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load configuration from JSON file.
        Загрузить конфигурацию из JSON-файла.
        
        Args:
            filepath: Path to configuration file.
        
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file format is invalid.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load rates
            if 'rates' in config_data:
                self.rates.update(config_data['rates'])
            
            # Load wallet balance
            if 'wallet_balance' in config_data:
                self.wallet_balance = float(config_data['wallet_balance'])
            
            # Load budget limits
            if 'budget_limits' in config_data:
                self.budget_limits.update(config_data['budget_limits'])
            
            # Load provider budgets
            if 'provider_budgets' in config_data:
                self.provider_budgets.update(config_data['provider_budgets'])
            
            # Load region
            if 'region' in config_data:
                region = config_data['region'].upper()
                if region in self.AVAILABLE_REGIONS:
                    self.region = region
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in config file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config file: {e}")
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save current configuration to JSON file.
        Сохранить текущую конфигурацию в JSON-файл.
        
        Args:
            filepath: Path to save configuration.
        """
        config_data = {
            'rates': self.rates,
            'wallet_balance': self.wallet_balance,
            'budget_limits': self.budget_limits,
            'provider_budgets': self.provider_budgets,
            'region': self.region
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def set_rate(self, provider: str, rate: float) -> None:
        """
        Set pricing rate for a provider.
        Установить тариф для провайдера.
        
        Args:
            provider: Provider name.
            rate: Rate per unit.
        
        Raises:
            ValueError: If rate is negative.
        """
        if rate < 0:
            raise ValueError(f"Rate must be non-negative, got {rate}")
        self.rates[provider] = rate
    
    def get_rate(self, provider: str) -> float:
        """
        Get pricing rate for a provider.
        Получить тариф для провайдера.
        
        Args:
            provider: Provider name.
        
        Returns:
            float: Rate per unit, or 0.0 if not found.
        """
        return self.rates.get(provider, 0.0)
    
    def set_wallet_balance(self, balance: float) -> None:
        """
        Set default wallet balance.
        Установить баланс кошелька по умолчанию.
        
        Args:
            balance: Initial balance amount.
        
        Raises:
            ValueError: If balance is negative.
        """
        if balance < 0:
            raise ValueError(f"Balance must be non-negative, got {balance}")
        self.wallet_balance = balance
    
    def set_budget_limit(self, period: str, amount: float = None) -> None:
        """
        Set budget limit for a period.
        Установить лимит бюджета на период.
        
        Args:
            period: Period name ('daily', 'weekly', 'monthly', 'total').
            amount: Limit amount (None for no limit).
        
        Raises:
            ValueError: If period is invalid or amount is negative.
        """
        if period not in self.budget_limits:
            raise ValueError(f"Invalid period: {period}. Must be one of: {list(self.budget_limits.keys())}")
        
        if amount is not None and amount < 0:
            raise ValueError(f"Budget amount must be non-negative, got {amount}")
        
        self.budget_limits[period] = amount
    
    def set_provider_budget(self, provider: str, amount: float = None) -> None:
        """
        Set budget limit for a provider.
        Установить лимит бюджета для провайдера.
        
        Args:
            provider: Provider name.
            amount: Budget limit (None for no limit).
        
        Raises:
            ValueError: If amount is negative.
        """
        if amount is not None and amount < 0:
            raise ValueError(f"Provider budget must be non-negative, got {amount}")
        
        self.provider_budgets[provider] = amount
    
    def set_region(self, region: str) -> None:
        """
        Set service region.
        Установить регион обслуживания.
        
        Args:
            region: Region code ('US', 'EU', 'RU').
        
        Raises:
            ValueError: If region is invalid.
        """
        region_upper = region.upper()
        if region_upper not in self.AVAILABLE_REGIONS:
            raise ValueError(f"Invalid region: {region}. Must be one of: {self.AVAILABLE_REGIONS}")
        self.region = region_upper
    
    def get_all_rates(self) -> Dict[str, float]:
        """
        Get all provider rates.
        Получить все тарифы провайдеров.
        
        Returns:
            dict: Provider rates.
        """
        return self.rates.copy()
    
    def get_config_summary(self) -> str:
        """
        Get formatted configuration summary.
        Получить форматированную сводку конфигурации.
        
        Returns:
            str: Formatted configuration info.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("OneFlow.AI Configuration | Конфигурация OneFlow.AI")
        lines.append("=" * 60)
        
        lines.append("\nProvider Rates | Тарифы провайдеров:")
        lines.append("-" * 60)
        for provider, rate in sorted(self.rates.items()):
            lines.append(f"  {provider}: {rate:.2f} credits per unit")
        
        lines.append(f"\nDefault Wallet Balance | Баланс по умолчанию: {self.wallet_balance:.2f} credits")
        lines.append(f"Region | Регион: {self.region}")
        
        lines.append("\nBudget Limits | Лимиты бюджета:")
        lines.append("-" * 60)
        for period, limit in self.budget_limits.items():
            limit_str = f"{limit:.2f} credits" if limit is not None else "No limit / Без лимита"
            lines.append(f"  {period.capitalize()}: {limit_str}")
        
        lines.append("\nProvider Budgets | Бюджеты провайдеров:")
        lines.append("-" * 60)
        for provider, budget in sorted(self.provider_budgets.items()):
            budget_str = f"{budget:.2f} credits" if budget is not None else "No limit / Без лимита"
            lines.append(f"  {provider}: {budget_str}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary.
        Экспортировать конфигурацию как словарь.
        
        Returns:
            dict: Complete configuration data.
        """
        return {
            'rates': self.rates,
            'wallet_balance': self.wallet_balance,
            'budget_limits': self.budget_limits,
            'provider_budgets': self.provider_budgets,
            'region': self.region
        }


# Singleton instance for global configuration
# Синглтон для глобальной конфигурации
_global_config = None


def get_config(config_file: str = None) -> Config:
    """
    Get global configuration instance.
    Получить глобальный экземпляр конфигурации.
    
    Args:
        config_file: Optional path to configuration file.
    
    Returns:
        Config: Global configuration instance.
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(config_file)
    return _global_config


def reset_config() -> None:
    """
    Reset global configuration to defaults.
    Сбросить глобальную конфигурацию к значениям по умолчанию.
    """
    global _global_config
    _global_config = None
