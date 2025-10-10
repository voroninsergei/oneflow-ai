"""
Base provider classes and definitions for OneFlow.AI.

This module defines base classes and interfaces for AI model providers used in the
OneFlow.AI ecosystem. Providers encapsulate the logic for interacting with external
AI services and provide a uniform interface for making requests.

Модуль базовых классов и интерфейсов провайдеров для OneFlow.AI.

В этом модуле определены базовые классы и интерфейсы для провайдеров моделей ИИ,
используемых в экосистеме OneFlow.AI. Провайдеры инкапсулируют логику взаимодействия
с внешними сервисами ИИ и предоставляют унифицированный интерфейс для выполнения запросов.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Abstract base class for AI model providers in OneFlow.AI.

    Абстрактный базовый класс для провайдеров моделей ИИ в OneFlow.AI.
    """

    @abstractmethod
    def __call__(self, prompt: str, **kwargs):
        """
        Execute a request against the AI model and return the result.

        Выполнить запрос к модели ИИ и вернуть результат.

        :param prompt: The input prompt or data for the model.
        :param kwargs: Additional keyword arguments for provider-specific options.
        :return: The result produced by the provider.
        """
        pass
