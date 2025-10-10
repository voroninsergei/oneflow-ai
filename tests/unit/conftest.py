"""
Shared fixtures for unit tests
Общие фикстуры для юнит-тестов
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.fixture
def mock_gpt_provider():
    """Mock GPT provider for testing"""
    provider = Mock()
    provider.name = "gpt"
    provider.__call__ = Mock(return_value="Mocked GPT response")
    provider.estimate_cost = Mock(return_value=1.0)
    return provider


@pytest.fixture
def mock_image_provider():
    """Mock Image provider for testing"""
    provider = Mock()
    provider.name = "image"
    provider.__call__ = Mock(return_value="Mocked image URL: http://example.com/image.png")
    provider.estimate_cost = Mock(return_value=10.0)
    return provider


@pytest.fixture
def mock_audio_provider():
    """Mock Audio provider for testing"""
    provider = Mock()
    provider.name = "audio"
    provider.__call__ = Mock(return_value="Mocked audio URL: http://example.com/audio.mp3")
    provider.estimate_cost = Mock(return_value=5.0)
    return provider


@pytest.fixture
def mock_video_provider():
    """Mock Video provider for testing"""
    provider = Mock()
    provider.name = "video"
    provider.__call__ = Mock(return_value="Mocked video URL: http://example.com/video.mp4")
    provider.estimate_cost = Mock(return_value=15.0)
    return provider


@pytest.fixture
def mock_all_providers(mock_gpt_provider, mock_image_provider, 
                       mock_audio_provider, mock_video_provider):
    """Dictionary of all mock providers"""
    return {
        'gpt': mock_gpt_provider,
        'image': mock_image_provider,
        'audio': mock_audio_provider,
        'video': mock_video_provider
    }


@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except:
        pass


@pytest.fixture
def temp_db_file():
    """Create temporary database file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except:
        pass


@pytest.fixture
def mock_wallet():
    """Mock wallet for testing"""
    wallet = Mock()
    wallet.balance = 100.0
    wallet.can_afford = Mock(return_value=True)
    wallet.deduct = Mock()
    wallet.add_credits = Mock()
    wallet.get_balance = Mock(return_value=100.0)
    return wallet


@pytest.fixture
def mock_analytics():
    """Mock analytics for testing"""
    analytics = Mock()
    analytics.log_request = Mock()
    analytics.get_request_count = Mock(return_value=0)
    analytics.get_total_cost = Mock(return_value=0.0)
    return analytics


@pytest.fixture
def mock_budget():
    """Mock budget for testing"""
    budget = Mock()
    budget.can_spend = Mock(return_value=(True, None))
    budget.record_spending = Mock()
    budget.get_spent = Mock(return_value=0.0)
    budget.get_remaining = Mock(return_value=100.0)
    return budget


@pytest.fixture
def sample_request_data():
    """Sample request data for testing"""
    return {
        'provider': 'gpt',
        'prompt': 'Test prompt',
        'user_id': 'test_user_123',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.7,
        'max_tokens': 100
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'initial_balance': 100.0
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    yield
    # Reset any global state if needed
    # This ensures test isolation
