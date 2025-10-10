"""
OneFlow.AI - Main Module with Database Integration
Главный модуль OneFlow.AI с интеграцией базы данных

Enhanced version with database persistence for all operations.
Улучшенная версия с сохранением всех операций в базе данных.
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

# Import database module
from database import get_db_manager, DatabaseManager


class OneFlowAIWithDB:
    """
    OneFlow.AI system with database persistence.
    Система OneFlow.AI с сохранением в базе данных.
    """
    
    def __init__(self, initial_balance: float = 100, use_real_api: bool = False,
                 config_file: Optional[str] = None, database_url: Optional[str] = None,
                 user_id: Optional[int] = None):
        """
        Initialize OneFlow.AI system with database.
        Инициализировать систему OneFlow.AI с базой данных.
        
        Args:
            initial_balance: Starting wallet balance.
            use_real_api: Whether to use real API providers.
            config_file: Optional configuration file path.
            database_url: Database connection URL.
            user_id: User ID for multi-user support.
        """
        # Initialize database
        self.db = get_db_manager(database_url)
        self.user_id = user_id
        
        # Load or create user
        if user_id:
            user = self.db.get_user(user_id)
            if user:
                initial_balance = user.balance
            else:
                raise ValueError(f"User with ID {user_id} not found")
        
        # Initialize core components
        self.wallet = Wallet(initial_balance=initial_balance)
        self.pricing = PricingCalculator()
        self.router = Router()
        self.analytics = Analytics()
        self.budget = Budget()
        self.use_real_api = use_real_api
        
        # Load configuration
        self.config = Config(config_file) if config_file else get_config()
        
        self._setup_providers()
        self._setup_pricing_from_db()
        self._apply_config()
        
        print(f"✓ OneFlow.AI initialized with database")
        print(f"  Database: {self.db.engine.url}")
        print(f"  User ID: {self.user_id or 'None (single-user mode)'}")
    
    def _setup_providers(self):
        """Register all available providers."""
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
    
    def _setup_pricing_from_db(self):
        """
        Load pricing rates from database.
        Загрузить тарифы из базы данных.
        """
        providers = self.db.get_all_providers()
        
        if providers:
            # Load from database
            for provider in providers:
                self.pricing.register_rate(provider.provider_name, provider.rate_per_unit)
            print(f"✓ Loaded {len(providers)} provider rates from database")
        else:
            # Initialize default rates in database
            default_rates = {
                'gpt': 1.0,
                'image': 10.0,
                'audio': 5.0,
                'video': 20.0
            }
            
            for provider, rate in default_rates.items():
                self.pricing.register_rate(provider, rate)
                self.db.create_or_update_provider(provider, rate)
            
            print("✓ Initialized default provider rates in database")
    
    def _apply_config(self):
        """Apply configuration settings."""
        for period_name, limit in self.config.budget_limits.items():
            if limit is not None:
                try:
                    period = BudgetPeriod[period_name.upper()]
                    self.budget.set_limit(period, limit)
                except KeyError:
                    pass
        
        for provider, limit in self.config.provider_budgets.items():
            if limit is not None:
                self.budget.set_provider_limit(provider, limit)
    
    def process_request(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process an AI request with database persistence.
        Обработать запрос к AI с сохранением в БД.
        
        Args:
            model: Model type (gpt, image, audio, video).
            prompt: User prompt.
            **kwargs: Additional parameters.
        
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
            # Log failed request to database
            self.db.create_request(
                user_id=self.user_id,
                provider=model_lower,
                model=model_lower,
                prompt=prompt,
                response=None,
                cost=0,
                status='budget_exceeded',
                error_message=budget_reason
            )
            
            self.analytics.log_request(model_lower, cost, prompt, status='budget_exceeded')
            return {
                'status': 'error',
                'message': f'Budget limit: {budget_reason}',
                'cost': cost,
                'balance': self.wallet.get_balance()
            }
        
        # Check wallet balance
        if not self.wallet.can_afford(cost):
            # Log failed request to database
            self.db.create_request(
                user_id=self.user_id,
                provider=model_lower,
                model=model_lower,
                prompt=prompt,
                response=None,
                cost=0,
                status='insufficient_funds',
                error_message=f'Required: {cost}, Available: {self.wallet.get_balance()}'
            )
            
            self.analytics.log_request(model_lower, cost, prompt, status='insufficient_funds')
            return {
                'status': 'error',
                'message': f'Insufficient funds. Required: {cost}, Available: {self.wallet.get_balance()}',
                'cost': cost,
                'balance': self.wallet.get_balance()
            }
        
        # Process request
        try:
            balance_before = self.wallet.get_balance()
            self.wallet.deduct(cost)
            balance_after = self.wallet.get_balance()
            
            # Record transaction
            self.budget.record_spending(cost, provider=model_lower)
            
            # Execute request
            request_data = {'type': model_lower, 'prompt': prompt, **kwargs}
            response = self.router.route_request(request_data)
            
            # Check if response contains an error
            if isinstance(response, dict) and 'error' in response:
                # Refund the cost if API call failed
                self.wallet.add_credits(cost)
                self.budget.record_spending(-cost, provider=model_lower)
                
                # Log failed request to database
                db_request = self.db.create_request(
                    user_id=self.user_id,
                    provider=model_lower,
                    model=model_lower,
                    prompt=prompt,
                    response=None,
                    cost=0,
                    status='api_error',
                    error_message=response.get('error', 'Unknown error')
                )
                
                self.analytics.log_request(model_lower, 0, prompt, status='api_error',
                                         response=response.get('error', 'Unknown error'))
                
                return {
                    'status': 'error',
                    'message': response['error'],
                    'cost': 0,
                    'balance': self.wallet.get_balance()
                }
            
            # Log successful request to database
            db_request = self.db.create_request(
                user_id=self.user_id,
                provider=model_lower,
                model=model_lower,
                prompt=prompt,
                response=str(response),
                cost=cost,
                status='success'
            )
            
            # Create transaction record
            self.db.create_transaction(
                user_id=self.user_id,
                type='deduct',
                amount=cost,
                balance_before=balance_before,
                balance_after=balance_after,
                description=f'{model_lower} request',
                request_id=db_request.id
            )
            
            # Update user balance in database
            if self.user_id:
                self.db.update_user_balance(self.user_id, balance_after)
            
            self.analytics.log_request(model_lower, cost, prompt, status='success',
                                      response=str(response))
            
            return {
                'status': 'success',
                'response': response,
                'cost': cost,
                'balance': self.wallet.get_balance(),
                'request_id': db_request.id
            }
        
        except Exception as e:
            # Refund on unexpected error
            self.wallet.add_credits(cost)
            
            # Log error to database
            self.db.create_request(
                user_id=self.user_id,
                provider=model_lower,
                model=model_lower,
                prompt=prompt,
                response=None,
                cost=0,
                status='error',
                error_message=str(e)
            )
            
            self.analytics.log_request(model_lower, 0, prompt, status='error',
                                      response=str(e))
            
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'cost': 0,
                'balance': self.wallet.get_balance()
            }
    
    def add_credits(self, amount: float, description: str = "Manual credit addition") -> Dict[str, Any]:
        """
        Add credits to wallet with database persistence.
        Добавить кредиты в кошелёк с сохранением в БД.
        
        Args:
            amount: Amount to add.
            description: Transaction description.
        
        Returns:
            dict: Result with new balance.
        """
        balance_before = self.wallet.get_balance()
        self.wallet.add_credits(amount)
        balance_after = self.wallet.get_balance()
        
        # Create transaction record
        self.db.create_transaction(
            user_id=self.user_id,
            type='add',
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description
        )
        
        # Update user balance in database
        if self.user_id:
            self.db.update_user_balance(self.user_id, balance_after)
        
        return {
            'status': 'success',
            'amount': amount,
            'balance': balance_after
        }
    
    def get_status(self) -> str:
        """Get current system status."""
        lines = []
        lines.append("=" * 60)
        lines.append("OneFlow.AI System Status (with Database)")
        lines.append("=" * 60)
        lines.append(f"\nAPI Mode: {'Real' if self.use_real_api else 'Mock (Demo)'}")
        lines.append(f"User ID: {self.user_id or 'Single-user mode'}")
        lines.append(f"Wallet Balance: {self.wallet.get_balance():.2f} credits")
        lines.append(f"Total Requests: {self.analytics.get_request_count()}")
        lines.append(f"Total Spent: {self.analytics.get_total_cost():.2f} credits")
        
        if self.analytics.get_request_count() > 0:
            lines.append(f"Average Cost: {self.analytics.get_average_cost_per_request():.2f} credits")
            lines.append(f"Most Used: {self.analytics.get_most_used_provider()}")
        
        # Database statistics
        db_request_count = self.db.get_request_count(self.user_id)
        db_total_cost = self.db.get_total_cost(self.user_id)
        
        lines.append("\nDatabase Statistics:")
        lines.append(f"  Total Requests in DB: {db_request_count}")
        lines.append(f"  Total Cost in DB: {db_total_cost:.2f} credits")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def get_request_history(self, limit: int = 10) -> list:
        """
        Get request history from database.
        Получить историю запросов из БД.
        
        Args:
            limit: Maximum number of requests to return.
        
        Returns:
            list: List of request dictionaries.
        """
        requests = self.db.get_requests(user_id=self.user_id, limit=limit)
        return [req.to_dict() for req in requests]
    
    def get_transaction_history(self, limit: int = 10) -> list:
        """
        Get transaction history from database.
        Получить историю транзакций из БД.
        
        Args:
            limit: Maximum number of transactions to return.
        
        Returns:
            list: List of transaction dictionaries.
        """
        transactions = self.db.get_transactions(user_id=self.user_id, limit=limit)
        return [trans.to_dict() for trans in transactions]
    
    def get_database_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics from database.
        Получить полную аналитику из БД.
        
        Returns:
            dict: Analytics data.
        """
        return {
            'total_requests': self.db.get_request_count(self.user_id),
            'total_cost': self.db.get_total_cost(self.user_id),
            'provider_stats': self.db.get_provider_stats(self.user_id),
            'recent_requests': [r.to_dict() for r in self.db.get_requests(self.user_id, limit=5)],
            'recent_transactions': [t.to_dict() for t in self.db.get_transactions(self.user_id, limit=5)]
        }


