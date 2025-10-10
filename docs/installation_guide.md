# OneFlow.AI Installation Guide
## Руководство по установке OneFlow.AI

Complete guide to install and configure OneFlow.AI with real AI providers.

Полное руководство по установке и настройке OneFlow.AI с реальными AI провайдерами.

---

## 📋 Prerequisites | Требования

- Python 3.7 or higher | Python 3.7 или выше
- pip package manager | менеджер пакетов pip
- Git (optional) | Git (опционально)
- API keys for AI providers | API ключи для AI провайдеров

---

## 🚀 Quick Installation | Быстрая установка

### Step 1: Download Project | Шаг 1: Скачать проект

```bash
# If you have git:
git clone <repository-url>
cd OneFlow.AI

# Or download and extract ZIP file
```

### Step 2: Install Dependencies | Шаг 2: Установить зависимости

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys | Шаг 3: Настроить API ключи

```bash
python setup_keys.py
```

This interactive script will guide you through setting up API keys for:
- OpenAI (required for GPT models)
- Anthropic (optional, for Claude models)
- Stability AI (optional, for image generation)
- ElevenLabs (optional, for audio generation)
- Runway ML (optional, for video generation)

**Этот интерактивный скрипт поможет настроить API ключи для:**
- OpenAI (обязательно для GPT моделей)
- Anthropic (опционально, для моделей Claude)
- Stability AI (опционально, для генерации изображений)
- ElevenLabs (опционально, для генерации аудио)
- Runway ML (опционально, для генерации видео)

### Step 4: Verify Installation | Шаг 4: Проверить установку

```bash
# Run tests
pytest -v

# Start interactive mode
python -m src.main
```

---

## 🔑 Getting API Keys | Получение API ключей

### OpenAI (Required | Обязательно)

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Create new secret key
4. Copy the key (starts with `sk-`)

**Cost**: Pay-as-you-go, ~$0.002 per 1K tokens for GPT-3.5
**Стоимость**: Оплата по факту, ~$0.002 за 1K токенов для GPT-3.5

### Anthropic (Optional | Опционально)

1. Go to: https://console.anthropic.com/settings/keys
2. Sign up or log in
3. Create API key
4. Copy the key (starts with `sk-ant-`)

**Cost**: Pay-as-you-go, pricing varies by model
**Стоимость**: Оплата по факту, цены зависят от модели

### Stability AI (Optional | Опционально)

1. Go to: https://platform.stability.ai/account/keys
2. Sign up or log in
3. Generate API key
4. Copy the key

**Cost**: Credits-based system, $10 for 1000 credits
**Стоимость**: Система кредитов, $10 за 1000 кредитов

### ElevenLabs (Optional | Опционально)

1. Go to: https://elevenlabs.io/app/settings/api-keys
2. Sign up or log in
3. Generate API key
4. Copy the key

**Cost**: Free tier available, paid plans from $5/month
**Стоимость**: Есть бесплатный тариф, платные от $5/месяц

### Runway ML (Optional | Опционально)

1. Go to: https://runwayml.com/account
2. Sign up or log in
3. Get API credentials
4. Copy the key

**Cost**: Credits-based, varies by generation type
**Стоимость**: Система кредитов, зависит от типа генерации

---

## 📁 Project Structure After Installation | Структура проекта после установки

```
OneFlow.AI/
├── .api_keys.json          # ⚠ YOUR API KEYS (never commit!)
├── .api_keys.example.json  # Example template
├── .gitignore              # Git ignore rules
├── setup_keys.py           # API keys setup script
├── requirements.txt        # Python dependencies
├── setup.py                # Package setup
├── Makefile                # Automation commands
│
├── src/
│   ├── api_keys.py         # API key management
│   ├── main.py             # Main application
│   ├── router.py           # Request routing
│   ├── pricing.py          # Cost calculation
│   ├── wallet.py           # Credit management
│   ├── analytics.py        # Usage tracking
│   ├── budget.py           # Budget controls
│   ├── config.py           # Configuration
│   ├── cli.py              # Command-line interface
│   └── providers/          # AI provider implementations
│
├── tests/                  # Test suite
└── docs/                   # Documentation
```

---

## ⚙️ Configuration Options | Опции конфигурации

### Option 1: Using setup script (Recommended | Рекомендуется)

```bash
python setup_keys.py
```

Interactive setup with guidance.
Интерактивная настройка с подсказками.

### Option 2: Environment Variables

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Option 3: Manual .api_keys.json

Create `.api_keys.json` file:

```json
{
  "openai": "sk-your-openai-api-key",
  "anthropic": "sk-ant-your-anthropic-key",
  "stability": "your-stability-key",
  "elevenlabs": "your-elevenlabs-key",
  "runway": "your-runway-key"
}
```

**⚠ Important**: Set file permissions:
```bash
chmod 600 .api_keys.json
```

---

## 🧪 Testing Installation | Проверка установки

### 1. Run Unit Tests

```bash
# All tests
pytest -v

# Expected: 58+ tests passing ✅
```

### 2. Test with Demo Mode

```bash
python -m src.main --demo
```

This runs without requiring API keys (uses mock providers).
Запускается без API ключей (использует mock провайдеры).

### 3. Test Real API (if configured)

```bash
# Interactive mode
python -m src.main

# CLI mode
python -m src.cli request gpt "Hello, world!"
```

---

## ❗ Troubleshooting | Решение проблем

### Issue: "Module not found"

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "API key not configured"

**Solution**:
```bash
# Re-run setup
python setup_keys.py

# Or check .api_keys.json exists and is readable
ls -la .api_keys.json
```

### Issue: "Permission denied on .api_keys.json"

**Solution**:
```bash
chmod 600 .api_keys.json
```

### Issue: "API request failed"

**Possible causes**:
1. Invalid API key
2. Insufficient credits/quota
3. Network connection
4. Rate limits

**Solution**:
```bash
# Verify key is correct
python -c "from src.api_keys import get_key_manager; km = get_key_manager(); print(km.get_masked_key('openai'))"

# Check account status on provider website
```

---

## 💰 Cost Management | Управление затратами

### Set Budget Limits

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=100)

# Set daily limit
system.setup_budget(daily=10)  # $10 per day

# Set per-provider limit
system.setup_provider_budget('gpt', 50)  # $50 for GPT
```

### Monitor Usage

```bash
# View analytics
python -m src.cli analytics

# Export usage data
python -m src.cli analytics --export usage.json
```

---

## 🔒 Security Best Practices | Лучшие практики безопасности

### ✅ DO | ДЕЛАЙТЕ:

- ✅ Add `.api_keys.json` to `.gitignore`
- ✅ Set file permissions: `chmod 600 .api_keys.json`
- ✅ Use environment variables in production
- ✅ Rotate API keys regularly
- ✅ Set spending limits on provider dashboards
- ✅ Monitor API usage and costs

### ❌ DON'T | НЕ ДЕЛАЙТЕ:

- ❌ Commit API keys to Git
- ❌ Share API keys publicly
- ❌ Use production keys in development
- ❌ Store keys in plain text in public locations
- ❌ Hardcode keys in source code

---

## 📊 Verifying API Key Setup | Проверка настройки API ключей

Run this command to check configured providers:

```bash
python -c "from src.api_keys import get_key_manager; km = get_key_manager(); print('Configured providers:', km.list_providers()); [print(f'{p}: {km.get_masked_key(p)}') for p in ['openai', 'anthropic', 'stability', 'elevenlabs', 'runway']]"
```

Expected output:
```
Configured providers: ['openai']
openai: sk-...abc1
anthropic: Not configured
stability: Not configured
elevenlabs: Not configured
runway: Not configured
```

---

## 🎓 Next Steps | Следующие шаги

After installation:

1. **Read documentation**: Check `QUICKSTART.md` for usage examples
2. **Try examples**: Explore `EXAMPLES.md` for code samples
3. **Configure budget**: Set spending limits to control costs
4. **Start building**: Use OneFlow.AI in your projects!

**После установки:**

1. **Прочитайте документацию**: См. `QUICKSTART.md` для примеров
2. **Попробуйте примеры**: Изучите `EXAMPLES.md` с примерами кода
3. **Настройте бюджет**: Установите лимиты расходов
4. **Начните разработку**: Используйте OneFlow.AI в своих проектах!

---

## 📞 Support | Поддержка

- **Documentation**: See `/docs` folder
- **Issues**: Check troubleshooting section above
- **Email**: voroninsergeiai@gmail.com

---

## ✅ Installation Checklist | Контрольный список установки

- [ ] Python 3.7+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API keys configured (at least OpenAI)
- [ ] `.api_keys.json` in `.gitignore`
- [ ] Tests pass (`pytest -v`)
- [ ] Demo mode works (`python -m src.main --demo`)
- [ ] Can make real API requests

**You're ready to use OneFlow.AI! 🎉**

**Вы готовы использовать OneFlow.AI! 🎉**
