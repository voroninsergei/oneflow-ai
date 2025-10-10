# OneFlow.AI

OneFlow.AI is a comprehensive pricing and routing layer over AI models (text, image, audio, video). The platform provides upfront price quotes, smart provider selection based on quality, speed, cost and region, automatic fallbacks for reliability, and a unified wallet with budgets and analytics.

**OneFlow.AI (русская версия)**

OneFlow.AI — полнофункциональный слой ценообразования и умной маршрутизации поверх AI моделей (текст, изображения, аудио, видео). Платформа предоставляет предварительные котировки стоимости, умный выбор провайдера по качеству, скорости, цене и региону, автоматические фолбэки для надёжности, а также единый кошелёк с бюджетами и аналитикой.

## Features | Возможности

### Core Features | Основные возможности
- **Multi-modal AI Support** - Text (GPT), Image, Audio, and Video generation
- **Smart Routing** - Automatic provider selection based on request type
- **Pricing Calculator** - Transparent cost estimation before requests
- **Wallet System** - Unified credit management across all providers
- **Budget Controls** - Set daily, weekly, monthly, and per-provider limits
- **Analytics Dashboard** - Track usage patterns and spending
- **Multi-region Support** - US/EU/RU regions
- **Multilingual** - Full English & Russian documentation

### New Features | Новые возможности
- **Analytics Module** (`analytics.py`) - Comprehensive usage tracking and reporting
- **Budget Management** (`budget.py`) - Advanced spending controls with period-based limits
- **Enhanced Main** - Interactive and demo modes with full system integration
- **Improved Error Handling** - Validation and informative error messages
- **Summary Reports** - Detailed analytics and budget reports

## Installation | Установка

```bash
# Clone the repository
git clone <repository-url>
cd OneFlow.AI

# Install dependencies
pip install -r requirements.txt
```

## Usage | Использование

### Interactive Mode | Интерактивный режим

Run the main application in interactive mode:

```bash
python -m src.main
```

This starts an interactive session where you can:
- Make AI requests to different providers
- View system status and balance
- Check analytics reports
- Monitor budget usage
- Configure budget limits

**Russian / Русский:**
Запустить основное приложение в интерактивном режиме:

```bash
python -m src.main
```

### Demo Mode | Демонстрационный режим

Run a demonstration with predefined requests:

```bash
python -m src.main --demo
```

The demo showcases:
- Multiple provider requests
- Budget limit enforcement
- Cost tracking
- Analytics reporting

**Russian / Русский:**
Запустить демонстрацию с предопределенными запросами:

```bash
python -m src.main --demo
```

### Running Tests | Запуск тестов

Run the complete test suite:

```bash
pytest -v
```

Run specific test modules:

```bash
# Test pricing calculator
pytest tests/test_pricing.py -v

# Test providers
pytest tests/test_providers.py -v

# Test router
pytest tests/test_router.py -v

# Test wallet
pytest tests/test_wallet.py -v

# Test analytics
pytest tests/test_analytics.py -v

# Test budget
pytest tests/test_budget.py -v
```

## Architecture | Архитектура

```
OneFlow.AI/
├── src/
│   ├── main.py              # Main application entry point / Главная точка входа
│   ├── router.py            # Smart provider routing / Умная маршрутизация
│   ├── pricing.py           # Cost calculation / Расчет стоимости
│   ├── wallet.py            # Credit management / Управление кредитами
│   ├── analytics.py         # Usage tracking / Отслеживание использования
│   ├── budget.py            # Budget controls / Контроль бюджета
│   └── providers/           # Provider implementations / Реализации провайдеров
│       ├── base_provider.py
│       ├── gpt_provider.py
│       ├── image_provider.py
│       ├── audio_provider.py
│       └── video_provider.py
├── tests/                   # Test suite / Набор тестов
│   ├── test_pricing.py
│   ├── test_providers.py
│   ├── test_router.py
│   ├── test_wallet.py
│   ├── test_analytics.py
│   └── test_budget.py
├── requirements.txt
├── LICENSE
└── README.md
```

## API Reference | Справочник API

### PricingCalculator

```python
from pricing import PricingCalculator

pricing = PricingCalculator()
pricing.register_rate('gpt', 1.0)  # 1 credit per word
cost = pricing.estimate_cost('gpt', 100)  # Estimate for 100 words
```

### Wallet

```python
from wallet import Wallet

wallet = Wallet(initial_balance=100)
wallet.add_credits(50)
wallet.deduct(25)
balance = wallet.get_balance()
can_afford = wallet.can_afford(30)
```

### Budget

```python
from budget import Budget, BudgetPeriod

budget = Budget()
budget.set_limit(BudgetPeriod.DAILY, 50.0)
budget.set_provider_limit('gpt', 30.0)

can_spend, reason = budget.can_spend(10.0, provider='gpt')
if can_spend:
    budget.record_spending(10.0, provider='gpt')
```

### Analytics

```python
from analytics import Analytics

analytics = Analytics()
analytics.log_request('gpt', 5.0, 'prompt', status='success')
total_cost = analytics.get_total_cost()
report = analytics.get_summary_report()
```

### Router

```python
from router import Router
from providers import GPTProvider

router = Router()
router.register_provider(GPTProvider(name='gpt'))

request = {'type': 'gpt', 'prompt': 'Hello world'}
response = router.route_request(request)
```

## Examples | Примеры

### Basic Request Example

```python
from src.main import OneFlowAI

# Initialize system
system = OneFlowAI(initial_balance=100)

# Setup budget
system.setup_budget(daily=50)
system.setup_provider_budget('video', 30)

# Process request
result = system.process_request('gpt', 'Hello world')
if result['status'] == 'success':
    print(f"Response: {result['response']}")
    print(f"Cost: {result['cost']}")
    print(f"Balance: {result['balance']}")
```

### Analytics Example

```python
# Get usage statistics
analytics_report = system.analytics.get_summary_report()
print(analytics_report)

# Get budget status
budget_summary = system.budget.get_budget_summary()
print(budget_summary)

# Get system status
status = system.get_status()
print(status)
```

## Pricing | Ценообразование

Default rates (can be customized):
- **GPT (Text)**: 1 credit per word
- **Image Generation**: 10 credits per image
- **Audio Generation**: 5 credits per audio
- **Video Generation**: 20 credits per video

**Russian / Русский:**
Стандартные тарифы (могут быть настроены):
- **GPT (Текст)**: 1 кредит за слово
- **Генерация изображений**: 10 кредитов за изображение
- **Генерация аудио**: 5 кредитов за аудио
- **Генерация видео**: 20 кредитов за видео

## Testing | Тестирование

The project includes comprehensive tests:
- Unit tests for all core modules
- Integration tests for system workflows
- Edge case and error handling tests

**Test Coverage:**
- ✅ PricingCalculator - 7 tests
- ✅ Providers - 4 tests
- ✅ Router - 2 tests
- ✅ Wallet - 2 tests
- ✅ Analytics - 12 tests
- ✅ Budget - 15 tests

## Contributing | Участие в разработке

This is a proprietary project. See LICENSE for details.

Это проприетарный проект. См. LICENSE для подробностей.

## Author | Автор

**Sergey Voronin**

Copyright (c) 2025 Sergey Voronin. All rights reserved.

## License | Лицензия

All rights reserved. See LICENSE file for details.

Все права защищены. См. файл LICENSE для подробностей.