def run_interactive_mode_with_db():
    """
    Run OneFlow.AI in interactive mode with database.
    Запустить OneFlow.AI в интерактивном режиме с БД.
    """
    print("=" * 60)
    print("Welcome to OneFlow.AI with Database | Добро пожаловать")
    print("=" * 60)
    
    # Ask about API mode
    use_real = input("\nUse real API providers? (y/n) [n]: ").strip().lower() == 'y'
    
    if use_real:
        print("\n⚠ Real API mode requires API keys configured in .api_keys.json")
        confirm = input("   Continue with real API? (y/n) [y]: ").strip().lower()
        if confirm == 'n':
            use_real = False
    
    # Initialize system
    system = OneFlowAIWithDB(initial_balance=100, use_real_api=use_real)
    
    # Optional: Setup budgets
    setup_budgets = input("\nSetup budget limits? (y/n) [n]: ").strip().lower()
    if setup_budgets == 'y':
        try:
            daily = input("Daily limit (press Enter to skip): ").strip()
            if daily:
                system.budget.set_limit(BudgetPeriod.DAILY, float(daily))
            
            weekly = input("Weekly limit (press Enter to skip): ").strip()
            if weekly:
                system.budget.set_limit(BudgetPeriod.WEEKLY, float(weekly))
            
            print("\n✓ Budget limits configured")
        except ValueError:
            print("✗ Invalid input, skipping budget setup")
    
    print("\n" + system.get_status())
    print("\nAvailable models: gpt, image, audio, video")
    print("Commands: request, status, analytics, history, budget, add-credits, quit")
    
    while True:
        print("\n" + "-" * 60)
        command = input("\nEnter command: ").strip().lower()
        
        if command == 'quit':
            print("\n" + system.analytics.get_summary_report())
            print("\n✓ Data saved to database")
            print("\nThank you for using OneFlow.AI!")
            break
        
        elif command == 'status':
            print(system.get_status())
        
        elif command == 'analytics':
            print(system.analytics.get_summary_report())
            print("\nDatabase Analytics:")
            db_analytics = system.get_database_analytics()
            print(f"  Total requests in DB: {db_analytics['total_requests']}")
            print(f"  Total cost in DB: {db_analytics['total_cost']:.2f} credits")
        
        elif command == 'history':
            print("\nRequest History (last 10):")
            history = system.get_request_history(limit=10)
            for i, req in enumerate(history, 1):
                print(f"  {i}. [{req['provider']}] {req['prompt'][:40]}... - {req['status']} ({req['cost']:.2f} credits)")
            
            print("\nTransaction History (last 10):")
            transactions = system.get_transaction_history(limit=10)
            for i, trans in enumerate(transactions, 1):
                print(f"  {i}. {trans['type']}: {trans['amount']:.2f} credits - {trans['description']}")
        
        elif command == 'budget':
            print(system.budget.get_budget_summary())
        
        elif command == 'add-credits':
            try:
                amount = float(input("Amount to add: ").strip())
                result = system.add_credits(amount)
                print(f"✓ Added {amount:.2f} credits")
                print(f"  New balance: {result['balance']:.2f} credits")
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
                print(f"✓ Request ID: {result['request_id']}")
            else:
                print(f"\n✗ Error: {result['message']}")
                print(f"✗ Balance: {result['balance']:.2f} credits")
        
        else:
            print("Unknown command. Available: request, status, analytics, history, budget, add-credits, quit")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        print("Demo mode with database not yet implemented.")
        print("Use interactive mode instead: python -m src.main_with_db")
    else:
        run_interactive_mode_with_db()
