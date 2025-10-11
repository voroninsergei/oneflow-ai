"""
Pricing calculator module.
Модуль калькулятора цен.
"""

from typing import Dict, Final


class PricingCalculator:
    """
    Calculate costs for AI provider requests.
    Калькулятор стоимости запросов к AI провайдерам.
    """

    def __init__(self) -> None:
        """Initialize pricing calculator with empty rates."""
        self._rates: Dict[str, float] = {}

    def register_rate(self, provider_name: str, rate: float) -> None:
        """
        Register pricing rate for a provider.

        Args:
            provider_name: Provider identifier.
            rate: Cost per unit.

        Raises:
            ValueError: If rate is negative or provider_name is empty.
        """
        if not provider_name:
            raise ValueError("Provider name cannot be empty")
        if rate < 0:
            raise ValueError(f"Rate must be non-negative, got {rate}")
        self._rates[provider_name] = rate

    def estimate_cost(self, provider_name: str, units: float) -> float:
        """
        Estimate cost for given provider and units.

        Args:
            provider_name: Provider identifier.
            units: Number of units (words, images, etc.).

        Returns:
            Estimated cost in credits. Returns 0.0 if provider not found.

        Raises:
            ValueError: If units is negative.
        """
        if units < 0:
            raise ValueError(f"Units must be non-negative, got {units}")
        if provider_name not in self._rates:
            return 0.0
        return self._rates[provider_name] * units

    def get_rate(self, provider_name: str) -> float:
        """
        Get pricing rate for a provider.

        Args:
            provider_name: Provider identifier.

        Returns:
            Rate per unit, or 0.0 if not found.
        """
        return self._rates.get(provider_name, 0.0)

    def has_provider(self, provider_name: str) -> bool:
        """
        Check if provider rate is registered.

        Args:
            provider_name: Provider identifier.

        Returns:
            True if provider exists.
        """
        return provider_name in self._rates

    def get_all_rates(self) -> Dict[str, float]:
        """
        Get all registered provider rates.

        Returns:
            Dictionary of provider names to rates.
        """
        return self._rates.copy()

    def remove_provider(self, provider_name: str) -> bool:
        """
        Remove a provider's rate.

        Args:
            provider_name: Provider identifier.

        Returns:
            True if provider was removed, False if not found.
        """
        if provider_name in self._rates:
            del self._rates[provider_name]
            return True
        return False

    def update_rate(self, provider_name: str, new_rate: float) -> bool:
        """
        Update existing provider's rate.

        Args:
            provider_name: Provider identifier.
            new_rate: New rate value.

        Returns:
            True if updated, False if provider not found.

        Raises:
            ValueError: If new_rate is negative.
        """
        if new_rate < 0:
            raise ValueError(f"Rate must be non-negative, got {new_rate}")
        if provider_name not in self._rates:
            return False
        self._rates[provider_name] = new_rate
        return True

    def clear_all_rates(self) -> None:
        """Clear all registered rates."""
        self._rates.clear()

    def get_provider_count(self) -> int:
        """
        Get number of registered providers.

        Returns:
            Number of providers.
        """
        return len(self._rates)

    def __repr__(self) -> str:
        return f"PricingCalculator(providers={len(self._rates)})"


__all__ = [
    "PricingCalculator",
]
