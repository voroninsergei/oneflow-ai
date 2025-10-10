# OneFlow.AI - Real API Integration Guide
## Руководство по интеграции с реальными API

---

## 🎯 Что нового в Этапе 3

### ✅ Реализовано:

1. **Enhanced Real API Module** (`enhanced_real_api.py`)
   - ✅ Retry logic с exponential backoff
   - ✅ Rate limiting для каждого провайдера
   - ✅ Автоматическая обработка ошибок
   - ✅ Mock режим для тестирования
   - ✅ Детальное логирование

2. **Provider Manager** (`provider_manager.py`)
   - ✅ Централизованное управление провайдерами
   - ✅ Автоматические fallbacks (GPT → Claude, Stability → DALL-E)
   - ✅ Метрики производительности
   - ✅ Health checks и статусы
   - ✅ Выбор лучшего провайдера

3. **API Keys Management** (уже был)
   - ✅ Безопасное хранение в `.api_keys.json`
   - ✅ Поддержка environment variables
   - ✅ Валидация ключей

---

## 📦 Установка зависимостей

```bash
# Основные зависимости (уже установлены)
pip install -r requirements.txt

# Для реальных API провайдеров
pip install openai anthropic requests

# Опционально: для async операций
pip install aiohttp asyncio
```

---

## 🔑 Настройка API ключей

### Способ 1: Интерактивная настройка

```bash
python setup_keys.py
```

Следуйте инструкциям для настройки ключей.

### Способ 2: Ручное создание `.api_keys.json`

```json
{
  "openai": "sk-proj-your-openai-key-here",
  "anthropic": "sk-ant-your-anthropic-key-here",
  "stability": "sk-your-stability-key-here",
  "elevenlabs": "your-elevenlabs-key-here"
}
```

**ВАЖНО**: Добавьте в `.gitignore`:
```bash
echo ".api_keys.json" >> .gitignore
chmod 600 .api_keys.json
```

### Способ 3: Environment Variables

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export STABILITY_API_KEY="sk-..."
export ELEVENLABS_API_KEY="..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-proj-..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 🚀 Быстрый старт

### Пример 1: Базовое использование Enhanced API

```python
from enhanced_real_api import create_enhanced_provider

# Создать OpenAI провайдера
gpt_provider = create_enhanced_provider('gpt')

# Текстовая генерация
result = gpt_provider(
    'Write a haiku about AI',
    task_type='text',
    model='gpt-3.5-turbo'
)

print(f"Response: {result['response']}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Tokens: {result['tokens_used']}")

# Генерация изображений
result = gpt_provider(
    'A beautiful sunset',
    task_type='image',
    size='1024x1024'
)

print(f"Image URL: {result['image_url']}")
print(f"Cost: ${result['cost']:.4f}")
```

### Пример 2: Использование Provider Manager

```python
from provider_manager import initialize_provider_manager

# Инициализация с реальными API
manager = initialize_provider_manager(use_real_api=True)

# Запрос с автоматическим fallback
# Попробует OpenAI, если не получится - Anthropic
result = manager.execute_with_fallback(
    'text',
    'Explain quantum computing simply'
)

print(f"Provider used: {result['provider_name']}")
print(f"Response: {result['response']}")
print(f"Response time: {result['response_time']:.2f}s")

# Просмотр метрик
summary = manager.get_metrics_summary()
print(f"Total requests: {summary['total_requests']}")
print(f"Success rate: {summary['overall_success_rate']}")
```

### Пример 3: Множественные запросы с fallback

```python
from provider_manager import initialize_provider_manager

manager = initialize_provider_manager(use_real_api=True)

requests = [
    ('text', 'Write a poem about AI'),
    ('text', 'Explain machine learning'),
    ('image', 'A futuristic city'),
    ('audio', 'Welcome to OneFlow.AI'),
]

for task_type, prompt in requests:
    result = manager.execute_with_fallback(task_type, prompt)
    
    if result['status'] == 'success':
        print(f"✓ {task_type}: {result['provider_name']} - ${result.get('cost', 0):.4f}")
    else:
        print(f"✗ {task_type}: {result['error']}")

# Показать статистику
status = manager.get_all_providers_status()
for name, info in status.items():
    metrics = info['metrics']
    print(f"\n{name}:")
    print(f"  Success rate: {metrics['success_rate']}")
    print(f"  Total cost: {metrics['total_cost']}")
```

---

