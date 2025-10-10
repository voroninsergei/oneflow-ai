"""
OneFlow.AI Main Module - Fixed Version
Главный модуль OneFlow.AI - Исправленная версия

Complete orchestrator implementation with all components integrated.
Полная реализация оркестратора со всеми интегрированными компонентами.
"""

from typing import Optional, Dict, Any
import sys

# Core components
from wallet import Wallet
from pricing import PricingCalculator
from router import Router

# Extended components (with fallback if not available)
try:
    from analytics import Analytics
    HAS_ANALYTICS = True
except ImportError:
    HAS_ANALYTICS = False

try:
    from budget import Budget, BudgetPeriod
    HAS_BUDGET = True
except ImportError:
    HAS_BUDGET = False

try:
    from config import Config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

# Providers
from providers.gpt_provider import GPTProvider
from providers.image_provider import ImageProvider
from providers.audio_provider import AudioProvider
from providers.video_provider import VideoProvider


class OneFlowAI:
    """
    Main orchestrator class for OneFlow.AI.
    Главный класс-оркестратор для OneFlow.AI.
    
    This class integrates all components: routing, pricing, wallet, analytics, and budget.
    Этот класс интегрирует все компоненты: маршрутизацию, ценообразование, кошелёк, аналитику и бюджет.
    """
    
    def __init__(
        self, 
        initial_balance: float = 100,
        use_real_api: bool = False,
        config_file: Optional[str] = None
    ):
        """
        Initialize OneFlow.AI system.
        
        Args:
            initial_balance: Initial wallet balance.
            use_real_api: Whether to use real API providers.
            config_file: Path to configuration file.
        """
        # Initialize core components
        self.wallet = Wallet(initial_balance=initial_balance)
        self.pricing = PricingCalculator()
        self.router = Router()
        self.use_real_api = use_real_api
        
        # Initialize optional components
        self.analytics = Analytics() if HAS_ANALYTICS else None
        self.budget = Budget() if HAS_BUDGET else None
        self.config = Config(config_file) if HAS_CONFIG and config_file else None
        
        # Setup system
        self._setup_pricing()
        self._setup_providers()
    
    def _setup_pricing(self):
        """Setup default pricing rates for all providers."""
        rates = {
            'gpt': 1.0,      # per word
            'image': 10.0,   # per image
            'audio': 5.0,    # per audio
            'video': 20.0    # per video
        }
        for provider, rate in rates.items():
            self.pricing.register_rate(provider, rate)
    
    def _setup_providers(self):
        """Setup providers based on API mode."""
        if self.use_real_api:
            self._setup_real_providers()
        else:
            self._setup_mock_providers()
    
    def _setup_real_providers(self):
        """Setup real API providers."""
        try:
            from real_api_integration import create_provider
            
            for provider_type in ['gpt', 'image', 'audio', 'video']:
                try:
                    provider = create_provider(provider_type, use_real_api=True)
                    self.router.register_provider(provider)
                except Exception as e:
                    print(f"Warning: Could not initialize {provider_type} provider: {e}")
                    # Fallback to mock for this provider
                    self._register_mock_provider(provider_type)
        except ImportError:
            print("Warning: Real API integration module not found. Using mock providers.")
            self._setup_mock_providers()
    
    def _setup_mock_providers(self):
        """Setup mock providers for testing."""
        self.router.register_provider(GPTProvider(name='gpt'))
        self.router.register_provider(ImageProvider(name='image'))
        self.router.register_provider(AudioProvider(name='audio'))
        self.router.register_provider(VideoProvider(name='video'))
    
    def _register_mock_provider(self, provider_type: str):
        """Register a single mock provider."""
        providers_map = {
            'gpt': GPTProvider,
            'image': ImageProvider,
            'audio': AudioProvider,
            'video': VideoProvider
        }
        if provider_type in providers_map:
            provider_class = providers_map[provider_type]
            self.router.register_provider(provider_class(name=provider_type))
    
    def process_request(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process AI request with full validation and tracking.
        Обработать AI запрос с полной валидацией и отслеживанием.
        
        Args:
            model: Model type (gpt, image, audio, video).
            prompt: Input prompt.
            **kwargs: Additional parameters.
        
        Returns:
            dict: Result with status, response, cost, and balance.
        """
        model_lower = model.lower()
        
        # Calculate cost based on model type
        if model_lower == 'gpt':
            cost_units = len(prompt.split())  # Cost per word
        else:
            cost_units = 1  # Flat rate for other models
        
        cost = self.pricing.estimate_cost(model_lower, cost_units)
        
        # Check budget if available
        if self.budget:
            can_spend, reason = self.budget.can_spend(cost, provider=model_lower)
            if not can_spend:
                return {
                    'status': 'error',
                    'message': f'Budget limit exceeded: {reason}',
                    'cost': 0,
                    'balance': self.wallet.get_balance()
                }
        
        # Check wallet balance
        if not self.wallet.can_afford(cost):
            return {
                'status': 'error',
                'message': f'Insufficient funds. Need {cost} credits, have {self.wallet.get_balance()}',
                'cost': cost,
                'balance': self.wallet.get_balance()
            }
        
        # Process request through router
        try:
            request_data = {'type': model_lower, 'prompt': prompt}
            response = self.router.route_request(request_data)
            
            if response is None:
                raise Exception(f"No provider available for type: {model_lower}")
            
            # Deduct cost
            self.wallet.deduct(cost)
            
            # Record spending in budget
            if self.budget:
                self.budget.record_spending(cost, provider=model_lower)
            
            # Log to analytics
            if self.analytics:
                self.analytics.log_request(
                    provider=model_lower,
                    cost=cost,
                    prompt=prompt,
                    status='success',
                    response=str(response)
                )
            
            return {
                'status': 'success',
                'response': response,
                'cost': cost,
                'balance': self.wallet.get_balance(),
                'provider': model_lower
            }
            
        except Exception as e:
            # Log error to analytics
            if self.analytics:
                self.analytics.log_request(
                    provider=model_lower,
                    cost=0,
                    prompt=prompt,
                    status='error',
                    response=str(e)
                )
            
            return {
                'status': 'error',
                'message': f'Provider error: {str(e)}',
                'cost': 0,
                'balance': self.wallet.get_balance()
            }
    
    def setup_budget(self, **limits):
        """
        Setup budget limits for different periods.
        Настроить лимиты бюджета для разных периодов.
        
        Args:
            **limits: Keyword arguments for period limits (daily, weekly, monthly, total).
        
        Example:
            system.setup_budget(daily=50, weekly=300)
        """
        if not self.budget:
            print("Warning: Budget module not available")
            return
        
        for period_name, amount in limits.items():
            if amount is not None:
                try:
                    period = BudgetPeriod[period_name.upper()]
                    self.budget.set_limit(period, amount)
                except KeyError:
                    print(f"Warning: Invalid budget period: {period_name}")
    
    def setup_provider_budget(self, provider: str, amount: float):
        """
        Setup budget limit for a specific provider.
        Настроить лимит бюджета для конкретного провайдера.
        
        Args:
            provider: Provider name (gpt, image, audio, video).
            amount: Budget limit amount.
        """
        if not self.budget:
            print("Warning: Budget module not available")
            return
        
        self.budget.set_provider_limit(provider, amount)
    
    def get_status(self) -> str:
        """
        Get formatted system status.
        Получить форматированный статус системы.
        
        Returns:
            str: Formatted status report.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("OneFlow.AI System Status | Статус системы OneFlow.AI")
        lines.append("=" * 60)
        lines.append(f"\nAPI Mode: {'Real API' if self.use_real_api else 'Mock (Demo)'}")
        lines.append(f"Balance: {self.wallet.get_balance():.2f} credits")
        
        if self.analytics:
            total_requests = self.analytics.get_request_count()
            total_cost = self.analytics.get_total_cost()
            
            lines.append(f"\nTotal Requests: {total_requests}")
            lines.append(f"Total Cost: {total_cost:.2f} credits")
            
            if total_requests > 0:
                avg_cost = self.analytics.get_average_cost_per_request()
                most_used = self.analytics.get_most_used_provider()
                
                lines.append(f"Average Cost per Request: {avg_cost:.2f} credits")
                lines.append(f"Most Used Provider: {most_used}")
        
        if self.budget:
            lines.append("\n" + "-" * 60)
            lines.append("Budget Status:")
            
            for period in [BudgetPeriod.DAILY, BudgetPeriod.WEEKLY, BudgetPeriod.MONTHLY]:
                remaining = self.budget.get_remaining(period)
                if remaining is not None:
                    spent = self.budget.get_spent(period)
                    limit = self.budget.limits[period]
                    lines.append(f"  {period.value.capitalize()}: {spent:.2f}/{limit:.2f} (remaining: {remaining:.2f})")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def add_credits(self, amount: float):
        """
        Add credits to wallet.
        Добавить кредиты в кошелёк.
        
        Args:
            amount: Amount to add.
        """
        self.wallet.add_credits(amount)
    
    def get_analytics_summary(self) -> Optional[str]:
        """
        Get analytics summary report.
        Получить сводный отчёт аналитики.
        
        Returns:
            str: Analytics report or None if analytics not available.
        """
        if not self.analytics:
            return "Analytics module not available"
        
        return self.analytics.get_summary_report()
    
    def get_budget_summary(self) -> Optional[str]:
        """
        Get budget summary report.
        Получить сводный отчёт бюджета.
        
        Returns:
            str: Budget report or None if budget not available.
        """
        if not self.budget:
            return "Budget module not available"
        
        return self.budget.get_budget_summary()


def run_workflow():
    """
    Run the main OneFlow.AI workflow demonstration.
    Запуск основного демонстрационного рабочего процесса OneFlow.AI.
    """
    print("=" * 60)
    print("OneFlow.AI - Interactive Demo")
    print("=" * 60)
    
    # Initialize system
    system = OneFlowAI(initial_balance=100, use_real_api=False)
    
    print(f"\nInitial balance: {system.wallet.get_balance()} credits")
    print("\nAvailable models: gpt, image, audio, video")
    
    # Interactive input
    try:
        model = input("\nEnter model type: ").strip()
        prompt = input("Enter your prompt: ").strip()
        
        if not model or not prompt:
            print("\nError: Model and prompt are required")
            return
        
        # Process request
        print("\nProcessing request...")
        result = system.process_request(model, prompt)
        
        # Display result
        print("\n" + "=" * 60)
        if result['status'] == 'success':
            print("✓ Request Successful")
            print(f"\nResponse: {result['response']}")
            print(f"Cost: {result['cost']} credits")
            print(f"Remaining Balance: {result['balance']} credits")
        else:
            print("✗ Request Failed")
            print(f"\nError: {result['message']}")
            print(f"Balance: {result['balance']} credits")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")


def main():
    """
    Main entry point.
    Главная точка входа.
    """
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Run demo with predefined scenarios
        print("Running demo mode...")
        system = OneFlowAI(initial_balance=100)
        
        # Demo scenario
        scenarios = [
            ('gpt', 'Hello world'),
            ('image', 'Beautiful sunset'),
            ('audio', 'Relaxing music'),
        ]
        
        for model, prompt in scenarios:
            print(f"\n--- Testing {model} ---")
            result = system.process_request(model, prompt)
            print(f"Status: {result['status']}")
            if result['status'] == 'success':
                print(f"Cost: {result['cost']} credits")
            else:
                print(f"Error: {result.get('message')}")
        
        # Show final status
        print("\n" + system.get_status())
    else:
        # Run interactive mode
        run_workflow()


if __name__ == '__main__':
    main()
