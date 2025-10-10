"""
OneFlow.AI Main Module - ИСПРАВЛЕНО
Главный модуль OneFlow.AI - ИСПРАВЛЕНО

Полная реализация класса OneFlowAI с интеграцией всех компонентов.
"""

from typing import Optional, Dict, Any
import sys

# Core components
from wallet import Wallet
from pricing import PricingCalculator
from router import Router

# Extended components
try:
    from analytics import Analytics
    HAS_ANALYTICS = True
except ImportError:
    HAS_ANALYTICS = False
    print("Warning: Analytics module not available")

try:
    from budget import Budget, BudgetPeriod
    HAS_BUDGET = True
except ImportError:
    HAS_BUDGET = False
    print("Warning: Budget module not available")

try:
    from config import Config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("Warning: Config module not available")

# Providers
from providers.gpt_provider import GPTProvider
from providers.image_provider import ImageProvider
from providers.audio_provider import AudioProvider
from providers.video_provider import VideoProvider


class OneFlowAI:
    """
    Main orchestrator class for OneFlow.AI.
    Главный класс-оркестратор для OneFlow.AI.
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
        if HAS_ANALYTICS:
            self.analytics = Analytics()
        else:
            self.analytics = None
            
        if HAS_BUDGET:
            self.budget = Budget()
        else:
            self.budget = None
            
        if HAS_CONFIG and config_file:
            self.config = Config(config_file)
        else:
            self.config = None
        
        # Setup system
        self._setup_pricing()
        self._setup_providers()
    
    def _setup_pricing(self):
        """Setup default pricing rates."""
        rates = {
            'gpt': 1.0,
            'image': 10.0,
            'audio': 5.0,
            'video': 20.0
        }
        for provider, rate in rates.items():
            self.pricing.register_rate(provider, rate)
    
    def _setup_providers(self):
        """Setup providers based on API mode."""
        if self.use_real_api:
            try:
                from real_api_integration import create_provider
                for ptype in ['gpt', 'image', 'audio', 'video']:
                    try:
                        provider = create_provider(ptype, use_real_api=True)
                        self.router.register_provider(provider)
                    except:
                        self._register_mock_provider(ptype)
            except ImportError:
                self._setup_mock_providers()
        else:
            self._setup_mock_providers()
    
    def _setup_mock_providers(self):
        """Setup mock providers."""
        self.router.register_provider(GPTProvider(name='gpt'))
        self.router.register_provider(ImageProvider(name='image'))
        self.router.register_provider(AudioProvider(name='audio'))
        self.router.register_provider(VideoProvider(name='video'))
    
    def _register_mock_provider(self, provider_type: str):
        """Register single mock provider."""
        providers_map = {
            'gpt': GPTProvider,
            'image': ImageProvider,
            'audio': AudioProvider,
            'video': VideoProvider
        }
        if provider_type in providers_map:
            self.router.register_provider(
                providers_map[provider_type](name=provider_type)
            )
    
    def process_request(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process AI request.
        
        Args:
            model: Model type (gpt, image, audio, video).
            prompt: Input prompt.
        
        Returns:
            dict: Result with status, response, cost, balance.
        """
        model_lower = model.lower()
        
        # Calculate cost
        if model_lower == 'gpt':
            cost_units = len(prompt.split())
        else:
            cost_units = 1
        
        cost = self.pricing.estimate_cost(model_lower, cost_units)
        
        # Check budget
        if self.budget:
            can_spend, reason = self.budget.can_spend(cost, provider=model_lower)
            if not can_spend:
                return {
                    'status': 'error',
                    'message': f'Budget limit: {reason}',
                    'cost': 0,
                    'balance': self.wallet.get_balance()
                }
        
        # Check wallet
        if not self.wallet.can_afford(cost):
            return {
                'status': 'error',
                'message': f'Insufficient funds',
                'cost': cost,
                'balance': self.wallet.get_balance()
            }
        
        # Process request
        try:
            request_data = {'type': model_lower, 'prompt': prompt}
            response = self.router.route_request(request_data)
            
            if response is None:
                raise Exception(f"No provider for: {model_lower}")
            
            # Deduct cost
            self.wallet.deduct(cost)
            
            # Record spending
            if self.budget:
                self.budget.record_spending(cost, provider=model_lower)
            
            # Log analytics
            if self.analytics:
                self.analytics.log_request(
                    model_lower, cost, prompt,
                    status='success', response=str(response)
                )
            
            return {
                'status': 'success',
                'response': response,
                'cost': cost,
                'balance': self.wallet.get_balance(),
                'provider': model_lower
            }
            
        except Exception as e:
            if self.analytics:
                self.analytics.log_request(
                    model_lower, 0, prompt,
                    status='error', response=str(e)
                )
            
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'cost': 0,
                'balance': self.wallet.get_balance()
            }
    
    def setup_budget(self, **limits):
        """Setup budget limits."""
        if not self.budget:
            return
        
        for period_name, amount in limits.items():
            if amount is not None:
                try:
                    period = BudgetPeriod[period_name.upper()]
                    self.budget.set_limit(period, amount)
                except KeyError:
                    pass
    
    def setup_provider_budget(self, provider: str, amount: float):
        """Setup provider budget."""
        if self.budget:
            self.budget.set_provider_limit(provider, amount)
    
    def get_status(self) -> str:
        """Get system status."""
        lines = ["=" * 60]
        lines.append("OneFlow.AI Status")
        lines.append("=" * 60)
        lines.append(f"\nMode: {'Real API' if self.use_real_api else 'Mock'}")
        lines.append(f"Balance: {self.wallet.get_balance():.2f} credits")
        
        if self.analytics:
            lines.append(f"Requests: {self.analytics.get_request_count()}")
            lines.append(f"Total cost: {self.analytics.get_total_cost():.2f}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def add_credits(self, amount: float):
        """Add credits."""
        self.wallet.add_credits(amount)
    
    def get_analytics_summary(self) -> Optional[str]:
        """Get analytics summary."""
        if self.analytics:
            return self.analytics.get_summary_report()
        return "Analytics not available"
    
    def get_budget_summary(self) -> Optional[str]:
        """Get budget summary."""
        if self.budget:
            return self.budget.get_budget_summary()
        return "Budget not available"


def run_workflow():
    """Run interactive workflow."""
    print("=" * 60)
    print("OneFlow.AI - Interactive Demo")
    print("=" * 60)
    
    system = OneFlowAI(initial_balance=100, use_real_api=False)
    
    print(f"\nInitial balance: {system.wallet.get_balance()} credits")
    print("\nAvailable models: gpt, image, audio, video")
    
    try:
        model = input("\nEnter model: ").strip()
        prompt = input("Enter prompt: ").strip()
        
        if not model or not prompt:
            print("\nError: Model and prompt required")
            return
        
        print("\nProcessing...")
        result = system.process_request(model, prompt)
        
        print("\n" + "=" * 60)
        if result['status'] == 'success':
            print("✓ Success")
            print(f"\nResponse: {result['response']}")
            print(f"Cost: {result['cost']} credits")
            print(f"Balance: {result['balance']} credits")
        else:
            print("✗ Failed")
            print(f"\nError: {result['message']}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        system = OneFlowAI(initial_balance=100)
        
        scenarios = [
            ('gpt', 'Hello world'),
            ('image', 'Sunset'),
        ]
        
        for model, prompt in scenarios:
            print(f"\n--- {model} ---")
            result = system.process_request(model, prompt)
            print(f"Status: {result['status']}")
        
        print("\n" + system.get_status())
    else:
        run_workflow()


if __name__ == '__main__':
    main()
