# OneFlow.AI Quick Start Guide
## Руководство по быстрому старту OneFlow.AI

Get up and running with OneFlow.AI in 5 minutes!

Начните работу с OneFlow.AI за 5 минут!

---

## 🚀 Installation | Установка

### Prerequisites | Требования

- Python 3.7 or higher | Python 3.7 или выше
- pip package manager | менеджер пакетов pip

### Step 1: Clone Repository | Шаг 1: Клонировать репозиторий

```bash
git clone <repository-url>
cd OneFlow.AI
```

### Step 2: Install Dependencies | Шаг 2: Установить зависимости

```bash
pip install -r requirements.txt
```

That's it! You're ready to go. | Вот и всё! Вы готовы к работе.

---

## 🎯 Your First Request | Ваш первый запрос

### Option 1: Python API | Вариант 1: Python API

Create a file `my_first_request.py`:

```python
from src.main import OneFlowAI

# Initialize system with 100 credits
system = OneFlowAI(initial_balance=100)

# Make your first request
result = system.process_request('gpt', 'Hello, OneFlow.AI!')

# Print result
if result['status'] == 'success':
    print(f"✓ Response: {result['response']}")
    print(f"✓ Cost: {result['cost']} credits")
    print(f"✓ Balance: {result['balance']} credits")
else:
    print(f"✗ Error: {result['message']}")
```

Run it:
```bash
python my_first_request.py
```

### Option 2: Interactive Mode | Вариант 2: Интерактивный режим

```bash
python -m src.main
```

Follow the prompts:
```
Enter model type (gpt, image, audio, video): gpt
Enter your prompt: Hello world
```

### Option 3: Command Line | Вариант 3: Командная строка

```bash
python -m src.cli request gpt "Hello, OneFlow.AI!"
```

---

## 📊 Check Your Status | Проверьте статус

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=100)

# Make some requests
system.process_request('gpt', 'Tell me a joke')
system.process_request('image', 'A beautiful sunset')

# Check status
print(system.get_status())
```

Or using CLI:
```bash
python -m src.cli status
```

---

## 💰 Set a Budget | Установите бюджет

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=500)

# Set daily budget limit
system.setup_budget(daily=50)

# Set provider-specific limit
system.setup_provider_budget('video', 100)

# Now requests will respect these limits
result = system.process_request('video', 'Cat playing')
```

Or using CLI:
```bash
python -m src.cli set-budget daily 50
```

---

## 📈 View Analytics | Просмотр аналитики

```python
from src.main import OneFlowAI

system = OneFlowAI(initial_balance=100)

# Make several requests
for i in range(5):
    system.process_request('gpt', f'Request {i+1}')

# View analytics report
print(system.analytics.get_summary_report())
```

Or using CLI:
```bash
python -m src.cli analytics --detailed
```

---

## ⚙️ Use Configuration File | Использование файла конфигурации

### Create `my_config.json`:

```json
{
  "rates": {
    "gpt": 0.5,
    "image": 5.0,
    "audio": 2.5,
    "video": 10.0
  },
  "wallet_balance": 200.0,
  "budget_limits": {
    "daily": 50.0,
    "weekly": 300.0
  },
  "region": "US"
}
```

### Load and use:

```python
from config import Config
from src.main import OneFlowAI

# Load configuration
config = Config('my_config.json')

# Create system with config
system = OneFlowAI(initial_balance=config.wallet_balance)

# Make request (will use custom rates)
result = system.process_request('gpt', 'Hello')
```

Or using CLI:
```bash
python -m src.cli --config my_config.json request gpt "Hello"
```

---

## 🎮 Try the Demo | Попробуйте демо

```bash
python -m src.main --demo
```

This runs a complete demonstration showing:
- Multiple request types
- Budget enforcement
- Cost tracking
- Analytics reporting

---

## 🧪 Run Tests | Запуск тестов

Verify everything is working:

```bash
# Run all tests
pytest -v

# Expected output: 58+ tests passing ✅
```