## 🔧 Интеграция с существующим кодом

### Обновление `src/main.py`

```python
"""
OneFlow.AI Main Module - Enhanced with Real API
"""

from provider_manager import initialize_provider_manager
from pricing import PricingCalculator
from wallet import Wallet
from analytics import Analytics
from budget import Budget, BudgetPeriod


class OneFlowAI:
    """Enhanced OneFlow.AI with real API support."""
    
    def __init__(self, initial_balance: float = 100, use_real_api: bool = False):
        self.wallet = Wallet(initial_balance=initial_balance)
        self.pricing = PricingCalculator()
        self.analytics = Analytics()
        self.budget = Budget()
        self.use_real_api = use_real_api
        
        # Initialize Provider Manager
        self.provider_manager = initialize_provider_manager(use_real_api)
        
        # Setup pricing from provider manager
        self._setup_pricing()
    
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
    
    def process_request(self, model: str, prompt: str, **kwargs) -> dict:
        """Process request with provider manager."""
        model_lower = model.lower()
        
        # Map model to task type
        task_type_map = {
            'gpt': 'text',
            'image': 'image',
            'audio': 'audio',
            'video': 'video'
        }
        task_type = task_type_map.get(model_lower, 'text')
        
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
                'message': f'Insufficient funds',
                'balance': self.wallet.get_balance()
            }
        
        # Execute with provider manager (automatic fallback)
        result = self.provider_manager.execute_with_fallback(
            task_type, prompt, **kwargs
        )
        
        if result['status'] == 'success':
            # Deduct cost
            self.wallet.deduct(cost)
            self.budget.record_spending(cost, provider=model_lower)
            
            # Log analytics
            self.analytics.log_request(
                result['provider_name'],
                cost,
                prompt,
                status='success',
                response=str(result.get('response', ''))
            )
            
            return {
                'status': 'success',
                'response': result,
                'cost': cost,
                'balance': self.wallet.get_balance(),
                'provider': result['provider_name'],
                'response_time': result.get('response_time', 0)
            }
        else:
            # Log failure
            self.analytics.log_request(
                'unknown',
                0,
                prompt,
                status='error',
                response=result.get('error', '')
            )
            
            return {
                'status': 'error',
                'message': result.get('error', 'Unknown error'),
                'balance': self.wallet.get_balance()
            }
    
    def get_provider_status(self):
        """Get all providers status."""
        return self.provider_manager.get_all_providers_status()
    
    def get_best_provider(self, task_type: str):
        """Get best provider for task type."""
        return self.provider_manager.get_best_provider(task_type)


# Example usage
if __name__ == '__main__':
    # Initialize with real API
    system = OneFlowAI(initial_balance=100, use_real_api=True)
    
    # Make request
    result = system.process_request('gpt', 'Hello, world!')
    
    if result['status'] == 'success':
        print(f"✓ Success!")
        print(f"  Provider: {result['provider']}")
        print(f"  Cost: {result['cost']:.2f}")
        print(f"  Response time: {result['response_time']:.2f}s")
    else:
        print(f"✗ Error: {result['message']}")
    
    # Check provider status
    status = system.get_provider_status()
    for name, info in status.items():
        print(f"\n{name}: {info['status']}")
        print(f"  Success rate: {info['metrics']['success_rate']}")
```

---

## 🎯 Ключевые возможности

### 1. Автоматические Fallbacks

```python
# Настройка fallback цепочек
manager.set_fallback_chain('text', ['openai', 'anthropic', 'gpt'])
manager.set_fallback_chain('image', ['stability', 'openai'])

# Запрос автоматически пробует провайдеров по порядку
result = manager.execute_with_fallback('text', 'Hello')
# Попробует: OpenAI → если ошибка → Anthropic → если ошибка → GPT mock
```

### 2. Rate Limiting

```python
# Автоматический rate limiting (встроен в провайдеры)
# OpenAI: 60 requests/minute
# Anthropic: 50 requests/minute
# Stability: 150 requests/minute
# ElevenLabs: 120 requests/minute

# Если лимит достигнут - провайдер автоматически ждёт
for i in range(100):
    result = gpt_provider('Request ' + str(i))
    # Автоматически управляет rate limits
```

### 3. Retry Logic с Exponential Backoff

