"""
OneFlow.AI Main Module with Database Integration.
Главный модуль OneFlow.AI с интеграцией базы данных.
"""

from typing import Optional, Dict, Any, List
from database import get_db_manager
from wallet import Wallet
from pricing import PricingCalculator
from router import Router
from analytics import Analytics
from budget import Budget, BudgetPeriod
from providers.gpt_provider import GPTProvider
from providers.image_provider import ImageProvider
from providers.audio_provider import AudioProvider
from providers.video_provider import VideoProvider


class OneFlowAIWithDB:
    """
    OneFlow.AI orchestrator with database persistence.
    Оркестратор OneFlow.AI с персистентностью в базе данных.
    """
    
    def __init__(
        self,
        initial_balance: float = 100,
        user_id: Optional[int] = None,
        use_real_api: bool = False,
        database_url: str = 'sqlite:///data/oneflow.db'
    ):
        """
        Initialize OneFlow.AI with database.
        
        Args:
            initial_balance: Initial wallet balance.
            user_id: User ID (None for default user).
            use_real_api: Whether to use real APIs.
            database_url: Database connection URL.
        """
        # Initialize database
        self.db = get_db_manager(database_url)
        
        # Get or create user
        if user_id:
            self.user = self.db.get_user(user_id)
            if not self.user:
                raise ValueError(f"User {user_id} not found")
        else:
            # Use default user or create one
            self.user = self.db.get_user(1)
            if not self.user:
                self.user = self.db.create_user(
                    username='default',
                    email='default@oneflow.ai',
                    initial_balance=initial_balance
                )
        
        # Initialize core components
        self.wallet = Wallet(initial_balance=self.user.balance)
        self.pricing = PricingCalculator()
        self.router = Router()
        self.analytics = Analytics()
        self.budget = Budget()
        self.use_real_api = use_real_api
        
        # Setup
        self._setup_pricing()
        self._setup_providers()
    
    def _setup_pricing(self):
        """Setup pricing rates."""
        rates = {
            'gpt': 1.0,
            'image': 10.0,
            'audio': 5.0,
            'video': 20.0
        }
        for provider, rate in rates.items():
            self.pricing.register_rate(provider, rate)
            # Save to database
            self.db.create_or_update_provider(provider, rate)
    
    def _setup_providers(self):
        """Setup providers."""
        if self.use_real_api:
            try:
                from real_api_integration import create_provider
                for provider_type in ['gpt', 'image', 'audio', 'video']:
                    provider = create_provider(provider_type, use_real_api=True)
                    self.router.register_provider(provider)
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
    
    def process_request(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process AI request with database logging.
        
        Args:
            model: Model type.
            prompt: Input prompt.
            **kwargs: Additional parameters.
        
        Returns:
            dict: Result with status, response, cost, and request_id.
        """
        model_lower = model.lower()
        
        # Calculate cost
        if model_lower == 'gpt':
            cost_units = len(prompt.split())
        else:
            cost_units = 1
        
        cost = self.pricing.estimate_cost(model_lower, cost_units)
        
        # Check budget
        can_spend, reason = self.budget.can_spend(cost, provider=model_lower)
        if not can_spend:
            return {
                'status': 'error',
                'message': f'Budget limit: {reason}',
                'balance': self.wallet.get_balance()
            }
        
        # Check wallet
        if not self.wallet.can_afford(cost):
            return {
                'status': 'error',
                'message': 'Insufficient funds',
                'balance': self.wallet.get_balance()
            }
        
        # Process request
        request_obj = {'type': model_lower, 'prompt': prompt}
        response = self.router.route_request(request_obj)
        
        # Deduct cost
        balance_before = self.wallet.get_balance()
        self.wallet.deduct(cost)
        balance_after = self.wallet.get_balance()
        
        # Update user balance in database
        self.db.update_user_balance(self.user.id, balance_after)
        
        # Record spending
        self.budget.record_spending(cost, provider=model_lower)
        
        # Log to analytics
        self.analytics.log_request(
            model_lower,
            cost,
            prompt,
            status='success',
            response=str(response)
        )
        
        # Save to database
        db_request = self.db.create_request(
            user_id=self.user.id,
            provider=model_lower,
            model=model_lower,
            prompt=prompt,
            response=str(response),
            cost=cost,
            status='success'
        )
        
        # Create transaction record
        self.db.create_transaction(
            user_id=self.user.id,
            trans_type='deduct',
            amount=cost,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f'Request to {model_lower}',
            request_id=db_request.id
        )
        
        return {
            'status': 'success',
            'response': response,
            'cost': cost,
            'balance': balance_after,
            'request_id': db_request.id
        }
    
    def add_credits(self, amount: float, description: str = 'Credit top-up') -> Dict[str, Any]:
        """Add credits with database logging."""
        balance_before = self.wallet.get_balance()
        self.wallet.add_credits(amount)
        balance_after = self.wallet.get_balance()
        
        # Update database
        self.db.update_user_balance(self.user.id, balance_after)
        
        # Create transaction
        self.db.create_transaction(
            user_id=self.user.id,
            trans_type='add',
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description
        )
        
        return {
            'status': 'success',
            'balance': balance_after,
            'added': amount
        }
    
    def get_request_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get request history from database."""
        requests = self.db.get_requests(user_id=self.user.id, limit=limit)
        return [req.to_dict() for req in requests]
    
    def get_transaction_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get transaction history from database."""
        transactions = self.db.get_transactions(user_id=self.user.id, limit=limit)
        return [trans.to_dict() for trans in transactions]
    
    def get_database_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics from database."""
        return {
            'total_requests': self.db.get_request_count(user_id=self.user.id),
            'total_cost': self.db.get_total_cost(user_id=self.user.id),
            'provider_stats': self.db.get_provider_stats(user_id=self.user.id),
            'recent_requests': self.get_request_history(limit=10),
            'recent_transactions': self.get_transaction_history(limit=10)
        }
    
    def setup_budget(self, **limits):
        """Setup budget limits."""
        for period_name, amount in limits.items():
            if amount is not None:
                period = BudgetPeriod[period_name.upper()]
                self.budget.set_limit(period, amount)
    
    def setup_provider_budget(self, provider: str, amount: float):
        """Setup provider budget."""
        self.budget.set_provider
