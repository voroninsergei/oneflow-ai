"""
Tests for provider classes in OneFlow.AI

English:
This module contains tests for the GPTProvider, ImageProvider, AudioProvider, and VideoProvider classes. It verifies that each provider correctly processes prompts and returns expected results.

Русская версия:
Этот модуль содержит тесты для классов GPTProvider, ImageProvider, AudioProvider и VideoProvider. Проверяет, что каждый провайдер правильно обрабатывает запросы и возвращает ожидаемые результаты.
"""
import os
import sys
import pytest

# Add the src path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from providers.gpt_provider import GPTProvider
from providers.image_provider import ImageProvider
from providers.audio_provider import AudioProvider
from providers.video_provider import VideoProvider


def test_gpt_provider_returns_response():
    provider = GPTProvider(name="gpt")
    prompt = "Hello world"
    result = provider(prompt)
    assert prompt in result


def test_image_provider_returns_response():
    provider = ImageProvider(name="image")
    prompt = "A sunset"
    result = provider(prompt)
    assert prompt in result


def test_audio_provider_returns_response():
    provider = AudioProvider(name="audio")
    prompt = "Bird chirping"
    result = provider(prompt)
    assert prompt in result


def test_video_provider_returns_response():
    provider = VideoProvider(name="video")
    prompt = "Cat playing"
    result = provider(prompt)
    assert prompt in result
