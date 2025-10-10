"""
Test module for the Router class in OneFlow.AI.

English:
This module tests the provider selection logic of the Router class, ensuring that the correct provider is chosen based on request type and that a fallback provider is used when no match is found.

Русская версия:
Этот модуль тестирует логику выбора провайдера в классе Router: проверяет, что правильный провайдер выбирается на основании типа запроса и что применяется запасной провайдер, если совпадений нет.
"""

import os
import sys
import pytest

# Add src path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from router import Router


class DummyTextProvider:
    """Dummy provider for text requests."""

    def __call__(self, prompt):
        return f"Text provider: {prompt}"


class DummyImageProvider:
    """Dummy provider for image requests."""

    def __call__(self, prompt):
        return f"Image provider: {prompt}"


def test_router_selects_correct_provider():
    """English: Verify correct provider selection for known type.

    Русская версия: Проверьте выбор правильного провайдера для известного типа.
    """
    router = Router()
    router.register_provider(DummyTextProvider())
    router.register_provider(DummyImageProvider())
    response = router.route_request({"type": "dummytext", "prompt": "hello"})
    assert response == "Text provider: hello"


def test_router_fallback_to_first_provider():
    """English: Ensure fallback to first provider when type is unknown.

    Русская версия: Убедитесь, что при неизвестном типе используется первый провайдер.
    """
    router = Router()
    router.register_provider(DummyTextProvider())
    router.register_provider(DummyImageProvider())
    response = router.route_request({"type": "unknown", "prompt": "fallback"})
    assert response == "Text provider: fallback"
