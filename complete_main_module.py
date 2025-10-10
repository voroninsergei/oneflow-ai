"""
OneFlow.AI - Complete Production-Ready System
Author: Sergey Voronin

Enhanced version with real API integration, analytics, and budget management.
Улучшенная версия с интеграцией реальных API, аналитикой и управлением бюджетом.
"""

import sys
import os
from typing import Optional, Dict, Any

# Import core modules
from router import Router
from pricing import PricingCalculator
from wallet import Wallet
from analytics import Analytics
from budget import Budget, BudgetPeriod
from config import Config, get_config


class OneFlowAI:
    """
    Complete OneFlow.AI system orchestrator with real API support.
    Полный оркестратор системы OneFlow.AI с поддержкой реальных API.
    """
    
    def __init__(self, initial_balance: float = 100, use_real_api: bool = False,
                 config_file: Optional[str] = None):
        """
        Initialize OneFlow.AI system.
        Инициализировать систему OneFlow.AI.
        
        Args:
            initial_balance: Starting wallet balance.
            use_real_api: Whether to use real API providers or mocks.
            config_file: Optional configuration file path.
        """
        self.wallet = Wallet(initial_balance=initial_balance)
        self.pricing = PricingCalculator()
        self.router = Router()
        self.analytics = Analytics()
        self.budget = Budget()
        self.use_real_api = use_real_api
        
        # Load configuration if provided
        self.config = Config(config_file) if config_file else get_config()
        
        self._setup_providers()
        self._setup_pricing()
        self._apply_config()
    
    def _setup_providers(self):
        """
        Register all available providers (real or mock).
        Зарегистрировать всех доступных провайдеров (реальных или mock).
        """
        if self.use_real_api:
            try:
                from real_api_integration import create_provider
                
                providers = [
                    create_provider('gpt', use_real_api=True),
                    create_provider('image', use_real_api=True),
                    create_provider('audio', use_real_api=True),
                    create_provider('video', use_real_api=True)
                ]
                
                for provider in providers:
                    self.router.register_provider(provider)
                
                print("✓ Real API providers initialized")
            except ImportError as e:
                print(f"⚠ Warning: Could not load real API providers: {e}")
                print("  Falling back to mock providers")
                self._setup_mock_providers()
        else:
            self._setup_mock_providers()
    
    def _setup_mock_providers(self):
        """Register mock providers for testing."""
        from providers.gpt_provider import GPTProvider
        from providers.image_provider import ImageProvider
        from providers.audio_provider import AudioProvider
        from providers.video_provider import VideoProvider
        
        providers = [
            GPTProvider(name='gpt'),
            ImageProvider(name='image'),
            AudioProvider(name='audio'),
            VideoProvider(name='video')
        ]
        
        for provider in providers:
            self.router.register_provider(provider)
    
    def _setup_pricing(self):
        """
        Register pricing rates for all providers.
        Зарегистрировать тарифы для всех провайдеров.
        """
        # Use rates from config if available
        rates = self.config.get_all_rates()
        for provider, rate in rates.items():
            self.pricing.register_rate(provider, rate)
    
    def _apply_config(self):
        """
        Apply configuration settings to the system.
        Применить настройки конфигурации к системе.
        """
        # Apply budget limits from config
        for period_name, limit in self.config.budget_limits.items():
            if limit is not None:
                try:
                    period = BudgetPeriod[period_name.upper()]
                    self.budget.set_limit(period, limit)
                except KeyError:
                    pass
        
        # Apply provider budgets from config
        for provider, limit in self.config.provider_budgets.items():
            if limit is not None:
                self.budget.set_provider_limit(provider, limit)
    
    def setup_budget(self, daily: float = None, weekly: float = None,
                    monthly: float = None, total: float = None):
        """
        Setup budget limits.
        Установить лимиты бюджета.
        
        Args:
            daily: Daily spending limit.
            weekly: Weekly spending limit.
            monthly: Monthly spending limit.
            total: Total spending limit.
        """
        if daily is not None:
            self.budget.set_limit(BudgetPeriod.DAILY, daily)
        if weekly is not None:
            self.budget.set_limit(BudgetPeriod.WEEKLY, weekly)
        if monthly is not None:
            self.budget.set_limit(BudgetPeriod.MONTHLY, monthly)
        if total is not None:
            self.budget.set_limit(BudgetPeriod.TOTAL, total)
    
    def setup_provider_budget(self, provider: str, limit: float):
        """
        Setup budget limit for specific provider.
        Установить лимит бюджета для конкретного провайдера.
        
        Args:
            provider: Provider name.
            limit: Spending limit for this provider.
        """
        self.budget.set_provider_limit(provider, limit)
    
    def process_request(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process an AI request with full validation and tracking.
        Обработать запрос к AI с полной валидацией и отслеживанием.
        
        Args:
            model: Model type (gpt, image, audio, video).
            prompt: User prompt.
            **kwargs: Additional parameters for API calls.
        
        Returns:
            dict: Result with status, response, cost, and balance.
        """
        model_lower = model.lower()
        
        # Validate model type
        if not self.pricing.has_provider(model_lower):
            return {
                'status': 'error',
                'message': f'Unknown model: {model}. Available: gpt, image, audio, video',
                'balance': self.wallet.get_balance()
            }
        
        # Calculate cost
        if model_lower == 'gpt':
            cost_units = len(prompt.split())
        else:
            cost_units = 1
        
        cost = self.pricing.estimate_cost(model_lower, cost_units)
        
        # Check budget limits
        can_spend, budget_reason = self.budget.can_spend(cost, provider=model_lower)
        if not can_spend:
            self.analytics.log_request(model_lower, cost, prompt, status='budget_exceeded')
            return {
                'status': 'error',
                'message': f'Budget limit: {budget_reason}',
                'cost': cost,
                'balance': self.wallet.get_balance()
            }
        
        # Check wallet balance
        if not self.wallet.can_afford(cost):
            self.analytics.log_request(model_lower, cost, prompt, status='insufficient_funds')
            return {
                'status': 'error',
                'message': f'Insufficient funds. Required: {cost}, Available: {self.wallet.get_balance()}',
                'cost': cost,
                'balance': self.wallet.get_balance()
            }
        
        # Process request
        try:
            self.wallet.deduct(cost)
            self.budget.record_spending(cost, provider=model_lower)
            
            request = {'type': model_lower, 'prompt': prompt, **kwargs}
            response = self.router.route_request(request)
            
            # Check if response contains an error
            if isinstance(response, dict) and 'error' in response:
                # Refund the cost if API call failed
                self.wallet.add_credits(cost)
                self.budget.record_spending(-cost, provider=model_lower)
                
                self.analytics.log_request(model_lower, 0, prompt, status='api_error',
                                         response=response.get('error', 'Unknown error'))
                
                return {
                    'status': 'error',
                    'message': response['error'],
                    'cost': 0,
                    'balance': self.wallet.get_balance()
                }
            
            # Log successful request
            self.analytics.log_request(model_lower, cost, prompt, status='success',
                                      response=str(response))
            
            return {
                'status': 'success',
                'response': response,
                'cost': cost,
                'balance': self.wallet.get_balance()
            }
        
        except Exception as e:
            # Refund on unexpected error
            self.wallet.add_credits(cost)
            self.analytics.log_request(model_lower, 0, prompt, status='error',
                                      response=str(e))
            
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'cost': 0,
                'balance': self.wallet.get_balance()
            }
    
    def get_status(self) -> str:
        """
        Get current system status.
        Получить текущий статус системы.
        
        Returns:
            str: Formatted status report.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("OneFlow.AI System Status | Статус системы OneFlow.AI")
        lines.append("=" * 60)
        lines.append(f"\nAPI Mode | Режим API: {'Real' if self.use_real_api else 'Mock (Demo)'}")
        lines.append(f"Wallet Balance | Баланс кошелька: {self.wallet.get_balance():.2f} credits")
        lines.append(f"Total Requests | Всего запросов: {self.analytics.get_request_count()}")
        lines.append(f"Total Spent | Всего потрачено: {self.analytics.get_total_cost():.2f} credits")
        
        if self.analytics.get_request_count() > 0:
            lines.append(f"Average Cost | Средняя стоимость: {self.analytics.get_average_cost_per_request():.2f} credits")
            lines.append(f"Most Used | Чаще всего: {self.analytics.get_most_used_provider()}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def run_interactive_mode():
    """
    Run OneFlow.AI in interactive mode.
    Запустить OneFlow.AI в интерактивном режиме.
    """
    print("=" * 60)
    print("Welcome to OneFlow.AI | Добро пожаловать в OneFlow.AI")
    print("=" * 60)
    
    # Ask about API mode
    use_real = input("\nUse real API providers? (y/n) [n]: ").strip().lower() == 'y'
    
    if use_real:
        print("\n⚠ Real API mode requires API keys configured in .api_keys.json")
        print("   Run: python setup_keys.py to configure keys")
        confirm = input("   Continue with real API? (y/n) [y]: ").strip().lower()
        if confirm == 'n':
            use_real = False
    
    system = OneFlowAI(initial_balance=100, use_real_api=use_real)
    
    # Optional: Setup budgets
    setup_budgets = input("\nSetup budget limits? (y/n) [n]: ").strip().lower()
    if setup_budgets == 'y':
        try:
            daily = input("Daily limit (press Enter to skip): ").strip()
            if daily:
                system.setup_budget(daily=float(daily))
            
            weekly = input("Weekly limit (press Enter to skip): ").strip()
            if weekly:
                system.setup_budget(weekly=float(weekly))
            
            print("\n✓ Budget limits configured")
        except ValueError:
            print("✗ Invalid input, skipping budget setup")
    
    print("\n" + system.get_status())
    print("\nAvailable models: gpt, image, audio, video")
    print("Commands: request, status, analytics, budget, add-credits, quit")
    
    while True:
        print("\n" + "-" * 60)
        command = input("\nEnter command: ").strip().lower()
        
        if command == 'quit':
            print("\n" + system.analytics.get_summary_report())
            print("\nThank you for using OneFlow.AI!")
            break
        
        elif command == 'status':
            print(system.get_status())
        
        elif command == 'analytics':
            print(system.analytics.get_summary_report())
        
        elif command == 'budget':
            print(system.budget.get_budget_summary())
        
        elif command == 'add-credits':
            try:
                amount = float(input("Amount to add: ").strip())
                system.wallet.add_credits(amount)
                print(f"✓ Added {amount:.2f} credits")
                print(f"  New balance: {system.wallet.get_balance():.2f} credits")
            except ValueError:
                print("✗ Invalid amount")
        
        elif command == 'request':
            model = input("Model type (gpt/image/audio/video): ").strip()
            prompt = input("Your prompt: ").strip()
            
            if not prompt:
                print("✗ Error: Prompt cannot be empty")
                continue
            
            print(f"\n⏳ Processing request...")
            result = system.process_request(model, prompt)
            
            if result['status'] == 'success':
                print(f"\n✓ Success!")
                print(f"✓ Cost: {result['cost']:.2f} credits")
                print(f"✓ Response: {result['response']}")
                print(f"✓ Balance: {result['balance']:.2f} credits")
            else:
                print(f"\n✗ Error: {result['message']}")
                print(f"✗ Balance: {result['balance']:.2f} credits")
        
        else:
            print("Unknown command. Available: request, status, analytics, budget, add-credits, quit")


def run_demo():
    """
    Run OneFlow.AI demonstration.
    Запустить демонстрацию OneFlow.AI.
    """
    print("=" * 60)
    print("OneFlow.AI Demo Mode | Демонстрационный режим")
    print("=" * 60)
    
    system = OneFlowAI(initial_balance=100, use_real_api=False)
    
    # Setup budgets for demo
    system.setup_budget(daily=80)
    system.setup_provider_budget('video', 30)
    
    print("\n✓ Budget configured: Daily limit 80 credits, Video limit 30 credits")
    print(system.get_status())
    
    demo_requests = [
        ('gpt', 'Hello world how are you today'),
        ('image', 'Beautiful sunset over mountains'),
        ('audio', 'Peaceful piano music'),
        ('video', 'Cat playing with yarn'),
        ('gpt', 'Write a short poem about AI'),
        ('video', 'Dog running in park'),  # This should exceed video budget
        ('gpt', 'Explain quantum computing'),  # This might exceed daily budget
    ]
    
    print("\n" + "=" * 60)
    print("Processing Demo Requests | Обработка демо-запросов")
    print("=" * 60)
    
    for i, (model, prompt) in enumerate(demo_requests, 1):
        print(f"\n--- Request {i}/{len(demo_requests)} ---")
        print(f"Model: {model}")
        print(f"Prompt: {prompt}")
        
        result = system.process_request(model, prompt)
        
        if result['status'] == 'success':
            print(f"✓ Success! Cost: {result['cost']:.2f} credits")
            print(f"✓ Balance: {result['balance']:.2f} credits")
        else:
            print(f"✗ Failed: {result['message']}")
            print(f"✗ Balance: {result['balance']:.2f} credits")
    
    print("\n" + "=" * 60)
    print("Demo Complete | Демонстрация завершена")
    print("=" * 60)
    
    print("\n" + system.analytics.get_summary_report())
    print("\n" + system.budget.get_budget_summary())
    print(system.get_status())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        run_demo()
    else:
        run_interactive_mode()