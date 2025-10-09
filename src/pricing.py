"""
Pricing module for OneFlow.AI.
Модуль расчета стоимости для OneFlow.AI.

This module defines the PricingCalculator class which estimates the cost of AI operations based on provider pricing and request parameters.
Этот модуль определяет класс PricingCalculator, который оценивает стоимость операций ИИ на основе тарифов поставщиков и параметров запроса.
"""

class PricingCalculator:
    """Calculate estimated cost for AI operations.
    Рассчитывает ориентировочную стоимость операций ИИ.
    """

    def __init__(self):
        """Initialize pricing calculator with provider rates.
        Инициализация калькулятора стоимости тарифами поставщиков.
        """
        self.rates = {}

    def register_rate(self, provider_name: str, rate: float) -> None:
        """Register rate per unit for a provider.
        Регистрация ставки за единицу для поставщика.

        Args:
            provider_name (str): Provider identifier.
            rate (float): Cost per unit.
        """
        self.rates[provider_name] = rate

    def estimate_cost(self, provider_name: str, units: float) -> float:
        """Estimate cost for given provider and units.
        Оценка стоимости для заданного поставщика и количества единиц.

        Args:
            provider_name (str): Provider identifier.
            units (float): Number of units.

        Returns:
            float: Estimated cost.
        """
        rate = self.rates.get(provider_name, 0.0)
        return rate * units