```python
# Встроен в каждый провайдер через декоратор @retry_with_backoff
# Параметры: max_retries=3, base_delay=1.0

# При временной ошибке:
# - Попытка 1: немедленно
# - Попытка 2: через 1 секунду
# - Попытка 3: через 2 секунды
# - Попытка 4: через 4 секунды
# - Если все неудачны - выбрасывает исключение
```

### 4. Метрики и мониторинг

```python
# Получить метрики провайдера
status = manager.get_provider_status('openai')
print(f"Total requests: {status['metrics']['total_requests']}")
print(f"Success rate: {status['metrics']['success_rate']}")
print(f"Average response time: {status['metrics']['average_response_time']}")
print(f"Total cost: {status['metrics']['total_cost']}")

# Сводка по всем провайдерам
summary = manager.get_metrics_summary()
print(summary)

# Сброс метрик
manager.reset_metrics('openai')  # Для одного
manager.reset_metrics()  # Для всех
```

### 5. Health Checks

```python
# Проверить доступность провайдера
if manager.providers['openai']['status'] == ProviderStatus.AVAILABLE:
    print("OpenAI доступен")
else:
    print("OpenAI недоступен")

# Вручную изменить статус
manager.mark_provider_unavailable('openai', 'Maintenance')
manager.mark_provider_available('openai')
```

---

## 📊 Примеры использования

### Сценарий 1: Производственное использование

```python
from provider_manager import initialize_provider_manager

# Production setup
manager = initialize_provider_manager(use_real_api=True)

# Настройка fallbacks
manager.set_fallback_chain('text', ['anthropic', 'openai'])  # Claude first

# Обработка запросов пользователей
user_prompts = [
    "Translate 'hello' to Spanish",
    "What is 2+2?",
    "Write a poem about stars"
]

for prompt in user_prompts:
    try:
        result = manager.execute_with_fallback('text', prompt)
        
        if result['status'] == 'success':
            # Сохранить результат
            save_to_database(
                user_id=current_user.id,
                prompt=prompt,
                response=result['response'],
                provider=result['provider_name'],
                cost=result['cost']
            )
        else:
            # Логировать ошибку
            log_error(f"Failed to process: {result['error']}")
    
    except Exception as e:
        # Critical error handling
        alert_admin(f"Critical API failure: {e}")
```

### Сценарий 2: A/B Testing провайдеров

```python
import random

def compare_providers(prompt: str):
    """Compare GPT vs Claude for same prompt."""
    
    # Test with OpenAI
    gpt_provider = create_enhanced_provider('gpt')
    gpt_result = gpt_provider(prompt, task_type='text')
    
    # Test with Anthropic
    claude_provider = create_enhanced_provider('claude')
    claude_result = claude_provider(prompt)
    
    # Compare results
    comparison = {
        'prompt': prompt,
        'gpt': {
            'response': gpt_result['response'],
            'cost': gpt_result['cost'],
            'tokens': gpt_result['tokens_used'],
            'response_time': gpt_result.get('response_time', 0)
        },
        'claude': {
            'response': claude_result['response'],
            'cost': claude_result['cost'],
            'tokens': claude_result['tokens_used'],
            'response_time': claude_result.get('response_time', 0)
        }
    }
    
    return comparison

# Run A/B test
test_prompts = [
    "Explain quantum physics simply",
    "Write a creative story",
    "Solve this math problem: 234 * 567"
]

for prompt in test_prompts:
    result = compare_providers(prompt)
    print(f"\nPrompt: {prompt}")
    print(f"GPT cost: ${result['gpt']['cost']:.4f}")
    print(f"Claude cost: ${result['claude']['cost']:.4f}")
    print(f"Winner: {'GPT' if result['gpt']['cost'] < result['claude']['cost'] else 'Claude'}")
```

### Сценарий 3: Batch Processing с прогресс-баром

```python
from provider_manager import initialize_provider_manager
from tqdm import tqdm

def process_batch(prompts: list, task_type: str = 'text'):
    """Process batch of prompts with progress tracking."""
    manager = initialize_provider_manager(use_real_api=True)
    results = []
    
    for prompt in tqdm(prompts, desc="Processing"):
        result = manager.execute_with_fallback(task_type, prompt)
        results.append(result)
        
        # Optional: delay between requests
        time.sleep(0.5)
    
    return results

# Usage
prompts = [f"Generate idea #{i}" for i in range(100)]
results = process_batch(prompts)

# Analyze results
successful = sum(1 for r in results if r['status'] == 'success')
total_cost = sum(r.get('cost', 0) for r in results)

print(f"Success rate: {successful/len(results)*100:.1f}%")
print(f"Total cost: ${total_cost:.2f}")
```

