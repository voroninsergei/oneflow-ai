# OneFlow.AI v2.0 - Production Ready

> AI Model Aggregator with Pricing, Routing, Analytics & Authentication

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status: Production](https://img.shields.io/badge/status-production-green.svg)]()

## 🚀 Быстрый старт | Quick Start

```bash
# 1. Клонировать репозиторий | Clone repository
git clone <repository-url>
cd OneFlow.AI

# 2. Установить зависимости | Install dependencies
pip install -r requirements.txt

# 3. Запустить демо | Run demo
python -m src.main --demo
```

## 📋 Возможности | Features

### ✅ Core Features
- **Multi-modal AI Support** - Text, Image, Audio, Video generation
- **Smart Routing** - Automatic provider selection with fallbacks
- **Transparent Pricing** - Upfront cost estimation
- **Unified Wallet** - Credit management across providers
- **Budget Controls** - Daily/weekly/monthly limits
- **Analytics Dashboard** - Usage tracking & reporting
- **Multi-region** - US/EU/RU support

### ✅ Advanced Features (v2.0)
- **Database Persistence** - SQLAlchemy with SQLite/PostgreSQL
- **Web API** - FastAPI with interactive dashboard
- **JWT Authentication** - Secure user management
- **API Keys** - Per-user authentication keys
- **Rate Limiting** - Automatic request throttling
- **Real API Integration** - OpenAI, Anthropic, Stability AI, ElevenLabs
- **Automatic Fallbacks** - 99.9% uptime guarantee
- **Performance Metrics** - Real-time monitoring

## 📦 Установка | Installation

### Базовая установка | Basic Installation

```bash
pip install -r requirements.txt
```

### Полная установка | Full Installation

```bash
# Все зависимости включая real API, web server, database
pip install -r requirements.txt
pip install openai anthropic requests  # Real API providers
pip install fastapi uvicorn            # Web server
pip install sqlalchemy                 # Database
pip install PyJWT passlib              # Authentication
```

### Установка как пакет | Install as Package

```bash
pip install -e .                       # Development mode
# или | or
pip install -e ".[dev,api,web,db,auth]"  # All features
```

## 🎮 Использование | Usage

### 1. Interactive Mode (Интерактивный режим)

```bash
python -m src.main
```

### 2. Demo Mode (Демонстрационный режим)

```bash
python -m src.main --demo
```

### 3. Web Dashboard (Веб-дашборд)

```bash
python web_server.py
# Открыть: http://localhost:8000
```

### 4. CLI Interface

```bash
# Статус системы | System status
python -m src.cli status

# Сделать запрос | Make request
python -m src.cli request gpt "Hello world"

# Аналитика | Analytics
python -m src.cli analytics --detailed

# Управление бюджетом | Budget management
python -m src.cli set-budget daily 100
```

### 5. Python API

```python
from src.main import OneFlowAI

# Инициализация | Initialize
system = OneFlowAI(initial_balance=100)

# Настройка бюджета | Setup budget
system.setup_budget(daily=50)

# Запрос | Make request
result = system.process_request('gpt', 'Hello world')

if result['status'] == 'success':
    print(f"Response: {result['response']}")
    print(f"Cost: {result['cost']} credits")
```

## 🔑 Настройка API ключей | API Keys Setup

### Интерактивная настройка | Interactive Setup

```bash
python setup_keys.py
```

### Ручная настройка | Manual Setup

Создайте `.api_keys.json`:

```json
{
  "openai": "sk-your-openai-key",
  "anthropic": "sk-ant-your-anthropic-key",
  "stability": "sk-your-stability-key",
  "elevenlabs": "your-elevenlabs-key"
}
```

**⚠️ ВАЖНО**: Добавьте в `.gitignore`:

```bash
echo ".api_keys.json" >> .gitignore
chmod 600 .api_keys.json
```

## 📊 Архитектура | Architecture

```
┌─────────────────────────────────────────┐
│         User Interfaces                 │
│  CLI | Interactive | Web API | Python   │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│      OneFlowAI Orchestrator             │
│  - Request Processing                   │
│  - Provider Management                  │
│  - Cost Calculation                     │
└──┬────┬────┬────┬────┬────┬─────────────┘
   │    │    │    │    │    │
   ▼    ▼    ▼    ▼    ▼    ▼
┌─────────────────────────────────────────┐
│         Core Services                   │
│  Router | Pricing | Wallet              │
│  Analytics | Budget | Config            │
│  Database | Auth                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│      Provider Layer                     │
│  GPT | Image | Audio | Video            │
│  + Real API Integration                 │
└─────────────────────────────────────────┘
```

## 🧪 Тестирование | Testing

```bash
# Все тесты | All tests
pytest -v

# С покрытием | With coverage
pytest --cov=src tests/

# Конкретный модуль | Specific module
pytest tests/test_pricing.py -v
```

**Ожидается**: 58+ тестов проходят ✅

## 📖 Документация | Documentation

- **[QUICKSTART.md](docs/quickstart.md)** - Быстрый старт
- **[EXAMPLES.md](docs/examples.md)** - Примеры использования
- **[DEVELOPER_GUIDE.md](docs/developer_guide.md)** - Руководство разработчика
- **[API_SEPARATION_GUIDE.md](docs/api_separation_guide.md)** - API ключи
- **[DATABASE_SETUP_GUIDE.md](docs/database_setup_guide.md)** - База данных
- **[AUTH_GUIDE.md](docs/auth_guide.md)** - Аутентификация
- **[REAL_API_GUIDE.md](docs/real_api_guide.md)** - Реальные API

## 🏗️ Структура проекта | Project Structure

```
OneFlow.AI/
├── src/                      # Исходный код | Source code
│   ├── main.py              # Main application
│   ├── router.py            # Smart routing
│   ├── pricing.py           # Cost calculation
│   ├── wallet.py            # Credit management
│   ├── analytics.py         # Usage tracking
│   ├── budget.py            # Budget controls
│   ├── config.py            # Configuration
│   ├── database.py          # Database module
│   ├── auth_module.py       # Authentication
│   └── providers/           # AI providers
├── tests/                   # Test suite
├── docs/                    # Documentation
├── web_server.py            # FastAPI server
├── requirements.txt         # Dependencies
└── setup.py                 # Package setup
```

## 🎯 Возможности по модулям | Features by Module

### 1. Core System
- ✅ Provider routing with fallbacks
- ✅ Cost estimation before requests
- ✅ Credit management
- ✅ Budget enforcement

### 2. Analytics
- ✅ Request tracking
- ✅ Provider statistics
- ✅ Cost analysis
- ✅ Export to JSON

### 3. Database
- ✅ Request history
- ✅ Transaction log
- ✅ User management
- ✅ Provider configuration

### 4. Web API
- ✅ REST API endpoints
- ✅ Interactive dashboard
- ✅ Swagger documentation
- ✅ CORS support

### 5. Authentication
- ✅ JWT tokens
- ✅ User registration/login
- ✅ API key management
- ✅ Rate limiting

### 6. Real API Integration
- ✅ OpenAI (GPT, DALL-E)
- ✅ Anthropic (Claude)
- ✅ Stability AI
- ✅ ElevenLabs
- ✅ Automatic fallbacks
- ✅ Retry logic

## 💰 Pricing | Ценообразование

Default rates (configurable):

| Provider | Type | Cost | Unit |
|----------|------|------|------|
| GPT | Text | 1 credit | per word |
| Image | Image | 10 credits | per image |
| Audio | Audio | 5 credits | per audio |
| Video | Video | 20 credits | per video |

## 🔒 Безопасность | Security

- ✅ JWT authentication with access/refresh tokens
- ✅ Password hashing with bcrypt
- ✅ API key per user
- ✅ Rate limiting (60 req/min, 1000 req/hour)
- ✅ Role-based access control
- ✅ Secure API key storage

## 🌍 Multi-language Support

All code, documentation, and comments are available in:
- ✅ English
- ✅ Russian (Русский)

## 📈 Статус проекта | Project Status

**Готовность**: 100% ✅

- ✅ Core functionality
- ✅ Analytics & Budget
- ✅ Web API & Dashboard
- ✅ Database integration
- ✅ Authentication & Security
- ✅ Real API integration
- ✅ Comprehensive documentation
- ✅ Complete test suite

## 🤝 Contributing

This is a proprietary project. See LICENSE for details.

## 📝 License

Copyright (c) 2025 Sergey Voronin. All rights reserved.

See [LICENSE](LICENSE) file for details.

## 👤 Author

**Sergey Voronin**
- Email: voroninsergeiai@gmail.com
- Project: OneFlow.AI v2.0

## 🙏 Acknowledgments

Built with:
- FastAPI - Web framework
- SQLAlchemy - ORM
- PyJWT - Authentication
- OpenAI, Anthropic, Stability AI, ElevenLabs - AI providers

---

**OneFlow.AI v2.0 - Production Ready** 🚀

Made with ❤️ by Sergey Voronin
