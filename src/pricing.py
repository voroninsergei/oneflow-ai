"""
Pricing calculator module for OneFlow.AI.
Модуль калькулятора цен для OneFlow.AI.

This module provides cost estimation for AI provider requests based on registered rates.
Этот модуль предоставляет оценку стоимости запросов к AI провайдерам на основе зарегистрированных тарифов.
"""

from typing import Dict, Optional


class PricingCalculator:
    """
    Calculate costs for AI provider requests.
    Калькулятор стоимости запросов к AI провайдерам.
    """
    
    def __init__(self):
        """
        Initialize pricing calculator with empty rates.
        Инициализация калькулятора с пустыми тарифами.
        """
        self.rates: Dict[str, float] = {}
    
    def register_rate(self, provider_name: str, rate: float) -> None:
        """
        Register a pricing rate for a provider.
        Зарегистрировать тариф для провайдера.
        
        Args:
            provider_name: Provider identifier (e.g., 'gpt', 'image').
            rate: Cost per unit (e.g., credits per word, per image).
        
        Raises:
            ValueError: If rate is negative.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)  # 1 credit per word
            >>> calc.register_rate('image', 10.0)  # 10 credits per image
        """
        if rate < 0:
            raise ValueError(f"Rate must be non-negative, got {rate}")
        
        self.rates[provider_name] = rate
    
    def estimate_cost(self, provider_name: str, units: float) -> float:
        """
        Estimate cost for given provider and units.
        Оценка стоимости для заданного поставщика и количества единиц.
        
        Args:
            provider_name: Provider identifier.
            units: Number of units (words, images, etc.).
        
        Returns:
            float: Estimated cost in credits. Returns 0.0 if provider not found.
        
        Raises:
            ValueError: If units is negative.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)
            >>> calc.estimate_cost('gpt', 100)  # 100 words
            100.0
            >>> calc.estimate_cost('unknown', 50)  # Unknown provider
            0.0
        """
        if units < 0:
            raise ValueError(f"Units must be non-negative, got {units}")
        
        # Return 0.0 for unknown providers instead of None
        if provider_name not in self.rates:
            return 0.0
        
        rate = self.rates.get(provider_name, 0.0)
        return rate * units
    
    def get_rate(self, provider_name: str) -> float:
        """
        Get pricing rate for a provider.
        Получить тариф для провайдера.
        
        Args:
            provider_name: Provider identifier.
        
        Returns:
            float: Rate per unit, or 0.0 if not found.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.5)
            >>> calc.get_rate('gpt')
            1.5
            >>> calc.get_rate('unknown')
            0.0
        """
        return self.rates.get(provider_name, 0.0)
    
    def has_provider(self, provider_name: str) -> bool:
        """
        Check if provider rate is registered.
        Проверить зарегистрирован ли тариф провайдера.
        
        Args:
            provider_name: Provider identifier.
        
        Returns:
            bool: True if provider exists, False otherwise.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)
            >>> calc.has_provider('gpt')
            True
            >>> calc.has_provider('unknown')
            False
        """
        return provider_name in self.rates
    
    def get_all_rates(self) -> Dict[str, float]:
        """
        Get all registered provider rates.
        Получить все зарегистрированные тарифы провайдеров.
        
        Returns:
            dict: Dictionary of provider names to rates.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)
            >>> calc.register_rate('image', 10.0)
            >>> calc.get_all_rates()
            {'gpt': 1.0, 'image': 10.0}
        """
        return self.rates.copy()
    
    def remove_provider(self, provider_name: str) -> bool:
        """
        Remove a provider's rate.
        Удалить тариф провайдера.
        
        Args:
            provider_name: Provider identifier.
        
        Returns:
            bool: True if provider was removed, False if not found.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)
            >>> calc.remove_provider('gpt')
            True
            >>> calc.remove_provider('unknown')
            False
        """
        if provider_name in self.rates:
            del self.rates[provider_name]
            return True
        return False
    
    def update_rate(self, provider_name: str, new_rate: float) -> bool:
        """
        Update an existing provider's rate.
        Обновить существующий тариф провайдера.
        
        Args:
            provider_name: Provider identifier.
            new_rate: New rate value.
        
        Returns:
            bool: True if updated, False if provider not found.
        
        Raises:
            ValueError: If new_rate is negative.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)
            >>> calc.update_rate('gpt', 1.5)
            True
            >>> calc.get_rate('gpt')
            1.5
        """
        if new_rate < 0:
            raise ValueError(f"Rate must be non-negative, got {new_rate}")
        
        if provider_name not in self.rates:
            return False
        
        self.rates[provider_name] = new_rate
        return True
    
    def clear_all_rates(self) -> None:
        """
        Clear all registered rates.
        Очистить все зарегистрированные тарифы.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)
            >>> calc.clear_all_rates()
            >>> calc.get_all_rates()
            {}
        """
        self.rates.clear()
    
    def get_provider_count(self) -> int:
        """
        Get number of registered providers.
        Получить количество зарегистрированных провайдеров.
        
        Returns:
            int: Number of providers.
        
        Example:
            >>> calc = PricingCalculator()
            >>> calc.register_rate('gpt', 1.0)
            >>> calc.register_rate('image', 10.0)
            >>> calc.get_provider_count()
            2
        """
        return len(self.rates)
    
    def __repr__(self) -> str:
        """String representation of calculator."""
        return f"PricingCalculator(providers={len(self.rates)})"
    
    def __str__(self) -> str:
        """Readable string representation."""
        if not self.rates:
            return "PricingCalculator: No rates registered"
        
        rates_str = ", ".join(f"{name}: {rate}" for name, rate in self.rates.items())
        return f"PricingCalculator: {rates_str}"


# Convenience function for quick estimates
def calculate_cost(provider_name: str, units: float, rate: float) -> float:
    """
    Quick cost calculation without creating a calculator instance.
    Быстрый расчёт стоимости без создания экземпляра калькулятора.
    
    Args:
        provider_name: Provider identifier (for reference).
        units: Number of units.
        rate: Cost per unit.
    
    Returns:
        float: Total cost.
    
    Example:
        >>> calculate_cost('gpt', 100, 1.0)
        100.0
    """
    if rate < 0:
        raise ValueError(f"Rate must be non-negative, got {rate}")
    if units < 0:
        raise ValueError(f"Units must be non-negative, got {units}")
    
    return rate * units
