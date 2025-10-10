"""
End-to-end tests for complete OneFlow.AI workflows
E2E тесты для полных рабочих процессов OneFlow.AI
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from router import Router
from wallet import Wallet
from analytics import Analytics
from budget import Budget, BudgetPeriod
from config import Config
from pricing_tables import calculate_cost_in_credits, convert_legacy_request


@pytest.mark.e2e
class TestCompleteRequestFlow:
    """Test complete request flow from start to finish"""

    def test_simple_gpt_request_flow(self, mock_gpt_provider):
        """Test simple GPT request through entire system"""
        # Setup
        router = Router()
        router.register_provider(mock_gpt_provider)
        wallet = Wallet(initial_balance=100.0)
        analytics = Analytics()
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 50.0)
        
        # Mock cost calculation
        mock_gpt_provider.estimate_cost = Mock(return_value=5.0)
        
        # Execute request
        request = {'type': 'gpt', 'prompt': 'Hello world'}
        
        # Check budget
        can_spend, _ = budget.can_spend(5.0)
        assert can_spend is True
        
        # Check wallet
        assert wallet.can_afford(5.0)
        
        # Route request
        response = router.route_request(request)
        
        # Deduct from wallet
        wallet.deduct(5.0)
        
        # Record in budget and analytics
        budget.record_spending(5.0, provider='gpt')
        analytics.log_request('gpt', 5.0, request['prompt'], status='success')
        
        # Verify
        assert response is not None
        assert wallet.get_balance() == 95.0
        assert budget.get_spent(BudgetPeriod.DAILY) == 5.0
        assert analytics.get_request_count() == 1
        assert analytics.get_total_cost() == 5.0

    def test_multiple_requests_flow(self, mock_all_providers):
        """Test multiple requests through system"""
        # Setup
        router = Router()
        for provider in mock_all_providers.values():
            router.register_provider(provider)
        
        wallet = Wallet(initial_balance=200.0)
        analytics = Analytics()
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 100.0)
        
        # Define requests with costs
        requests = [
            ({'type': 'gpt', 'prompt': 'Test 1'}, 5.0),
            ({'type': 'image', 'prompt': 'Test 2'}, 10.0),
            ({'type': 'audio', 'prompt': 'Test 3'}, 3.0),
            ({'type': 'gpt', 'prompt': 'Test 4'}, 5.0),
        ]
        
        # Execute all requests
        for request_data, cost in requests:
            provider_type = request_data['type']
            
            # Check budget
            can_spend, _ = budget.can_spend(cost, provider=provider_type)
            if not can_spend:
                continue
            
            # Check wallet
            if not wallet.can_afford(cost):
                continue
            
            # Route and process
            response = router.route_request(request_data)
            wallet.deduct(cost)
            budget.record_spending(cost, provider=provider_type)
            analytics.log_request(provider_type, cost, request_data['prompt'], status='success')
        
        # Verify final state
        assert wallet.get_balance() == 177.0  # 200 - 23
        assert budget.get_spent(BudgetPeriod.DAILY) == 23.0
        assert analytics.get_request_count() == 4
        assert analytics.get_total_cost() == 23.0

    def test_budget_limit_prevents_request(self, mock_gpt_provider):
        """Test that budget limit prevents excessive requests"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        wallet = Wallet(initial_balance=1000.0)
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 20.0)
        
        # Try to make expensive request
        request = {'type': 'gpt', 'prompt': 'Expensive request'}
        cost = 25.0
        
        can_spend, reason = budget.can_spend(cost)
        
        assert can_spend is False
        assert "limit exceeded" in reason.lower()
        
        # Request should not be processed
        # Wallet remains unchanged
        assert wallet.get_balance() == 1000.0

    def test_insufficient_wallet_balance(self, mock_gpt_provider):
        """Test handling of insufficient wallet balance"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        wallet = Wallet(initial_balance=5.0)
        budget = Budget()
        analytics = Analytics()
        
        request = {'type': 'gpt', 'prompt': 'Test'}
        cost = 10.0
        
        # Budget check passes
        can_spend, _ = budget.can_spend(cost)
        assert can_spend is True
        
        # Wallet check fails
        can_afford = wallet.can_afford(cost)
        assert can_afford is False
        
        # Request should not be processed
        # Log as failed
        analytics.log_request('gpt', 0.0, request['prompt'], status='insufficient_balance')
        
        assert analytics.get_request_count() == 1
        assert analytics.get_total_cost() == 0.0

    def test_provider_budget_enforcement(self, mock_all_providers):
        """Test provider-specific budget enforcement"""
        router = Router()
        for provider in mock_all_providers.values():
            router.register_provider(provider)
        
        wallet = Wallet(initial_balance=500.0)
        budget = Budget()
        
        # Set provider-specific limits
        budget.set_provider_limit('gpt', 30.0)
        budget.set_provider_limit('image', 50.0)
        
        # GPT requests
        for i in range(5):
            request = {'type': 'gpt', 'prompt': f'GPT request {i}'}
            cost = 7.0
            
            can_spend, _ = budget.can_spend(cost, provider='gpt')
            if can_spend:
                router.route_request(request)
                wallet.deduct(cost)
                budget.record_spending(cost, provider='gpt')
        
        # Should have processed 4 requests (28.0), 5th would exceed
        assert budget.get_provider_spent('gpt') == 28.0
        assert wallet.get_balance() == 472.0

    def test_analytics_tracking_across_providers(self, mock_all_providers):
        """Test analytics tracking across multiple providers"""
        router = Router()
        for provider in mock_all_providers.values():
            router.register_provider(provider)
        
        analytics = Analytics()
        wallet = Wallet(initial_balance=1000.0)
        
        # Execute mixed requests
        requests_data = [
            ('gpt', 5.0, 'GPT prompt 1'),
            ('gpt', 5.0, 'GPT prompt 2'),
            ('image', 10.0, 'Image prompt 1'),
            ('audio', 3.0, 'Audio prompt 1'),
            ('gpt', 5.0, 'GPT prompt 3'),
        ]
        
        for provider_type, cost, prompt in requests_data:
            request = {'type': provider_type, 'prompt': prompt}
            router.route_request(request)
            wallet.deduct(cost)
            analytics.log_request(provider_type, cost, prompt, status='success')
        
        # Verify analytics
        stats = analytics.get_provider_stats()
        assert stats['gpt']['count'] == 3
        assert stats['gpt']['total_cost'] == 15.0
        assert stats['image']['count'] == 1
        assert stats['image']['total_cost'] == 10.0
        
        assert analytics.get_most_used_provider() == 'gpt'


@pytest.mark.e2e
class TestConfigurationFlow:
    """Test configuration-driven workflows"""

    def test_config_driven_setup(self, temp_config_file):
        """Test setting up system from configuration"""
        # Create config
        config = Config()
        config.set_rate('gpt', 2.0)
        config.set_rate('image', 15.0)
        config.set_wallet_balance(250.0)
        config.set_budget_limit('daily', 100.0)
        config.save_to_file(temp_config_file)
        
        # Load config in new instance
        loaded_config = Config(temp_config_file)
        
        # Setup system from config
        wallet = Wallet(initial_balance=loaded_config.wallet_balance)
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, loaded_config.budget_limits['daily'])
        
        assert wallet.get_balance() == 250.0
        assert budget.limits[BudgetPeriod.DAILY] == 100.0

    def test_multi_region_configuration(self):
        """Test configuration for different regions"""
        # US Config
        us_config = Config()
        us_config.set_region('US')
        us_config.set_rate('gpt', 1.0)
        
        # EU Config
        eu_config = Config()
        eu_config.set_region('EU')
        eu_config.set_rate('gpt', 1.2)  # Higher rate
        
        assert us_config.get_rate('gpt') < eu_config.get_rate('gpt')


@pytest.mark.e2e
class TestErrorRecoveryFlow:
    """Test error handling and recovery"""

    def test_provider_failure_recovery(self, mock_gpt_provider):
        """Test recovery from provider failure"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        analytics = Analytics()
        
        # Simulate provider failure
        mock_gpt_provider.__call__.side_effect = Exception("Provider error")
        
        request = {'type': 'gpt', 'prompt': 'Test'}
        
        try:
            router.route_request(request)
        except Exception as e:
            # Log failure
            analytics.log_request('gpt', 0.0, request['prompt'], status='error')
        
        # Verify error was logged
        stats = analytics.get_provider_stats()
        assert stats['gpt']['error_count'] == 1

    def test_partial_request_batch_failure(self, mock_gpt_provider):
        """Test handling partial failures in batch requests"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        wallet = Wallet(initial_balance=100.0)
        analytics = Analytics()
        
        # Mix of success and failure
        results = []
        for i in range(5):
            if i == 2:
                # Simulate failure on 3rd request
                mock_gpt_provider.__call__.side_effect = Exception("Error")
            else:
                mock_gpt_provider.__call__.side_effect = None
                mock_gpt_provider.__call__.return_value = f"Response {i}"
            
            request = {'type': 'gpt', 'prompt': f'Prompt {i}'}
            
            try:
                response = router.route_request(request)
                wallet.deduct(5.0)
                analytics.log_request('gpt', 5.0, request['prompt'], status='success')
                results.append(('success', response))
            except Exception:
                analytics.log_request('gpt', 0.0, request['prompt'], status='error')
                results.append(('error', None))
        
        # Verify mixed results
        success_count = sum(1 for status, _ in results if status == 'success')
        error_count = sum(1 for status, _ in results if status == 'error')
        
        assert success_count == 4
        assert error_count == 1
        assert wallet.get_balance() == 80.0  # Only 4 requests charged


@pytest.mark.e2e
class TestRealisticScenarios:
    """Test realistic usage scenarios"""

    def test_daily_usage_scenario(self, mock_all_providers):
        """Test realistic daily usage pattern"""
        # Setup
        router = Router()
        for provider in mock_all_providers.values():
            router.register_provider(provider)
        
        wallet = Wallet(initial_balance=1000.0)
        analytics = Analytics()
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 500.0)
        
        # Simulate daily usage pattern
        daily_requests = [
            ('gpt', 'Morning summary', 3.0),
            ('gpt', 'Email draft', 4.0),
            ('image', 'Logo design', 15.0),
            ('gpt', 'Code review', 5.0),
            ('audio', 'Podcast intro', 8.0),
            ('gpt', 'Documentation', 6.0),
            ('image', 'Social media post', 12.0),
            ('gpt', 'Evening report', 4.0),
        ]
        
        successful_requests = 0
        for provider_type, prompt, cost in daily_requests:
            request = {'type': provider_type, 'prompt': prompt}
            
            if budget.can_spend(cost)[0] and wallet.can_afford(cost):
                router.route_request(request)
                wallet.deduct(cost)
                budget.record_spending(cost, provider=provider_type)
                analytics.log_request(provider_type, cost, prompt, status='success')
                successful_requests += 1
        
        # All should succeed
        assert successful_requests == 8
        assert wallet.get_balance() == 943.0
        assert analytics.get_request_count() == 8

    def test_burst_traffic_handling(self, mock_gpt_provider):
        """Test handling of burst traffic"""
        router = Router()
        router.register_provider(mock_gpt_provider)
        wallet = Wallet(initial_balance=500.0)
        budget = Budget()
        budget.set_limit(BudgetPeriod.DAILY, 200.0)
        analytics = Analytics()
        
        # Simulate burst of 50 requests
        burst_size = 50
        cost_per_request = 3.0
        
        processed = 0
        for i in range(burst_size):
            request = {'type': 'gpt', 'prompt': f'Burst request {i}'}
            
            if budget.can_spend(cost_per_request)[0] and wallet.can_afford(cost_per_request):
                router.route_request(request)
                wallet.deduct(cost_per_request)
                budget.record_spending(cost_per_request)
                analytics.log_request('gpt', cost_per_request, request['prompt'], status='success')
                processed += 1
            else:
                break
        
        # Should process until budget limit (200/3 = 66 max, but starts at 0)
        assert processed > 0
        assert processed <= burst_size
        assert budget.get_spent(BudgetPeriod.DAILY) <= 200.0
