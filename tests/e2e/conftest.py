"""
Shared fixtures for end-to-end tests
Общие фикстуры для e2e тестов
"""

import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from router import Router
from wallet import Wallet
from analytics import Analytics
from budget import Budget, BudgetPeriod
from config import Config
from database import DatabaseManager


@pytest.fixture
def full_system_setup(mock_all_providers):
    """Setup complete system with all components"""
    router = Router()
    for provider in mock_all_providers.values():
        router.register_provider(provider)
    
    wallet = Wallet(initial_balance=1000.0)
    analytics = Analytics()
    budget = Budget()
    budget.set_limit(BudgetPeriod.DAILY, 500.0)
    budget.set_limit(BudgetPeriod.WEEKLY, 2000.0)
    budget.set_limit(BudgetPeriod.MONTHLY, 8000.0)
    
    config = Config()
    
    return {
        'router': router,
        'wallet': wallet,
        'analytics': analytics,
        'budget': budget,
        'config': config
    }


@pytest.fixture
def system_with_db(mock_all_providers, temp_db_file):
    """Setup system with database integration"""
    router = Router()
    for provider in mock_all_providers.values():
        router.register_provider(provider)
    
    wallet = Wallet(initial_balance=1000.0)
    analytics = Analytics()
    budget = Budget()
    
    db_url = f'sqlite:///{temp_db_file}'
    db_manager = DatabaseManager(database_url=db_url)
    
    return {
        'router': router,
        'wallet': wallet,
        'analytics': analytics,
        'budget': budget,
        'db': db_manager
    }


@pytest.fixture
def realistic_config():
    """Realistic configuration for production-like testing"""
    config = Config()
    
    # Provider rates
    config.set_rate('gpt', 1.5)
    config.set_rate('image', 12.0)
    config.set_rate('audio', 5.0)
    config.set_rate('video', 20.0)
    
    # Budget limits
    config.set_budget_limit('daily', 100.0)
    config.set_budget_limit('weekly', 600.0)
    config.set_budget_limit('monthly', 2500.0)
    
    # Provider budgets
    config.set_provider_budget('gpt', 50.0)
    config.set_provider_budget('image', 150.0)
    
    # Wallet
    config.set_wallet_balance(500.0)
    
    # Region
    config.set_region('US')
    
    return config


@pytest.fixture
def request_factory():
    """Factory for creating test requests"""
    def _create_request(provider='gpt', prompt='Test', **kwargs):
        request = {
            'type': provider,
            'prompt': prompt,
            'user_id': kwargs.get('user_id', 'test_user'),
        }
        request.update(kwargs)
        return request
    return _create_request


@pytest.fixture
def batch_requests(request_factory):
    """Generate batch of test requests"""
    return [
        request_factory('gpt', f'GPT prompt {i}')
        for i in range(10)
    ]


@pytest.fixture(autouse=True)
def cleanup_after_e2e():
    """Cleanup after e2e tests"""
    yield
    # Cleanup any resources
    # Reset global state if needed


@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests"""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            self.metrics['duration'] = self.end_time - self.start_time
        
        def get_duration(self):
            return self.metrics.get('duration', 0)
        
        def record_metric(self, name, value):
            self.metrics[name] = value
    
    return PerformanceMonitor()


@pytest.fixture
def stress_test_requests(request_factory):
    """Generate large batch for stress testing"""
    return [
        request_factory('gpt', f'Stress test {i}')
        for i in range(100)
    ]
