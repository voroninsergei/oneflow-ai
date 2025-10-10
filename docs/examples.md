# OneFlow.AI Examples | Примеры использования

This document provides comprehensive examples for using OneFlow.AI.

Этот документ содержит исчерпывающие примеры использования OneFlow.AI.

---

## Table of Contents | Содержание

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Usage](#advanced-usage)
4. [CLI Examples](#cli-examples)
5. [Configuration Examples](#configuration-examples)
6. [Integration Examples](#integration-examples)

---

## Quick Start

### Simplest Example | Простейший пример

```python
from src.main import OneFlowAI

# Initialize with default settings
system = OneFlowAI()

# Make a request
result = system.process_request('gpt', 'Hello, world!')

if result['status'] == 'success':
    print(f"Response: {result['response']}")
    print(f"Cost: {result['cost']} credits")
```

---

## Basic Usage

### Example 1: Text Generation | Генерация текста

```python
from src.main import OneFlowAI

# Create system with initial balance
system = OneFlowAI(initial_balance=100)

# Process GPT request
result = system.process_request('gpt', 'Write a haiku about programming')

print(result)
# Output:
# {
#   'status': 'success',
#   'response': {...},
#   'cost': 6.0,  # 6 words in prompt
#   'balance': 94.0
# }
```

**Русский**:
```python
# Создать систему с начальным балансом
система = OneFlowAI(initial_balance=100)

# Обработать запрос к GPT
результат = система.process_request('gpt', 'Напиши хокку о программировании')
```

### Example 2: Image Generation | Генерация изображений

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=50)

# Generate image
result = system.process_request('image', 'A beautiful sunset over mountains')

if result['status'] == 'success':
    print(f"Image generated!")
    print(f"Cost: {result['cost']} credits")  # 10 credits for image
    print(f"Remaining: {result['balance']} credits")
else:
    print(f"Error: {result['message']}")
```

### Example 3: Multiple Requests | Множественные запросы

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=100)

requests = [
    ('gpt', 'Hello world'),
    ('image', 'Beautiful landscape'),
    ('audio', 'Relaxing music'),
    ('video', 'Cat playing')
]

for model, prompt in requests:
    result = system.process_request(model, prompt)
    print(f"{model}: {result['status']} - Cost: {result.get('cost', 0)}")

# Check final status
print(system.get_status())
```

---

## Advanced Usage

### Example 4: Budget Management | Управление бюджетом

```python
from src.main import OneFlowAI
from budget import BudgetPeriod

system = OneFlowAI(initial_balance=1000)

# Set daily budget limit
system.setup_budget(daily=50, weekly=300, monthly=1000)

# Set per-provider limits
system.setup_provider_budget('video', 100)
system.setup_provider_budget('image', 200)

# Make requests
requests = [
    ('gpt', 'Short text'),      # 2 credits
    ('image', 'Picture 1'),      # 10 credits
    ('video', 'Video 1'),        # 20 credits
    ('video', 'Video 2'),        # 20 credits
    ('image', 'Picture 2'),      # 10 credits
]

for model, prompt in requests:
    result = system.process_request(model, prompt)
    
    if result['status'] == 'success':
        print(f"✓ {model}: {result['cost']} credits")
    else:
        print(f"✗ {model}: {result['message']}")

# View budget status
print("\n" + system.budget.get_budget_summary())
```

**Output** | **Вывод**:
```
✓ gpt: 2.0 credits
✓ image: 10.0 credits
✓ video: 20.0 credits
✓ video: 20.0 credits
✓ image: 10.0 credits

Budget Summary | Сводка по бюджету
==========================================================
Period Limits | Лимиты по периодам:
  Daily:
    Limit: 50.00 credits
    Spent: 62.00 credits (124.0%)
    Remaining: 0.00 credits
```

### Example 5: Analytics Tracking | Отслеживание аналитики

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=200)

# Make various requests
models = ['gpt', 'image', 'gpt', 'audio', 'gpt', 'video']
for i, model in enumerate(models):
    result = system.process_request(model, f'Request {i+1}')

# Get analytics summary
print(system.analytics.get_summary_report())

# Get specific statistics
print(f"\nTotal requests: {system.analytics.get_request_count()}")
print(f"Total cost: {system.analytics.get_total_cost()}")
print(f"Average cost: {system.analytics.get_average_cost_per_request():.2f}")
print(f"Most used provider: {system.analytics.get_most_used_provider()}")
print(f"Most expensive provider: {system.analytics.get_most_expensive_provider()}")

# Get recent requests
recent = system.analytics.get_recent_requests(limit=3)
print("\nLast 3 requests:")
for req in recent:
    print(f"  - {req['provider']}: {req['prompt']} ({req['cost']} credits)")
```

### Example 6: Export Analytics | Экспорт аналитики

```python
import json
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=100)

# Make some requests
for i in range(5):
    system.process_request('gpt', f'Request number {i+1}')

# Export analytics to JSON
analytics_data = system.analytics.export_to_dict()

with open('analytics_export.json', 'w', encoding='utf-8') as f:
    json.dump(analytics_data, f, indent=2, ensure_ascii=False)

print("Analytics exported to analytics_export.json")

# Load and analyze
with open('analytics_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f"Loaded {data['total_requests']} requests")
    print(f"Total cost: {data['total_cost']} credits")
```

### Example 7: Configuration-Driven Setup | Настройка через конфигурацию

```python
from config import Config
from src.main import OneFlowAI

# Create custom configuration
config = Config()
config.set_wallet_balance(500)
config.set_rate('gpt', 0.5)  # Half price!
config.set_rate('image', 5.0)
config.set_budget_limit('daily', 100)
config.set_provider_budget('video', 50)

# Save configuration
config.save_to_file('my_config.json')

# Load and use
loaded_config = Config('my_config.json')
print(loaded_config.get_config_summary())

# Apply to system (manual application needed in v2.0)
system = OneFlowAI(initial_balance=loaded_config.wallet_balance)
```

---

## CLI Examples

### Example 8: Command Line Usage | Использование командной строки

```bash
# Make a request
python -m src.cli request gpt "Hello, world!"

# Check system status
python -m src.cli status

# View analytics
python -m src.cli analytics

# View detailed analytics
python -m src.cli analytics --detailed

# Export analytics to file
python -m src.cli analytics --export analytics.json

# View budget information
python -m src.cli budget

# Add credits
python -m src.cli add-credits 50

# Set budget limits
python -m src.cli set-budget daily 100
python -m src.cli set-budget weekly 500

# View configuration
python -m src.cli config

# Use custom config file
python -m src.cli --config my_config.json status

# Verbose mode
python -m src.cli -v request gpt "Tell me a joke"
```

### Example 9: Batch Processing with CLI | Пакетная обработка через CLI

```bash
#!/bin/bash
# batch_requests.sh

# Process multiple requests
echo "Processing batch requests..."

python -m src.cli request gpt "Translate 'hello' to Spanish"
python -m src.cli request gpt "What is 2+2?"
python -m src.cli request image "A red apple"
python -m src.cli request audio "Piano music"

# Check final status
python -m src.cli status
python -m src.cli analytics
```

---

## Configuration Examples

### Example 10: Development Configuration | Конфигурация для разработки

**config.dev.json**:
```json
{
  "rates": {
    "gpt": 0.1,
    "image": 1.0,
    "audio": 0.5,
    "video": 2.0
  },
  "wallet_balance": 1000.0,
  "budget_limits": {
    "daily": null,
    "weekly": null,
    "monthly": null,
    "total": null
  },
  "provider_budgets": {
    "gpt": null,
    "image": null,
    "audio": null,
    "video": null
  },
  "region": "US"
}
```

### Example 11: Production Configuration | Конфигурация для продакшена

**config.prod.json**:
```json
{
  "rates": {
    "gpt": 1.0,
    "image": 10.0,
    "audio": 5.0,
    "video": 20.0
  },
  "wallet_balance": 100.0,
  "budget_limits": {
    "daily": 50.0,
    "weekly": 300.0,
    "monthly": 1000.0,
    "total": 5000.0
  },
  "provider_budgets": {
    "gpt": 500.0,
    "image": 1000.0,
    "audio": 750.0,
    "video": 1500.0
  },
  "region": "US"
}
```

### Example 12: Testing Configuration | Конфигурация для тестов

**config.test.json**:
```json
{
  "rates": {
    "gpt": 1.0,
    "image": 1.0,
    "audio": 1.0,
    "video": 1.0
  },
  "wallet_balance": 100.0,
  "budget_limits": {
    "daily": 10.0,
    "weekly": null,
    "monthly": null,
    "total": null
  },
  "provider_budgets": {
    "gpt": 5.0,
    "image": 5.0,
    "audio": 5.0,
    "video": 5.0
  },
  "region": "US"
}
```

---

## Integration Examples

### Example 13: Web Application Integration | Интеграция с веб-приложением

```python
from flask import Flask, request, jsonify
from src.main import OneFlowAI

app = Flask(__name__)
system = OneFlowAI(initial_balance=1000)

@app.route('/api/request', methods=['POST'])
def make_request():
    """Handle AI request from web client."""
    data = request.json
    model = data.get('model')
    prompt = data.get('prompt')
    
    if not model or not prompt:
        return jsonify({'error': 'Missing model or prompt'}), 400
    
    result = system.process_request(model, prompt)
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    return jsonify({
        'balance': system.wallet.get_balance(),
        'total_requests': system.analytics.get_request_count(),
        'total_cost': system.analytics.get_total_cost()
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data."""
    return jsonify(system.analytics.export_to_dict())

if __name__ == '__main__':
    app.run(debug=True)
```

### Example 14: Async Processing | Асинхронная обработка

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.main import OneFlowAI

async def process_request_async(system, model, prompt):
    """Process request asynchronously."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor, 
            system.process_request, 
            model, 
            prompt
        )
    return result

async def main():
    system = OneFlowAI(initial_balance=500)
    
    # Process multiple requests concurrently
    tasks = [
        process_request_async(system, 'gpt', f'Request {i}')
        for i in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"Request {i}: {result['status']}")
    
    print(system.get_status())

if __name__ == '__main__':
    asyncio.run(main())
```

### Example 15: Custom Provider | Пользовательский провайдер

```python
from src.providers.base_provider import BaseProvider
from src.main import OneFlowAI

class CustomProvider(BaseProvider):
    """Custom provider implementation."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __call__(self, prompt: str, **kwargs):
        # Your custom logic here
        response = f"Custom processing: {prompt}"
        return {
            'provider': self.name,
            'response': response,
            'custom_field': 'value'
        }

# Use custom provider
system = OneFlowAI(initial_balance=100)
custom_provider = CustomProvider(name='custom')
system.router.register_provider(custom_provider)
system.pricing.register_rate('custom', 2.5)

# Make request
result = system.process_request('custom', 'Test prompt')
print(result)
```

---

## Best Practices | Лучшие практики

### Error Handling | Обработка ошибок

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=10)

def safe_request(model, prompt):
    """Make request with error handling."""
    try:
        result = system.process_request(model, prompt)
        
        if result['status'] == 'success':
            return result['response']
        else:
            print(f"Request failed: {result['message']}")
            return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Use
response = safe_request('gpt', 'Hello world')
if response:
    print(f"Got response: {response}")
```

### Context Manager Pattern | Паттерн контекстного менеджера

```python
class OneFlowContext:
    """Context manager for OneFlow.AI."""
    
    def __init__(self, balance=100):
        self.system = None
        self.balance = balance
    
    def __enter__(self):
        self.system = OneFlowAI(initial_balance=self.balance)
        return self.system
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup or final report
        if self.system:
            print(self.system.analytics.get_summary_report())
        return False

# Usage
with OneFlowContext(balance=200) as system:
    system.process_request('gpt', 'Hello')
    system.process_request('image', 'Sunset')
# Automatically prints analytics on exit
```

---

**For more examples, see the test files in `tests/` directory.**

**Для большего количества примеров см. тестовые файлы в директории `tests/`.**