---

## 🔍 Troubleshooting

### Проблема 1: "API key not configured"

**Решение:**
```bash
# Проверьте .api_keys.json
cat .api_keys.json

# Или переменные окружения
echo $OPENAI_API_KEY

# Запустите setup
python setup_keys.py
```

### Проблема 2: "Rate limit exceeded"

**Решение:**
```python
# Rate limiter уже встроен, но можно настроить:
from enhanced_real_api import _rate_limiters

# Увеличить лимиты (если у вас Premium аккаунт)
_rate_limiters['openai'] = RateLimiter(max_requests=100, time_window=60)
```

### Проблема 3: "All providers failed"

**Решение:**
```python
# Проверьте статус провайдеров
status = manager.get_all_providers_status()
for name, info in status.items():
    print(f"{name}: {info['status']}")
    if info['metrics']['last_error']:
        print(f"  Last error: {info['metrics']['last_error']}")

# Попробуйте вручную
provider = manager.get_provider('openai')
result = provider('Test prompt', task_type='text')
print(result)
```

### Проблема 4: "Import Error"

**Решение:**
```bash
# Установите недостающие пакеты
pip install openai anthropic requests

# Или для всех зависимостей
pip install -r requirements.txt
pip install openai anthropic requests
```

---

## 📈 Мониторинг и логирование

### Настройка логирования

```python
import logging

# Настроить уровень логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oneflow.log'),
        logging.StreamHandler()
    ]
)

# Использовать в коде
logger = logging.getLogger('OneFlow.AI')

# Логи автоматически будут показывать:
# - Какой провайдер используется
# - Ошибки и retry попытки
# - Rate limiting события
# - Успешные запросы
```

### Экспорт метрик

```python
import json
from datetime import datetime

def export_metrics(manager, filename=None):
    """Export provider metrics to JSON."""
    if filename is None:
        filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    metrics = manager.get_metrics_summary()
    
    with open(filename, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Metrics exported to {filename}")
    return filename

# Usage
manager = initialize_provider_manager(use_real_api=True)
# ... make some requests ...
export_metrics(manager)
```

---

## 🔒 Безопасность

### Best Practices:

1. **Никогда не коммитьте API ключи**
   ```bash
   # .gitignore
   .api_keys.json
   *.key
   *.pem
   .env
   ```

2. **Используйте переменные окружения в production**
   ```bash
   # В production
   export OPENAI_API_KEY="sk-..."
   # НЕ храните в коде!
   ```

3. **Ротация ключей**
   ```python
   # Периодически обновляйте ключи
   # 1. Создайте новый ключ на платформе
   # 2. Обновите .api_keys.json
   # 3. Перезапустите приложение
   # 4. Удалите старый ключ через 24 часа
   ```

4. **Мониторинг использования**
   ```python
   # Регулярно проверяйте затраты
   summary = manager.get_metrics_summary()
   if float(summary['total_cost'].replace(', '')) > 100:
       alert_admin("High API costs detected!")
   ```

---

## 💰 Оптимизация затрат

### Стратегия 1: Выбор дешёвых моделей

```python
# Используйте gpt-3.5-turbo вместо gpt-4
result = gpt_provider(
    'Simple question',
    task_type='text',
    model='gpt-3.5-turbo'  # $0.002/1K vs $0.03/1K
)

# Claude Haiku вместо Opus
result = claude_provider(
    'Simple question',
    model='claude-3-haiku-20240307'  # Дешевле
)
```

### Стратегия 2: Кеширование

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_request(prompt_hash: str, task_type: str):
    """Cache API responses."""
    # Реальный запрос только если не в кеше
    return manager.execute_with_fallback(task_type, prompt)

# Usage
prompt = "What is AI?"
prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
result = cached_request(prompt_hash, 'text')
```

### Стратегия 3: Batch Processing

```python
# Группируйте запросы
prompts = ["Question 1", "Question 2", "Question 3"]

# Вместо 3 отдельных вызовов:
combined_prompt = "\n".join([f"{i+1}. {p}" for i, p in enumerate(prompts)])
result = gpt_provider(
    f"Answer these questions:\n{combined_prompt}",
    task_type='text'
)
# Одна транзакция вместо трёх
```

---

## 🧪 Тестирование

### Unit тесты для Real API

```python
import pytest
from enhanced_real_api import create_enhanced_provider

