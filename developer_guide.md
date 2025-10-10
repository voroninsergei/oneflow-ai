# OneFlow.AI Developer Guide

## Руководство разработчика OneFlow.AI

This guide provides detailed information for developers working with or extending OneFlow.AI.

Это руководство предоставляет подробную информацию для разработчиков, работающих с OneFlow.AI или расширяющих его.

---

## Table of Contents | Содержание

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Adding New Providers](#adding-new-providers)
4. [Configuration System](#configuration-system)
5. [Testing Guidelines](#testing-guidelines)
6. [Best Practices](#best-practices)
7. [API Reference](#api-reference)

---

## Architecture Overview

OneFlow.AI follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│           User Interface Layer              │
│  (CLI, Interactive Mode, API)               │
└──────────────┬──────────────────────────────┘
               │
┌──────────────┴──────────────────────────────┐
│         Orchestration Layer                 │
│  (OneFlowAI - main.py)                      │
└──┬────┬────┬────┬────┬────┬─────────────────┘
   │    │    │    │    │    │
   ▼    ▼    ▼    ▼    ▼    ▼
┌──────────────────────────────────────────────┐
│          Core Services Layer                 │
│  ┌────────┐ ┌────────┐ ┌────────┐           │
│  │ Router │ │Pricing │ │ Wallet │           │
│  └────────┘ └────────┘ └────────┘           │
│  ┌────────┐ ┌────────┐                      │
│  │Analytics│ │ Budget │                      │
│  └────────┘ └────────┘                      │
└──────────────┬───────────────────────────────┘
               │
┌──────────────┴───────────────────────────────┐
│         Provider Layer                       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ GPT  │ │Image │ │Audio │ │Video │       │
│  └──────┘ └──────┘ └──────┘ └──────┘       │
└──────────────────────────────────────────────┘
```

### Key Design Principles | Ключевые принципы проектирования

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Extensibility**: Easy to add new providers and features
3. **Testability**: All components are independently testable
4. **Configuration-driven**: Behavior controlled through configuration
5. **Multilingual**: Full English and Russian support

---

## Core Components

### 1. Router (`router.py`)

**Purpose**: Select the appropriate provider based on request type.

**Русский**: Выбрать подходящего провайдера на основе типа запроса.

```python
from router import Router
from providers import GPTProvider

router = Router()
router.register_provider(GPTProvider(name='gpt'))

request = {'type': 'gpt', 'prompt': 'Hello'}
response = router.route_request(request)
```

**Key Methods**:
- `register_provider(provider)`: Register a new provider
- `route_request(request)`: Route request to appropriate provider

### 2. Pricing Calculator (`pricing.py`)

**Purpose**: Calculate costs for AI operations.

**Русский**: Рассчитать стоимость операций AI.

```python
from pricing import PricingCalculator

pricing = PricingCalculator()
pricing.register_rate('gpt', 1.0)  # 1 credit per word

cost = pricing.estimate_cost('gpt', 100)  # 100 words
print(f"Cost: {cost} credits")
```

**Key Methods**:
- `register_rate(provider_name, rate)`: Set pricing rate
- `estimate_cost(provider_name, units)`: Calculate cost
- `has_provider(provider_name)`: Check if provider exists
- `get_all_rates()`: Get all registered rates

### 3. Wallet (`wallet.py`)

**Purpose**: Manage user credits and balance.

**Русский**: Управлять кредитами и балансом пользователя.

```python
from wallet import Wallet

wallet = Wallet(initial_balance=100)
wallet.add_credits(50)

if wallet.can_afford(25):
    wallet.deduct(25)
    print(f"Remaining: {wallet.get_balance()}")
```

**Key Methods**:
- `add_credits(amount)`: Add credits
- `deduct(cost)`: Deduct credits
- `get_balance()`: Get current balance
- `can_afford(cost)`: Check if sufficient funds

### 4. Analytics (`analytics.py`)

**Purpose**: Track and analyze usage patterns.

**Русский**: Отслеживать и анализировать паттерны использования.

```python
from analytics import Analytics

analytics = Analytics()
analytics.log_request('gpt', 5.0, 'prompt', status='success')

print(f"Total cost: {analytics.get_total_cost()}")
print(f"Most used: {analytics.get_most_used_provider()}")
print(analytics.get_summary_report())
```

**Key Methods**:
- `log_request(provider, cost, prompt, status, response)`: Log a request
- `get_total_cost()`: Get cumulative cost
- `get_request_count()`: Get number of requests
- `get_provider_stats()`: Get provider statistics
- `get_summary_report()`: Generate report

### 5. Budget (`budget.py`)

**Purpose**: Enforce spending limits and budget controls.

**Русский**: Обеспечить лимиты расходов и контроль бюджета.

```python
from budget import Budget, BudgetPeriod

budget = Budget()
budget.set_limit(BudgetPeriod.DAILY, 100.0)
budget.set_provider_limit('gpt', 50.0)

can_spend, reason = budget.can_spend(10.0, provider='gpt')
if can_spend:
    budget.record_spending(10.0, provider='gpt')
```

**Key Methods**:
- `set_limit(period, amount)`: Set period limit
- `set_provider_limit(provider, amount)`: Set provider limit
- `can_spend(amount, provider)`: Check if within budget
- `record_spending(amount, provider)`: Record spending
- `get_remaining(period)`: Get remaining budget

### 6. Configuration (`config.py`)

**Purpose**: Centralized configuration management.

**Русский**: Централизованное управление конфигурацией.

```python
from config import Config

config = Config('config.json')
config.set_rate('gpt', 2.0)
config.set_wallet_balance(200.0)
config.save_to_file('updated_config.json')
```

---

## Adding New Providers

To add a new AI provider:

### Step 1: Create Provider Class

Create a new file in `src/providers/`:

```python
# src/providers/my_provider.py

from .base_provider import BaseProvider

class MyProvider(BaseProvider):
    """
    Custom provider implementation.
    Реализация пользовательского провайдера.
    """
    
    def __init__(self, name: str):
        self.name = name
    
    def __call__(self, prompt: str, **kwargs):
        """
        Process the request and return response.
        Обработать запрос и вернуть ответ.
        """
        # Your implementation here
        response = f"Processed by {self.name}: {prompt}"
        return {"provider": self.name, "response": response}
```

### Step 2: Register in __init__.py

Add to `src/providers/__init__.py`:

```python
from .my_provider import MyProvider

__all__ = [
    "BaseProvider",
    "GPTProvider",
    "ImageProvider",
    "AudioProvider",
    "VideoProvider",
    "MyProvider",  # Add your provider
]
```

### Step 3: Configure Pricing

Add pricing rate in configuration:

```python
pricing.register_rate('myprovider', 3.0)  # 3 credits per unit
```

### Step 4: Register with Router

```python
from providers import MyProvider

provider = MyProvider(name='myprovider')
router.register_provider(provider)
```

### Step 5: Write Tests

Create `tests/test_my_provider.py`:

```python
def test_my_provider():
    provider = MyProvider(name='test')
    result = provider('test prompt')
    assert 'test prompt' in result
    assert result['provider'] == 'test'
```

---

## Configuration System

### Configuration File Format

JSON format with the following structure:

```json
{
  "rates": {
    "provider_name": <rate_per_unit>
  },
  "wallet_balance": <initial_balance>,
  "budget_limits": {
    "daily": <limit_or_null>,
    "weekly": <limit_or_null>,
    "monthly": <limit_or_null>,
    "total": <limit_or_null>
  },
  "provider_budgets": {
    "provider_name": <limit_or_null>
  },
  "region": "US|EU|RU"
}
```

### Loading Configuration

```python
# From file
config = Config('config.json')

# Programmatically
config = Config()
config.set_rate('gpt', 1.5)
config.set_budget_limit('daily', 100.0)
config.save_to_file('my_config.json')
```

---

## Testing Guidelines

### Running Tests

```bash
# All tests
pytest -v

# Specific module
pytest tests/test_pricing.py -v

# With coverage
pytest --cov=src tests/
```

### Writing Tests

Follow these conventions:

1. **Test file naming**: `test_<module>.py`
2. **Test function naming**: `test_<functionality>`
3. **Use descriptive docstrings** (English & Russian)
4. **Test edge cases and error conditions**
5. **Use pytest fixtures** for common setup

Example:

```python
def test_provider_with_invalid_input():
    """Test provider handles invalid input gracefully.
    
    Русский: Проверка обработки некорректного ввода провайдером.
    """
    provider = MyProvider(name='test')
    with pytest.raises(ValueError):
        provider('')  # Empty prompt should raise error
```

---

## Best Practices

### Code Style

1. **Follow PEP 8** style guidelines
2. **Use type hints** where appropriate
3. **Write bilingual docstrings** (English & Russian)
4. **Keep functions focused** (single responsibility)
5. **Use meaningful variable names**

### Error Handling

```python
# Good
try:
    result = provider(prompt)
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    return {'status': 'error', 'message': str(e)}

# Bad
try:
    result = provider(prompt)
except:
    pass
```

### Documentation

- Document all public APIs
- Include usage examples
- Provide both English and Russian versions
- Keep documentation up-to-date with code

---

## API Reference

### Complete Method Signatures

#### PricingCalculator

```python
def __init__(self)
def register_rate(self, provider_name: str, rate: float) -> None
def estimate_cost(self, provider_name: str, units: float) -> float
def get_all_rates(self) -> dict
def has_provider(self, provider_name: str) -> bool
```

#### Wallet

```python
def __init__(self, initial_balance: float = 0.0)
def add_credits(self, amount: float)
def deduct(self, cost: float) -> bool
def get_balance(self) -> float
def can_afford(self, cost: float) -> bool
```

#### Budget

```python
def __init__(self)
def set_limit(self, period: BudgetPeriod, amount: float) -> None
def set_provider_limit(self, provider: str, amount: float) -> None
def can_spend(self, amount: float, provider: Optional[str] = None) -> tuple[bool, Optional[str]]
def record_spending(self, amount: float, provider: Optional[str] = None) -> None
def get_remaining(self, period: BudgetPeriod) -> Optional[float]
def get_spent(self, period: BudgetPeriod) -> float
```

---

## Contributing

For contribution guidelines, please refer to CONTRIBUTING.md (to be created).

---

**Last Updated**: 2025-01-XX
**Version**: 1.0.0
**Author**: Sergey Voronin
