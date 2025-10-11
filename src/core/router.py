"""
Router module for provider selection.
Модуль маршрутизатора для выбора провайдера.
"""

from typing import List, Protocol, Optional, Dict, Any


class Provider(Protocol):
    """Protocol for AI providers."""

    def __call__(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute provider request."""
        ...


class Router:
    """
    Selects AI provider for a given request.
    Выбирает поставщика ИИ для заданного запроса.
    """

    def __init__(self) -> None:
        """Initialize router with empty provider registry."""
        self._providers: List[Provider] = []

    def register_provider(self, provider: Provider) -> None:
        """
        Register a provider in the router.

        Args:
            provider: Provider instance to register.
        """
        self._providers.append(provider)

    def route_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Select the best provider for the request.

        Args:
            request: Request details (type, prompt, etc.).

        Returns:
            Provider response or None if no provider found.
        """
        request_type = request.get("type")
        prompt = request.get("prompt", "")

        # Try to find provider by type
        if request_type:
            for provider in self._providers:
                provider_class_name = provider.__class__.__name__.lower()
                if request_type.lower() in provider_class_name:
                    return provider(prompt)

        # Fallback to first available provider
        if self._providers:
            return self._providers[0](prompt)

        return None

    def get_provider_count(self) -> int:
        """
        Get number of registered providers.

        Returns:
            Number of providers.
        """
        return len(self._providers)

    def clear_providers(self) -> None:
        """Clear all registered providers."""
        self._providers.clear()


__all__ = [
    "Router",
    "Provider",
]
