"""
Router module for OneFlow.AI.
Маршрутизатор для OneFlow.AI.

This module defines the Router class which selects the best AI provider based on quality, speed, cost and region.
Этот модуль определяет класс Router, который выбирает наилучшего поставщика ИИ в зависимости от качества, скорости, стоимости и региона.
"""

class Router:
    """Router selects AI provider for a given request.
    Маршрутизатор выбирает поставщика ИИ для заданного запроса.
    """

    def __init__(self):
        """Initialize Router with provider registry.
        Инициализирует маршрутизатор с реестром поставщиков.
        """
        self.providers = []

    def register_provider(self, provider):
        """Register a provider in the router.
        Регистрация поставщика в маршрутизаторе.
        """
        self.providers.append(provider)

    def route_request(self, request):
        """Select the best provider for the request.
        Выбрать лучшего поставщика для запроса.

        Args:
            request (dict): Details about task (type, quality, speed, budget, region).
            request (dict): Сведения о задаче (тип, качество, скорость, бюджет, регион).

        Returns:
            object: Selected provider instance.
            object: Выбранный экземпляр поставщика.
        """
        
                # Determine the type of content requested
        # Определяем тип запрошенного контента
        request_type = request.get('type')
        prompt = request.get('prompt', '')

        # Try to find a provider whose class name contains the request type
        # Пытаемся найти провайдера, название класса которого содержит тип запроса
        if request_type:
            for provider in self.providers:
                if request_type.lower() in provider.__class__.__name__.lower():
                    return provider(prompt)

        # Fallback: if any providers are registered, use the first one
        # Запасной вариант: если есть зарегистрированные провайдеры, используем первого
        if self.providers:
            return self.providers[0](prompt)

        # If no providers are registered, return None
        # Если провайдеров нет, возвращаем None
                return None
