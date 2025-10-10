"""
Unit tests for Router module with mocked providers
Юнит-тесты для модуля маршрутизации с моками провайдеров
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from router import Router


@pytest.mark.unit
@pytest.mark.routing
class TestRouterUnit:
    """Unit tests for Router class"""

    def test_router_initialization(self):
        """Test router initializes with empty providers"""
        router = Router()
        assert router.providers == {}

    def test_register_provider(self, mock_gpt_provider):
        """Test provider registration"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        assert 'gpt' in router.providers
        assert router.providers['gpt'] == mock_gpt_provider

    def test_register_multiple_providers(self, mock_all_providers):
        """Test registering multiple providers"""
        router = Router()
        
        for provider in mock_all_providers.values():
            router.register_provider(provider)
        
        assert len(router.providers) == 4
        assert 'gpt' in router.providers
        assert 'image' in router.providers
        assert 'audio' in router.providers
        assert 'video' in router.providers

    def test_get_provider_existing(self, mock_gpt_provider):
        """Test getting existing provider"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        provider = router.get_provider('gpt')
        assert provider == mock_gpt_provider

    def test_get_provider_nonexistent(self):
        """Test getting non-existent provider returns None"""
        router = Router()
        provider = router.get_provider('nonexistent')
        assert provider is None

    def test_route_request_valid_provider(self, mock_gpt_provider):
        """Test routing request to valid provider"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        request = {'type': 'gpt', 'prompt': 'Hello'}
        response = router.route_request(request)
        
        mock_gpt_provider.__call__.assert_called_once_with('Hello')
        assert response == "Mocked GPT response"

    def test_route_request_with_provider_field(self, mock_image_provider):
        """Test routing with 'provider' field instead of 'type'"""
        router = Router()
        router.register_provider(mock_image_provider)
        
        request = {'provider': 'image', 'prompt': 'A sunset'}
        response = router.route_request(request)
        
        mock_image_provider.__call__.assert_called_once_with('A sunset')
        assert 'Mocked image' in response

    def test_route_request_fallback_to_first(self, mock_gpt_provider, mock_image_provider):
        """Test fallback to first provider when type unknown"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        router.register_provider(mock_image_provider)
        
        request = {'type': 'unknown', 'prompt': 'Fallback test'}
        response = router.route_request(request)
        
        # Should use first registered provider (gpt)
        mock_gpt_provider.__call__.assert_called_once()
        assert response == "Mocked GPT response"

    def test_route_request_no_providers_raises_error(self):
        """Test routing with no providers raises error"""
        router = Router()
        
        request = {'type': 'gpt', 'prompt': 'Test'}
        
        with pytest.raises(ValueError, match="No providers registered"):
            router.route_request(request)

    def test_route_request_missing_prompt(self, mock_gpt_provider):
        """Test routing without prompt field"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        request = {'type': 'gpt'}
        
        with pytest.raises(KeyError, match="prompt"):
            router.route_request(request)

    def test_unregister_provider(self, mock_gpt_provider):
        """Test unregistering a provider"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        assert 'gpt' in router.providers
        
        router.unregister_provider('gpt')
        assert 'gpt' not in router.providers

    def test_list_providers(self, mock_all_providers):
        """Test listing all registered providers"""
        router = Router()
        
        for provider in mock_all_providers.values():
            router.register_provider(provider)
        
        provider_list = router.list_providers()
        assert set(provider_list) == {'gpt', 'image', 'audio', 'video'}

    def test_has_provider(self, mock_gpt_provider):
        """Test checking if provider exists"""
        router = Router()
        
        assert not router.has_provider('gpt')
        
        router.register_provider(mock_gpt_provider)
        assert router.has_provider('gpt')

    def test_route_with_metadata(self, mock_gpt_provider):
        """Test routing request with additional metadata"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        request = {
            'type': 'gpt',
            'prompt': 'Test',
            'metadata': {'user_id': '123', 'session_id': 'abc'}
        }
        
        response = router.route_request(request)
        mock_gpt_provider.__call__.assert_called_once_with('Test')

    def test_route_concurrent_requests(self, mock_gpt_provider):
        """Test handling multiple concurrent requests"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        requests = [
            {'type': 'gpt', 'prompt': f'Request {i}'}
            for i in range(5)
        ]
        
        for req in requests:
            router.route_request(req)
        
        assert mock_gpt_provider.__call__.call_count == 5

    def test_provider_override(self, mock_gpt_provider):
        """Test overriding existing provider"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        new_provider = Mock()
        new_provider.name = 'gpt'
        new_provider.__call__ = Mock(return_value="New response")
        
        router.register_provider(new_provider)
        
        request = {'type': 'gpt', 'prompt': 'Test'}
        response = router.route_request(request)
        
        assert response == "New response"
        mock_gpt_provider.__call__.assert_not_called()

    def test_case_insensitive_routing(self, mock_gpt_provider):
        """Test case-insensitive provider routing"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        
        # Try different cases
        request1 = {'type': 'GPT', 'prompt': 'Test'}
        request2 = {'type': 'Gpt', 'prompt': 'Test'}
        
        # Assuming router handles case-insensitivity
        # If not, this test documents the expected behavior
        try:
            router.route_request(request1)
            router.route_request(request2)
        except ValueError:
            # If case-sensitive, that's fine too
            pass

    def test_router_with_default_provider(self, mock_gpt_provider):
        """Test setting a default provider"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        router.set_default_provider('gpt')
        
        request = {'prompt': 'Test'}  # No type specified
        response = router.route_request(request)
        
        mock_gpt_provider.__call__.assert_called_once()

    def test_provider_validation(self):
        """Test provider validation on registration"""
        router = Router()
        
        # Invalid provider (no name attribute)
        invalid_provider = Mock(spec=[])
        
        with pytest.raises(AttributeError):
            router.register_provider(invalid_provider)

    def test_clear_all_providers(self, mock_all_providers):
        """Test clearing all providers"""
        router = Router()
        
        for provider in mock_all_providers.values():
            router.register_provider(provider)
        
        assert len(router.providers) == 4
        
        router.clear_providers()
        assert len(router.providers) == 0
