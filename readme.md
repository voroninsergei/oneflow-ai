# OneFlow.AI v2.0 - Production Ready 🚀

AI Model Aggregator with Pricing, Routing, Analytics & **Secure Secret Management**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-enhanced-brightgreen.svg)](docs/SECURITY_GUIDE.md)

---

## 🎯 Что нового в v2.0

- ✅ **Безопасное хранение секретов** - поддержка AWS, Vault, GCP, Azure
- ✅ **12-factor app** - конфигурация через переменные окружения
- ✅ **Docker & Kubernetes** - готовые конфигурации для деплоя
- ✅ **Pre-commit hooks** - автоматическая проверка безопасности
- ✅ **Миграция** - автоматический переход с `.api_keys.json`

---

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd OneFlow.AI

# Установить зависимости
pip install -r requirements.txt

# Установить pre-commit hooks (рекомендуется)
pip install pre-commit
pre-commit install
```

### 2. Настройка секретов

#### ⚡ Для разработки (рекомендуется)

```bash
# Скопировать шаблон
cp .env.example .env

# Отредактировать .env и добавить свои ключи
nano .env
```

Пример `.env`:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
STABILITY_API_KEY=sk-your-key-here
ELEVENLABS_API_KEY=your-key-here
JWT_SECRET_KEY=your-secret-key-here
```

#### 🔒 Миграция со старого формата

Если у вас есть `.api_keys.json`:

```bash
# Автоматическая миграция
python migrate_to_env.py

# Или миграция во все форматы
python migrate_to_env.py --all
```

#### 🏢 Для продакшена

См. [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) для настройки:
- AWS Secrets Manager
- HashiCorp Vault
- Google Cloud Secret Manager
- Azure Key Vault
- Kubernetes Secrets

### 3. Запуск

```bash
# Демо режим
python -m src.main --demo

# Web сервер
python web_server.py

# Docker
docker-compose up -d

# Kubernetes
kubectl apply -f kubernetes-deployment.yaml
```

---

## 📋 Возможности

### 🤖 Multi-modal AI Support
- ✅ Text generation (GPT, Claude)
- ✅ Image generation (DALL-E, Stable Diffusion)
- ✅ Audio generation (ElevenLabs)
- ✅ Video generation

### 🎯 Smart Routing
- ✅ Автоматический выбор провайдера
- ✅ Fallback при недоступности
- ✅ Балансировка нагрузки

### 💰 Transparent Pricing
- ✅ Предварительная оценка стоимости
- ✅ Детальная аналитика расходов
- ✅ Бюджетный контроль

### 🔐 Security & Authentication
- ✅ JWT аутентификация
- ✅ API key management
- ✅ Rate limiting
- ✅ **Безопасное хранение секретов**

### 📊 Analytics & Monitoring
- ✅ Трекинг использования
- ✅ Статистика по провайдерам
- ✅ Анализ затрат
- ✅ Экспорт в JSON

---

## 🔒 Безопасность

### ❌ Что больше НЕ поддерживается

```json
// .api_keys.json - УСТАРЕЛО и НЕБЕЗОПАСНО
{
  "openai": "sk-proj-...",
  "anthropic": "sk-ant-..."
}
```

### ✅ Новый безопасный подход

```python
from src.config import get_config

# Автоматическое определение источника секретов
config = get_config()
config.validate()

# Использование
openai_key = config.OPENAI_API_KEY
```

### 🛡️ Поддерживаемые Secret Managers

| Метод | Безопасность | Рекомендация |
|-------|--------------|--------------|
| Environment Variables | ⭐⭐ | Development |
| Docker Secrets | ⭐⭐⭐ | Small Production |
| Kubernetes Secrets | ⭐⭐⭐ | K8s Deployments |
| AWS Secrets Manager | ⭐⭐⭐⭐⭐ | AWS Production |
| HashiCorp Vault | ⭐⭐⭐⭐⭐ | Enterprise |
| GCP Secret Manager | ⭐⭐⭐⭐⭐ | GCP Production |
| Azure Key Vault | ⭐⭐⭐⭐⭐ | Azure Production |

Подробная документация: [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)

---

## 📦 Структура проекта

```
OneFlow.AI/
├── src/
│   ├── main.py              # Главное приложение
│   ├── config.py            # ⭐ Новая система конфигурации
│   ├── router.py            # Умная маршрутизация
│   ├── pricing.py           # Расчет стоимости
│   ├── wallet.py            # Управление кредитами
│   ├── analytics.py         # Аналитика
│   ├── budget.py            # Бюджетный контроль
│   ├── database.py          # База данных
│   ├── auth_module.py       # Аутентификация
│   └── providers/           # AI провайдеры
├── docs/
│   ├── SECURITY_GUIDE.md    # ⭐ Руководство по безопасности
│   ├── QUICKSTART.md        # Быстрый старт
│   ├── EXAMPLES.md          # Примеры
│   └── API_DOCUMENTATION.md # API документация
├── .env.example             # ⭐ Шаблон переменных окружения
├── .pre-commit-config.yaml  # ⭐ Git hooks для безопасности
├── docker-compose.yml       # ⭐ Docker конфигурация
├── kubernetes-deployment.yaml # ⭐ K8s конфигурация
├── terraform-aws-secrets.tf # ⭐ Terraform для AWS
├── migrate_to_env.py        # ⭐ Скрипт миграции
├── requirements.txt         # Зависимости
└── README.md                # Этот файл
```

