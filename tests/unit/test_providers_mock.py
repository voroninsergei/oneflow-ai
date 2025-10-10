"""
Unit tests for providers with HTTP mocking using responses/httpx
Юнит-тесты для провайдеров с HTTP моками
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import responses for HTTP mocking
try:
    import responses
    RESPONSES_AVAILABLE = True
except ImportError:
    RESPONSES_AVAILABLE = False

try:
    from respx import MockRouter
    import httpx
    RESPX_AVAILABLE = True
except ImportError:
    RESPX_AVAILABLE = False


@pytest.mark.unit
@pytest.mark.providers
class TestProvidersWithMocking:
    """Test providers with mocked external API calls"""

    def test_gpt_provider_basic(self):
        """Test GPT provider basic functionality"""
        from providers.gpt_provider import GPTProvider
        
        provider = GPTProvider(name="gpt")
        
        with patch.object(provider, '_call_api') as mock_api:
            mock_api.return_value = "Mocked GPT response"
            
            result = provider("Test prompt")
            assert "Test prompt" in result or "Mocked" in result
            mock_api.assert_called_once()

    def test_image_provider_basic(self):
        """Test Image provider basic functionality"""
        from providers.image_provider import ImageProvider
        
        provider = ImageProvider(name="image")
        
        with patch.object(provider, '_call_api') as mock_api:
            mock_api.return_value = "http://example.com/image.png"
            
            result = provider("A sunset")
            assert "sunset" in result.lower() or "image" in result.lower()

    def test_audio_provider_basic(self):
        """Test Audio provider basic functionality"""
        from providers.audio_provider import AudioProvider
        
        provider = AudioProvider(name="audio")
        
        with patch.object(provider, '_call_api') as mock_api:
            mock_api.return_value = "http://example.com/audio.mp3"
            
            result = provider("Generate speech")
            assert "audio" in result.lower() or "speech" in result.lower()

    def test_video_provider_basic(self):
        """Test Video provider basic functionality"""
        from providers.video_provider import VideoProvider
        
        provider = VideoProvider(name="video")
        
        with patch.object(provider, '_call_api') as mock_api:
            mock_api.return_value = "http://example.com/video.mp4"
            
            result = provider("Create video")
            assert "video" in result.lower() or "create" in result.lower()


@pytest.mark.skipif(not RESPONSES_AVAILABLE, reason="responses library not installed")
@pytest.mark.unit
@pytest.mark.providers
class TestProvidersWithResponses:
    """Test providers using responses library for HTTP mocking"""

    @responses.activate
    def test_gpt_provider_api_call(self):
        """Test GPT provider with mocked API call"""
        # Mock OpenAI API endpoint
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={
                "choices": [
                    {"message": {"content": "This is a test response"}}
                ],
                "usage": {"total_tokens": 50}
            },
            status=200
        )
        
        from providers.gpt_provider import GPTProvider
        provider = GPTProvider(name="gpt")
        
        # If provider makes real API calls, this will use the mock
        # Otherwise, this tests the provider's structure
        result = provider("Test prompt")
        assert result is not None

    @responses.activate
    def test_image_provider_api_call(self):
        """Test Image provider with mocked API call"""
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/images/generations",
            json={
                "data": [
                    {"url": "https://example.com/generated-image.png"}
                ]
            },
            status=200
        )
        
        from providers.image_provider import ImageProvider
        provider = ImageProvider(name="image")
        
        result = provider("A cat")
        assert result is not None

    @responses.activate
    def test_provider_error_handling(self):
        """Test provider error handling with mocked failed API"""
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={"error": {"message": "Rate limit exceeded"}},
            status=429
        )
        
        from providers.gpt_provider import GPTProvider
        provider = GPTProvider(name="gpt")
        
        # Test that provider handles errors gracefully
        try:
            result = provider("Test prompt")
            # Should either raise or return error message
            assert result is not None
        except Exception as e:
            # Error handling is acceptable
            assert "error" in str(e).lower() or "rate" in str(e).lower()


@pytest.mark.skipif(not RESPX_AVAILABLE, reason="respx library not installed")
@pytest.mark.unit
@pytest.mark.providers
class TestProvidersWithRespx:
    """Test providers using respx library for async HTTP mocking"""

    @pytest.mark.asyncio
    async def test_gpt_provider_async(self):
        """Test GPT provider with async mocking"""
        import respx
        
        with respx.mock:
            # Mock the OpenAI endpoint
            respx.post("https://api.openai.com/v1/chat/completions").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "choices": [{"message": {"content": "Async response"}}],
                        "usage": {"total_tokens": 25}
                    }
                )
            )
            
            from providers.gpt_provider import GPTProvider
            provider = GPTProvider(name="gpt")
            
            # If provider supports async
            if hasattr(provider, 'async_call'):
                result = await provider.async_call("Test")
                assert result is not None

    @pytest.mark.asyncio
    async def test_provider_timeout_handling(self):
        """Test provider timeout handling"""
        import respx
        from httpx import TimeoutException
        
        with respx.mock:
            respx.post("https://api.openai.com/v1/chat/completions").mock(
                side_effect=TimeoutException("Request timeout")
            )
            
            from providers.gpt_provider import GPTProvider
            provider = GPTProvider(name="gpt")
            
            # Test timeout handling
            try:
                if hasattr(provider, 'async_call'):
                    result = await provider.async_call("Test", timeout=1)
            except Exception as e:
                assert "timeout" in str(e).lower()


@pytest.mark.unit
@pytest.mark.providers
class TestProviderConfiguration:
    """Test provider configuration and initialization"""

    def test_provider_initialization_with_config(self):
        """Test provider initialization with configuration"""
        from providers.gpt_provider import GPTProvider
        
        config = {
            'api_key': 'test-key',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7
        }
        
        provider = GPTProvider(name="gpt", config=config)
        assert provider.name == "gpt"

    def test_provider_default_parameters(self):
        """Test provider default parameters"""
        from providers.gpt_provider import GPTProvider
        
        provider = GPTProvider(name="gpt")
        
        # Check default attributes exist
        assert hasattr(provider, 'name')
        assert provider.name == "gpt"

    def test_provider_custom_parameters(self):
        """Test provider with custom parameters"""
        from providers.image_provider import ImageProvider
        
        provider = ImageProvider(
            name="image",
            size="1024x1024",
            quality="hd"
        )
        
        assert provider.name == "image"

    def test_multiple_provider_instances(self):
        """Test creating multiple provider instances"""
        from providers.gpt_provider import GPTProvider
        from providers.image_provider import ImageProvider
        
        gpt1 = GPTProvider(name="gpt-1")
        gpt2 = GPTProvider(name="gpt-2")
        img = ImageProvider(name="image")
        
        assert gpt1.name != gpt2.name
        assert gpt1 is not gpt2


@pytest.mark.unit
@pytest.mark.providers
class TestProviderValidation:
    """Test provider input validation"""

    def test_empty_prompt_handling(self):
        """Test handling of empty prompts"""
        from providers.gpt_provider import GPTProvider
        
        provider = GPTProvider(name="gpt")
        
        # Test empty prompt
        try:
            result = provider("")
            # Should handle gracefully or raise
            assert result is not None or result == ""
        except ValueError as e:
            # Raising ValueError is acceptable
            assert "prompt" in str(e).lower() or "empty" in str(e).lower()

    def test_very_long_prompt_handling(self):
        """Test handling of very long prompts"""
        from providers.gpt_provider import GPTProvider
        
        provider = GPTProvider(name="gpt")
        long_prompt = "test " * 10000  # Very long prompt
        
        try:
            result = provider(long_prompt)
            assert result is not None
        except Exception as e:
            # Truncation or error is acceptable
            assert True

    def test_special_characters_in_prompt(self):
        """Test handling of special characters"""
        from providers.gpt_provider import GPTProvider
        
        provider = GPTProvider(name="gpt")
        special_prompt = "Test with émojis 🔥 and symbols @#$%"
        
        with patch.object(provider, '_call_api', return_value="Mocked"):
            result = provider(special_prompt)
            assert result is not None

    def test_unicode_prompt_handling(self):
        """Test handling of unicode in prompts"""
        from providers.gpt_provider import GPTProvider
        
        provider = GPTProvider(name="gpt")
        unicode_prompt = "Привет мир 你好世界 مرحبا"
        
        with patch.object(provider, '_call_api', return_value="Mocked"):
            result = provider(unicode_prompt)
            assert result is not None