---

## 📚 Next Steps | Следующие шаги

Now that you're up and running, explore:

1. **Full Examples**: See `EXAMPLES.md` for 15+ detailed examples
2. **Developer Guide**: Read `DEVELOPER_GUIDE.md` to extend OneFlow.AI
3. **API Reference**: Check documentation for all available methods
4. **Configuration**: Review `config.example.json` for all options

---

## 🆘 Common Issues | Распространённые проблемы

### Issue: "Module not found"
**Solution**: Make sure you're in the project root directory and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Insufficient credits"
**Solution**: Increase initial balance:
```python
system = OneFlowAI(initial_balance=1000)  # More credits
```

Or add credits:
```bash
python -m src.cli add-credits 500
```

### Issue: "Budget limit exceeded"
**Solution**: Adjust or remove budget limits:
```python
system.setup_budget(daily=None)  # Remove daily limit
```

---

## 💡 Tips & Tricks | Советы и хитрости

### Tip 1: Use Demo Mode for Learning
```bash
python -m src.main --demo
```
Great way to see all features in action!

### Tip 2: Export Analytics for Analysis
```bash
python -m src.cli analytics --export my_analytics.json
```

### Tip 3: Check Balance Before Expensive Requests
```python
if system.wallet.can_afford(cost):
    result = system.process_request('video', 'My prompt')
```

### Tip 4: Use Configuration for Different Environments
```bash
# Development
python -m src.cli --config config.dev.json request gpt "Test"

# Production
python -m src.cli --config config.prod.json request gpt "Production query"
```

---

## 📖 Command Reference | Справочник команд

### CLI Commands | CLI команды

```bash
# Make request
python -m src.cli request <model> "<prompt>"

# Check status
python -m src.cli status

# View analytics
python -m src.cli analytics
python -m src.cli analytics --detailed
python -m src.cli analytics --export file.json

# View budget
python -m src.cli budget

# Add credits
python -m src.cli add-credits <amount>

# Set budget limit
python -m src.cli set-budget <period> <amount>

# View configuration
python -m src.cli config

# Use custom config
python -m src.cli --config my_config.json <command>

# Verbose mode
python -m src.cli -v <command>
```

### Python API Quick Reference | Быстрый справочник Python API

```python
from src.main import OneFlowAI

# Initialize
system = OneFlowAI(initial_balance=100)

# Make request
result = system.process_request(model, prompt)

# Setup budget
system.setup_budget(daily=50, weekly=300)
system.setup_provider_budget('gpt', 100)

# View status
print(system.get_status())

# Analytics
print(system.analytics.get_summary_report())
print(system.analytics.get_total_cost())
print(system.analytics.get_most_used_provider())

# Budget
print(system.budget.get_budget_summary())
remaining = system.budget.get_remaining(BudgetPeriod.DAILY)

# Wallet
system.wallet.add_credits(50)
balance = system.wallet.get_balance()
can_afford = system.wallet.can_afford(cost)
```

---

## 🎓 Learning Path | Путь обучения

1. ✅ **Start here** - Complete this quickstart
2. 📖 **Read README.md** - Understand features and architecture
3. 💻 **Try examples** - Work through EXAMPLES.md
4. 🛠️ **Extend system** - Follow DEVELOPER_GUIDE.md
5. 🚀 **Build something** - Create your own application!

---

## ✨ You're Ready! | Вы готовы!

Congratulations! You now know how to:
- ✅ Make AI requests
- ✅ Track analytics
- ✅ Manage budgets
- ✅ Use configuration
- ✅ Run from CLI or Python

**Happy coding with OneFlow.AI!** 🎉

**Удачного программирования с OneFlow.AI!** 🎉

---

**Need help?** Check the full documentation:
- `README.md` - Features and usage
- `EXAMPLES.md` - Code examples
- `DEVELOPER_GUIDE.md` - Technical details

**Нужна помощь?** Проверьте полную документацию выше.