---

## 🔧 Конфигурация

### Environment Variables

```bash
# API Keys (обязательно)
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:pass@localhost/oneflow

# Security
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO

# Features
ENABLE_ANALYTICS=true
ENABLE_BUDGET_ENFORCEMENT=true
ENABLE_RATE_LIMITING=true
```

### AWS Secrets Manager

```bash
# Установка переменных
export AWS_SECRET_NAME=oneflow-ai/api-keys
export AWS_REGION=us-east-1

# Или использование Terraform
cd terraform/
terraform init
terraform apply
```

### Kubernetes

```bash
# Создание секретов
kubectl create secret generic oneflow-api-keys \
  --from-literal=openai-key='sk-proj-...' \
  --from-literal=anthropic-key='sk-ant-...' \
  --namespace=oneflow

# Деплой
kubectl apply -f kubernetes-deployment.yaml
```

---

## 🧪 Тестирование

```bash
# Все тесты
pytest -v

# С покрытием
pytest --cov=src tests/

# Конкретный модуль
pytest tests/test_config.py -v

# Проверка безопасности
pre-commit run --all-files
```

---

## 📊 Использование

### Python API

```python
from src.main import OneFlowAI

# Инициализация
system = OneFlowAI(initial_balance=100)

# Настройка бюджета
system.setup_budget(daily=50)

# Запрос к AI
result = system.process_request('gpt', 'Hello world')

if result['status'] == 'success':
    print(f"Response: {result['response']}")
    print(f"Cost: {result['cost']} credits")
```

### CLI

```bash
# Статус системы
python -m src.cli status

# Запрос к модели
python -m src.cli request gpt "Write a poem"

# Аналитика
python -m src.cli analytics --detailed

# Управление бюджетом
python -m src.cli set-budget daily 100
```

### Web API

```bash
# Запуск сервера
python web_server.py

# Открыть dashboard
open http://localhost:8000

# Swagger документация
open http://localhost:8000/docs
```

---

## 🚢 Deployment

### Docker

```bash
# Build
docker build -t oneflow-ai:latest .

# Run
docker-compose up -d

# Logs
docker-compose logs -f oneflow-ai

# Stop
docker-compose down
```

### Kubernetes

```bash
# Создать namespace
kubectl create namespace oneflow

# Создать секреты
kubectl create secret generic oneflow-api-keys \
  --from-literal=openai-key='...' \
  --namespace=oneflow

# Deploy
kubectl apply -f kubernetes-deployment.yaml

# Проверка
kubectl get pods -n oneflow
kubectl logs -f deployment/oneflow-ai -n oneflow
```

### AWS ECS/EC2

```bash
# Terraform
cd terraform/
terraform init
terraform plan
terraform apply

# Или CloudFormation
aws cloudformation create-stack \
  --stack-name oneflow-ai \
  --template-body file://cloudformation.yaml
```

---

## 📖 Документация

- [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) - **⭐ Безопасность и секреты**
- [QUICKSTART.md](docs/QUICKSTART.md) - Быстрый старт
- [EXAMPLES.md](docs/EXAMPLES.md) - Примеры использования
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - API документация
- [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) - Руководство разработчика

---

## 🔄 Миграция с v1.x

Если вы используете старую версию с `.api_keys.json`:

```bash
# Автоматическая миграция
python migrate_to_env.py

# Проверка
python -m src.main --demo

# Удаление старого файла
rm .api_keys.json
```

**Важно:** См. [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) для деталей миграции.

---

## 🤝 Contributing

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Стандарты разработки

- ✅ Все секреты только через переменные окружения
- ✅ Pre-commit hooks должны проходить
- ✅ Покрытие тестами > 80%
- ✅ Следование PEP 8
- ✅ Документация обязательна

---

## 📝 License

This is a proprietary project. See [LICENSE](LICENSE) for details.

Copyright © 2025 Sergey Voronin. All rights reserved.

---

## 👤 Author

**Sergey Voronin**
- Email: voroninsergeiai@gmail.com
- Project: OneFlow.AI v2.0

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [PyJWT](https://pyjwt.readthedocs.io/) - Authentication
- [OpenAI](https://openai.com/), [Anthropic](https://anthropic.com/), [Stability AI](https://stability.ai/), [ElevenLabs](https://elevenlabs.io/) - AI providers

---

## 📊 Roadmap

- [ ] GraphQL API
- [ ] WebSocket support
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] Plugin system

---

**Made with ❤️ by Sergey Voronin | OneFlow.AI v2.0 - Production Ready 🚀**

> ⚠️ **Security First**: Эта версия полностью переработана с фокусом на безопасность. Больше никаких секретов в JSON файлах!
