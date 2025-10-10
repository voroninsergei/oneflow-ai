class OneFlowAI:
    """
    Main orchestrator class for OneFlow.AI.
    Главный класс-оркестратор для OneFlow.AI.
    """
    
    def __init__(self, initial_balance: float = 100, use_real_api: bool = False):
        """
        Initialize OneFlow.AI system.
        
        Args:
            initial_balance: Initial wallet balance.
            use_real_api: Whether to use real API providers.
        """
        self.wallet = Wallet(initial_balance=initial_balance)
        self.pricing = PricingCalculator()
        self.router = Router()
        self.use_real_api = use_real_api
        
        # Import analytics and budget if available
        try:
            from analytics import Analytics
            from budget import Budget
            from config import Config
            self.analytics = Analytics()
            self.budget = Budget()
            self.config = Config()
        except ImportError:
            self.analytics = None
            self.budget = None
            self.config = None
        
        self._setup_pricing()
        self._setup_providers()
    
    def _setup_pricing(self):
        """Setup default pricing rates."""
        self.pricing.register_rate('gpt', 1.0)
        self.pricing.register_rate('image', 10.0)
        self.pricing.register_rate('audio', 5.0)
        self.pricing.register_rate('video', 20.0)
    
    def _setup_providers(self):
        """Setup providers based on API mode."""
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
    
    def process_request(self, model: str, prompt: str, **kwargs):
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
        
        # Check budget if available
        if self.budget:
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
        self.wallet.deduct(cost)
        request = {'type': model_lower, 'prompt': prompt}
        response = self.router.route_request(request)
        
        # Record spending
        if self.budget:
            self.budget.record_spending(cost, provider=model_lower)
        
        # Log analytics
        if self.analytics:
            self.analytics.log_request(
                model_lower, cost, prompt,
                status='success',
                response=str(response)
            )
        
        return {
            'status': 'success',
            'response': response,
            'cost': cost,
            'balance': self.wallet.get_balance()
        }
    
    def setup_budget(self, **limits):
        """Setup budget limits."""
        if not self.budget:
            return
        
        from budget import BudgetPeriod
        for period_name, amount in limits.items():
            if amount is not None:
                period = BudgetPeriod[period_name.upper()]
                self.budget.set_limit(period, amount)
    
    def setup_provider_budget(self, provider: str, amount: float):
        """Setup provider budget."""
        if self.budget:
            self.budget.set_provider_limit(provider, amount)
    
    def get_status(self) -> str:
        """Get system status."""
        lines = ["=" * 60]
        lines.append("OneFlow.AI Status | Статус OneFlow.AI")
        lines.append("=" * 60)
        lines.append(f"\nAPI Mode: {'Real' if self.use_real_api else 'Mock (Demo)'}")
        lines.append(f"Balance: {self.wallet.get_balance():.2f} credits")
        
        if self.analytics:
            lines.append(f"\nTotal Requests: {self.analytics.get_request_count()}")
            lines.append(f"Total Cost: {self.analytics.get_total_cost():.2f} credits")
            
            if self.analytics.get_request_count() > 0:
                lines.append(f"Average Cost: {self.analytics.get_average_cost_per_request():.2f} credits")
                lines.append(f"Most Used Provider: {self.analytics.get_most_used_provider()}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def run_workflow():
    """
    Run the main OneFlow.AI workflow demonstration.
    Запуск основного демонстрационного рабочего процесса OneFlow.AI.
    """
    system = OneFlowAI(initial_balance=100)
    
    # Prompt user for input
    model = input("Enter model type (gpt, image, audio, or video): ")
    prompt = input("Enter your prompt: ")
    
    # Process request
    result = system.process_request(model, prompt)
    
    if result['status'] == 'success':
        print(f"\nResponse from {model}: {result['response']}")
        print(f"Cost: {result['cost']} credits")
        print(f"Remaining balance: {result['balance']} credits")
    else:
        print(f"\nError: {result['message']}")
        print(f"Balance: {result['balance']} credits")