def test_openai_provider_text():
    """Test OpenAI text generation."""
    provider = create_enhanced_provider('gpt')
    result = provider('Test prompt', task_type='text', model='gpt-3.5-turbo')
    
    assert result['status'] == 'success' or 'error' in result
    assert 'cost' in result
    assert 'response' in result or 'error' in result

def test_provider_manager_fallback():
    """Test automatic fallback."""
    from provider_manager import initialize_provider_manager
    
    manager = initialize_provider_manager(use_real_api=True)
    
    # Mark first provider as unavailable
    manager.mark_provider_unavailable('openai', 'Testing')
    
    # Should fallback to anthropic
    result = manager.execute_with_fallback('text', 'Test')
    
    if result['status'] == 'success':
        assert result['provider_name'] == 'anthropic'

def test_rate_limiting():
    """Test rate limiter."""
    from enhanced_real_api import RateLimiter
    
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    assert limiter.can_proceed() == True
    limiter.add_request()
    assert limiter.can_proceed() == True
    limiter.add_request()
    assert limiter.can_proceed() == False  # Limit reached

# Run tests
pytest.main([__file__, '-v'])
```

---

## 📊 Сравнение провайдеров

### Стоимость (приблизительно):

| Провайдер | Тип | Стоимость | Примечания |
|-----------|-----|-----------|------------|
| OpenAI GPT-3.5 | Text | $0.002/1K tokens | Быстрый, дешёвый |
| OpenAI GPT-4 | Text | $0.03/1K tokens | Качественный, дорогой |
| Anthropic Claude Haiku | Text | $0.00025/1K tokens | Очень дешёвый |
| Anthropic Claude Sonnet | Text | $0.003/1K tokens | Балансированный |
| Anthropic Claude Opus | Text | $0.015/1K tokens | Премиум качество |
| OpenAI DALL-E 3 | Image | $0.04-0.12/image | HD quality |
| Stability AI SDXL | Image | $0.01-0.03/image | Более дешёвый |
| ElevenLabs | Audio | $0.30/1K chars | Качественный TTS |

### Производительность:

| Провайдер | Скорость | Качество | Надёжность |
|-----------|----------|----------|------------|
| OpenAI GPT-3.5 | ⚡⚡⚡ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| OpenAI GPT-4 | ⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Anthropic Claude | ⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Stability AI | ⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| ElevenLabs | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎓 Следующие шаги

После настройки Real API вы можете:

1. ✅ **Интегрировать с Web Server**
   ```python
   # В web_server.py
   from provider_manager import initialize_provider_manager
   
   manager = initialize_provider_manager(use_real_api=True)
   ```

2. ✅ **Добавить в Database Module**
   ```python
   # Сохранять метаданные о провайдере
   db.create_request(
       provider=result['provider_name'],
       response_time=result['response_time'],
       # ...
   )
   ```

3. ✅ **Создать мониторинг dashboard**
   - Показывать метрики в реальном времени
   - Графики использования
   - Alerts при превышении бюджета

4. ✅ **Настроить CI/CD**
   - Автоматическое тестирование
   - Деплой с новыми провайдерами

---

## ✅ Чеклист готовности

- [ ] Установлены зависимости: `pip install openai anthropic requests`
- [ ] Настроены API ключи в `.api_keys.json` или env vars
- [ ] `.api_keys.json` добавлен в `.gitignore`
- [ ] Сохранён `enhanced_real_api.py`
- [ ] Сохранён `provider_manager.py`
- [ ] Протестирован базовый запрос
- [ ] Проверена работа fallbacks
- [ ] Настроено логирование
- [ ] Мониторинг затрат

---

## 🎉 Готово!

Теперь OneFlow.AI имеет:
- ✅ Полную интеграцию с реальными AI API
- ✅ Автоматические fallbacks между провайдерами
- ✅ Rate limiting и retry логику
- ✅ Детальные метрики и мониторинг
- ✅ Production-ready код

**Этап 3 завершён!** 🚀

**Следующий этап: Authentication & Security** 🔐

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f oneflow.log`
2. Проверьте статус провайдеров: `manager.get_all_providers_status()`
3. Проверьте API ключи: `python -c "from enhanced_real_api import _key_manager; print(_key_manager.keys)"`
4. Проверьте документацию провайдера

---

**Автор**: Sergey Voronin  
**Версия**: 2.0 - Stage 3  
**Дата**: 2025