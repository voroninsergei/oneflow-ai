# OneFlow.AI v0.1.0 – Beta Preview 🚧

> **Note:** This project is currently in **beta**.  While many of the building blocks for a production–grade system are in place, we are still collecting real‑world telemetry and iterating on the architecture.  Please treat it as a preview rather than a finished, battle‑hardened product.

> Enterprise-grade AI Model Aggregator с маршрутизацией, ценообразованием, аналитикой и полной observability

[![Status](https://img.shields.io/badge/status-beta-yellow)](/)
[![Test Coverage](https://img.shields.io/badge/coverage-~80%25-brightgreen)](/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-experimental-lightblue)](/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](/)

---

## 🎯 Что это?

OneFlow.AI — это **ценовой и маршрутизирующий слой** для AI‑моделей.  Он предоставляет общую точку входа к нескольким провайдерам искусственного интеллекта, оценивает стоимость запроса по числу токенов, выбирает наиболее подходящую модель и обеспечивает мониторинг и безопасность.  Проект находится на стадии **beta**, поэтому некоторые функции и показатели ещё будут меняться.

- 🔀 **Автоматически выбирает** оптимальную модель (цена/скорость/качество)
- 💰 **Прозрачное ценообразование** на основе токенов с нормализацией к кредитам
- 🔄 **Умные fallback** при недоступности провайдеров (в стадии тестирования)
- 📊 **Детальная аналитика** использования и затрат
- 🔐 **Enterprise security** с JWT, API keys rotation, CORS
- 📈 **Observability** с Prometheus, Grafana, OpenTelemetry (в разработке)

---

## 📍 Статус проекта и дорожная карта

### ✅ Что уже работает (Beta)

- ✅ Token-based ценообразование с нормализацией к кредитам
- ✅ Интеллектуальная маршрутизация (cost/latency/quality/balanced)
- ✅ Интеграция с OpenAI, Anthropic, Stability AI, ElevenLabs
- ✅ Circuit breaker и retry логика
- ✅ Базовая аутентификация (JWT, API keys)
- ✅ Health и readiness probes
- ✅ Prometheus metrics endpoint
- ✅ Docker и docker-compose конфигурация
- ✅ Базовое покрытие тестами (~80%)
- ✅ Structured logging

### 🚧 В активной разработке

- 🚧 **Observability stack**: Настройка Grafana dashboards и OpenTelemetry трассировки
- 🚧 **Real-world SLO**: Сбор метрик доступности и latency в production-like окружении
- 🚧 **CI/CD pipeline**: GitHub Actions для automated testing и deployment
- 🚧 **API versioning**: Формализация OpenAPI спецификации
- 🚧 **Rate limiting**: Тонкая настройка лимитов per-user/per-project
- 🚧 **Kubernetes production config**: StatefulSets, PVC, HPA, ingress

### 🔮 В планах (Q2-Q3 2025)

- 🔮 Расширенная аналитика (cost breakdown, usage patterns)
- 🔮 Admin dashboard для управления провайдерами
- 🔮 Webhooks для событий (quota exceeded, provider failures)
- 🔮 Multi-region deployments
- 🔮 Advanced caching strategies
- 🔮 Cost optimization recommendations
- 🔮 A/B testing для моделей

---

## ✨ Ключевые возможности

### 🤖 Поддерживаемые провайдеры

| Провайдер | Модели | Тип | Статус |
|-----------|--------|-----|--------|
| **OpenAI** | GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5-turbo, DALL-E | Text, Image | ✅ Stable |
| **Anthropic** | Claude 3 Opus, Sonnet, Haiku | Text | ✅ Stable |
| **Stability AI** | Stable Diffusion XL, SD3 | Image | 🚧 Testing |
| **ElevenLabs** | Multilingual v2 | Audio | 🚧 Testing |

### 💎 Production-Ready Features

✅ **Observability**
- Prometheus metrics на `/metrics`
- Structured logging (JSON)
- Health/readiness probes (`/health`, `/ready`)
- OpenTelemetry distributed tracing (🚧 в настройке)

✅ **Reliability**
- Circuit breaker с exponential backoff
- Retry логика с jitter
- Timeouts (connect: 10s, read: 30s)
- Идемпотентность запросов
- Quotas per‑user/per‑provider/per‑project (🚧 в тестировании)

✅ **Security**
- JWT authentication + refresh tokens
- API keys с автоматической ротацией (🚧 grace period testing)
- Security headers (HSTS, CSP, X-Frame-Options)
- Request size limits (10MB)
- Secrets sanitization в логах
- Rate limiting (60/min, 1000/hour) — базовая реализация

✅ **Smart Routing**
- Cost-optimized: минимальная стоимость
- Latency-optimized: максимальная скорость
- Quality-optimized: лучшее качество
- Balanced: оптимальный баланс

✅ **Token‑Based Billing**
- Точный расчёт входящих и исходящих токенов для каждого запроса
- Нормализация стоимости к кредитам (по умолчанию 1 USD = 100 кредитов)
- Поддержка нескольких провайдеров и моделей
- Property‑based тесты (Hypothesis)

> Стоимость запроса вычисляется в модуле `pricing_v2.py`.  Этот модуль оперирует токенами (не словами) и учитывает различную стоимость входящих и исходящих токенов для каждого провайдера.  Подробнее см. [src/pricing_v2.py](src/pricing_v2.py).

---

## 🚀 Быстрый старт

### Предварительные требования

- **Python 3.11+** (tested on 3.11, 3.12)
- Docker 20.10+ и Docker Compose 2.0+
- PostgreSQL 14+ (или используйте docker-compose)
- Redis 7+ (или используйте docker-compose)

### Установка

```bash
# 1. Клонирование репозитория
git clone https://github.com/voroninsergei/oneflow-ai.git
cd oneflow-ai

# 2. Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# 3. Установка зависимостей
pip install -r requirements.txt

# Для разработки:
pip install -r requirements-dev.txt

# 4. Конфигурация
cp .env.example .env
nano .env  # Добавить API ключи провайдеров
```

---

## 🔑 API Keys Configuration

### Recommended: Environment Variables

```bash
# Export API keys (рекомендуемый способ)
export OPENAI_API_KEY='sk-...'
export ANTHROPIC_API_KEY='sk-ant-...'
export STABILITY_API_KEY='sk-...'
export ELEVENLABS_API_KEY='...'

# Для постоянного использования добавьте в ~/.bashrc или ~/.zshrc
echo "export OPENAI_API_KEY='sk-...'" >> ~/.bashrc
echo "export ANTHROPIC_API_KEY='sk-ant-...'" >> ~/.bashrc
source ~/.bashrc
```

### Alternative: .env File

```bash
# .env файл (не коммитить в git!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
STABILITY_API_KEY=sk-...
ELEVENLABS_API_KEY=...

# Дополнительные настройки
JWT_SECRET=your-secret-key-here
DATABASE_URL=postgresql://oneflow:password@localhost:5432/oneflow_dev
REDIS_URL=redis://localhost:6379/0
```

### Security Best Practices

⚠️ **Важно:**
- **Никогда не коммитьте** API ключи в git
- Используйте `.gitignore` для исключения `.env` файлов
- Ротируйте ключи регулярно (рекомендуется каждые 90 дней)
- Используйте разные ключи для dev/staging/production
- Для production используйте secrets management (Kubernetes Secrets, AWS Secrets Manager, HashiCorp Vault)

### Получение API ключей

| Провайдер | URL для получения ключа |
|-----------|------------------------|
| **OpenAI** | https://platform.openai.com/api-keys |
| **Anthropic** | https://console.anthropic.com/account/keys |
| **Stability AI** | https://platform.stability.ai/account/keys |
| **ElevenLabs** | https://elevenlabs.io/app/settings/api-keys |

### Проверка конфигурации

```bash
# Проверить, что ключи загружены
python -c "import os; print('OpenAI:', 'OK' if os.getenv('OPENAI_API_KEY') else 'MISSING')"
python -c "import os; print('Anthropic:', 'OK' if os.getenv('ANTHROPIC_API_KEY') else 'MISSING')"
```

---

## ⚙️ Provider Configuration

### Схема конфигурации

Конфигурация провайдеров, ценообразования и маршрутизации описана в JSON Schema:

```bash
config/
├── config.schema.json    # JSON Schema с валидацией
├── config.json          # Рабочая конфигурация
├── config.example.json  # Пример конфигурации
└── README.md           # Документация по конфигурации
```

См. **[config/README.md](config/README.md)** для полной документации по конфигурации провайдеров.

### Основные параметры

```json
{
  "providers": [
    {
      "id": "openai-primary",
      "type": "openai",
      "model": "gpt-4-turbo",
      "priority": 1,
      "weight": 100,
      "timeouts": {
        "connect_ms": 5000,
        "read_ms": 60000,
        "total_ms": 120000
      }
    }
  ],
  "pricing": {
    "version": "2025-01-15",
    "models": {
      "gpt-4-turbo": {
        "input_token_cost": 0.00001,
        "output_token_cost": 0.00003,
        "context_window": 128000
      }
    }
  },
  "routing_policy": {
    "strategy": "adaptive"
  }
}
```

### Валидация конфигурации

```bash
# Валидация против схемы
ajv validate -s config/config.schema.json -d config/config.json

# Проверка consistency
python scripts/validate_config.py

# Проверка environment variables
./scripts/check_env.sh config/config.json
```

### Единицы измерения

- **Время**: миллисекунды (ms) для таймаутов, секунды для TTL
- **Стоимость**: USD, токены **per-token** (не per 1000)
- **Rate limits**: абсолютные значения за период (per_minute, per_hour, per_day)
- **Проценты**: 0-100 для порогов
- **Скоры**: 0.0-1.0 для качества и похожести

Подробнее см. [config/README.md](config/README.md).

---

## 💻 Локальная разработка

### Локальная разработка

```bash
# Запуск всех сервисов (PostgreSQL, Redis, Prometheus, Grafana)
docker-compose up -d postgres redis

# Применение миграций
alembic upgrade head

# Запуск development сервера
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Или через Makefile:
make dev

# Открыть API документацию
open http://localhost:8000/docs
```

### Доступные эндпоинты

```bash
# Health check
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/ready

# Prometheus metrics
curl http://localhost:8000/metrics

# API v1 endpoints
curl http://localhost:8000/api/v1/estimate  # POST
curl http://localhost:8000/api/v1/request   # POST

# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

### Docker развёртывание

```bash
# Сборка образа
docker build -t oneflow-ai:0.1.0 .

# Или через Makefile:
make docker-build

# Запуск полного stack
docker-compose up -d

# Проверка здоровья
./scripts/health_check.sh

# Просмотр метрик
open http://localhost:8000/metrics
```

### Kubernetes развёртывание (Experimental)

> **Warning:** Kubernetes конфигурация находится в экспериментальной стадии. Перед production использованием требуется дополнительная настройка StatefulSets, PVC, и ingress.

```bash
# Создание namespace
kubectl create namespace oneflow-ai

# Создание secrets
kubectl create secret generic oneflow-secrets \
  --namespace oneflow-ai \
  --from-literal=JWT_SECRET=$(openssl rand -hex 32) \
  --from-literal=DATABASE_PASSWORD=$(openssl rand -hex 16) \
  --from-literal=OPENAI_API_KEY=sk-your-key \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-your-key

# Развёртывание (basic config)
kubectl apply -f k8s/ --namespace oneflow-ai

# Проверка статуса
kubectl get pods -n oneflow-ai

# Port forward для локального тестирования
kubectl port-forward -n oneflow-ai service/oneflow-ai 8000:8000
```

---

## 📖 Использование

### Python SDK

```python
from src.pricing_v2 import PricingEngine, IntelligentRouter, RoutingStrategy
from src.middleware.circuit_breaker import ResilientHTTPClient

# Инициализация
engine = PricingEngine()
router = IntelligentRouter(engine)

# Получение решения о маршрутизации
decision = router.route(
    input_tokens=1500,
    output_tokens=500,
    strategy=RoutingStrategy.COST_OPTIMIZED,
    modality="text"
)

print(f"Primary model: {decision.primary_model}")
print(f"Estimated cost: {decision.estimated_credits} credits")
print(f"Fallback chain: {decision.fallback_chain}")

# Resilient HTTP клиент с circuit breaker
client = ResilientHTTPClient(
    provider_name="openai",
    timeout=30.0,
    max_retries=3
)

response = await client.post(
    url="https://api.openai.com/v1/chat/completions",
    json={"model": "gpt-4", "messages": [...]},
    headers={"Authorization": f"Bearer {api_key}"},
    idempotency_key="req-unique-id"
)
```

### REST API

```bash
# Health check
curl http://localhost:8000/health

# Получение оценки стоимости
curl -X POST http://localhost:8000/api/v1/estimate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_tokens": 1500,
    "output_tokens": 500,
    "strategy": "cost_optimized",
    "modality": "text"
  }'

# Обработка запроса
curl -X POST http://localhost:8000/api/v1/request \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a haiku about AI",
    "strategy": "balanced"
  }'
```

---

## 📊 Мониторинг

### Метрики (Prometheus)

```bash
# Запуск Prometheus через docker-compose
docker-compose up -d prometheus

# Открыть Prometheus UI
open http://localhost:9090

# Примеры запросов (PromQL):
# Request rate
rate(http_requests_total[5m])

# Average latency
rate(http_request_duration_seconds_sum[5m]) / 
rate(http_request_duration_seconds_count[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) / 
sum(rate(http_requests_total[5m]))

# Circuit breaker status
circuit_breaker_state{provider="openai"}
```

### Dashboards (Grafana)

```bash
# Запуск Grafana через docker-compose
docker-compose up -d grafana

# Открыть Grafana (admin/admin)
open http://localhost:3000

# Готовые дашборды для импорта:
# - FastAPI: ID 11713
# - PostgreSQL: ID 9628
# - Redis: ID 11835

# 🚧 Custom дашборды в разработке
```

### Distributed Tracing (Jaeger) — 🚧 In Progress

```bash
# Включить в .env
ENABLE_TRACING=true
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# Запуск Jaeger (требует дополнительную настройку)
docker run -d --name jaeger \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Открыть Jaeger UI
open http://localhost:16686
```

---

## 🧪 Тестирование

```bash
# Все unit тесты
pytest tests/

# С coverage
pytest --cov=src --cov-report=html tests/

# Property-based тесты
pytest tests/test_pricing_property.py -v

# Integration тесты (требуют запущенные сервисы)
docker-compose up -d postgres redis
pytest tests/integration/ -v

# Через Makefile:
make test              # Все тесты
make test-coverage     # С coverage report
make test-property     # Property-based
```

### Текущее покрытие

```
Name                           Stmts   Miss  Cover
--------------------------------------------------
src/pricing_v2.py               234     28    88%
src/middleware/circuit_breaker  156     35    78%
src/api/routes.py               189     42    78%
src/models/                     142     18    87%
--------------------------------------------------
TOTAL                          1247    247    80%
```

---

## 📚 Документация

- **[config/README.md](config/README.md)** - Документация по конфигурации провайдеров
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Полное руководство по развёртыванию
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Чеклист перед релизом
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Сводка изменений
- **[API Docs](http://localhost:8000/docs)** - OpenAPI/Swagger документация
- **[ReDoc](http://localhost:8000/redoc)** - Alternative API documentation

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────┐
│          Client Applications            │
│   (Web, Mobile, CLI, Python SDK)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         FastAPI Application             │
│  ┌────────────────────────────────────┐ │
│  │  Security Middleware               │ │
│  │  (CORS, Headers, Size Limits)      │ │
│  ├────────────────────────────────────┤ │
│  │  Authentication                    │ │
│  │  (JWT, API Keys)                   │ │
│  ├────────────────────────────────────┤ │
│  │  Intelligent Router                │ │
│  │  (Cost/Latency/Quality)            │ │
│  ├────────────────────────────────────┤ │
│  │  Circuit Breaker & Retry           │ │
│  ├────────────────────────────────────┤ │
│  │  Pricing Engine                    │ │
│  │  (Token-based billing)             │ │
│  └────────────────────────────────────┘ │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      AI Providers (with Fallbacks)      │
│  ┌────────┐ ┌──────────┐ ┌───────────┐ │
│  │ OpenAI │ │Anthropic │ │Stability  │ │
│  └────────┘ └──────────┘ └───────────┘ │
└─────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Data & Monitoring               │
│  ┌────────┐ ┌───────┐ ┌──────────────┐ │
│  │Postgres│ │ Redis │ │  Prometheus  │ │
│  └────────┘ └───────┘ └──────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🔐 Безопасность

### Встроенная защита

- **Authentication**: JWT tokens + API keys
- **Authorization**: Role-based access control (🚧 базовая реализация)
- **Rate Limiting**: 60 req/min, 1000 req/hour (настраивается)
- **Input Validation**: Pydantic models с strict validation
- **SQL Injection**: SQLAlchemy ORM
- **XSS Protection**: Security headers
- **Secrets Management**: Rotation + grace period (🚧 в тестировании)

### Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

### Проверка безопасности

```bash
# Security audit с bandit
bandit -r src/ -f json -o security-report.json

# Dependency audit
pip-audit

# Container scanning (если установлен Trivy)
trivy image oneflow-ai:0.1.0

# Через Makefile:
make security-check
make audit
```

---

## 💰 Ценообразование

### Поддерживаемые модели

| Модель | Input ($/1M tokens) | Output ($/1M tokens) | Credits/1K tokens (≈) |
|--------|---------------------|----------------------|-------------------|
| GPT-4o | $2.50 | $10.00 | 0.25 - 1.00 |
| GPT-4 Turbo | $10.00 | $30.00 | 1.00 - 3.00 |
| GPT-4 | $30.00 | $60.00 | 3.00 - 6.00 |
| GPT-3.5-turbo | $0.50 | $1.50 | 0.05 - 0.15 |
| Claude 3 Opus | $15.00 | $75.00 | 1.50 - 7.50 |
| Claude 3 Sonnet | $3.00 | $15.00 | 0.30 - 1.50 |
| Claude 3 Haiku | $0.25 | $1.25 | 0.03 - 0.13 |

*Цены актуальны на январь 2025 и могут изменяться провайдерами*

### Пример расчёта

```python
# GPT-4: 1500 input + 500 output токенов
input_cost = (1500 / 1_000_000) * 30.00 = $0.045
output_cost = (500 / 1_000_000) * 60.00 = $0.030
total_usd = $0.075
credits = 0.075 * 100 = 7.5 credits
```

Подробная конфигурация ценообразования находится в `config/config.json`. См. [config/README.md](config/README.md).

---

## 📈 Performance & Observability

### SLI/SLO Targets (Beta Goals)

Во время бета‑фазы мы собираем реальные метрики и формируем целевые уровни обслуживания (SLO).  Таблица ниже отражает **ожидаемые** цели, а не фактические показатели production окружения.

| Метрика | Цель (Beta) | Статус | Комментарий |
|---------|-------------|--------|-------------|
| **Доступность** | ≥ 95% | 🚧 Measuring | Повышается за счёт fallback‑ов; цель уточняется по мере накопления данных |
| **Latency p95** | < 2s | 🚧 Measuring | Время ответа для 95% запросов; зависит от провайдера |
| **Latency p99** | < 5s | 🚧 Measuring | Время ответа для 99% запросов |
| **Ошибка 5xx** | < 1% | 🚧 Measuring | Доля запросов, завершившихся ошибкой сервера |
| **Throughput** | 100-500 req/s | 🚧 Tuning | Для single‑node; масштабирование возможно через horizontal scaling |

> **Note:** Эти цели будут уточнены после накопления статистики в production-like окружении. Фактическая производительность сильно зависит от инфраструктуры и нагрузки.

### Наблюдаемость

Проект интегрирован с Prometheus для сбора метрик. Grafana dashboards и OpenTelemetry трассировка находятся в стадии активной разработки.  В каталоге `monitoring/` можно найти примеры конфигураций.  

**Рекомендуется проводить собственные нагрузочные тесты** в целевом окружении (например, с помощью k6, Locust, или Apache Bench), поскольку результаты сильно зависят от инфраструктуры.

```bash
# Пример нагрузочного теста с k6
k6 run --vus 10 --duration 30s tests/load/scenario.js
```

---

## 🛠️ Makefile команды

### Development

```bash
make install          # Установка зависимостей
make install-dev      # Установка с dev dependencies
make dev              # Запуск dev сервера (uvicorn с reload)
make test             # Запуск всех тестов
make test-coverage    # Тесты с coverage
make lint             # Проверка кода (flake8, black --check)
make format           # Форматирование кода (black, isort)
make type-check       # Проверка типов (mypy)
```

### Docker

```bash
make docker-build     # Сборка образа
make docker-up        # Запуск всех сервисов
make docker-down      # Остановка сервисов
make docker-logs      # Просмотр логов
make docker-restart   # Перезапуск приложения
make docker-shell     # Shell в контейнере
make docker-clean     # Очистка volumes и images
```

### Kubernetes (Experimental)

```bash
make k8s-deploy       # Развёртывание в K8s
make k8s-delete       # Удаление ресурсов
make k8s-status       # Статус deployment
make k8s-logs         # Логи подов
make k8s-port-forward # Port forward на localhost
```

### Database

```bash
make db-migrate       # Применить миграции (alembic upgrade head)
make db-rollback      # Откатить миграцию
make db-reset         # Сброс БД (ОПАСНО! Удаляет все данные)
make db-shell         # PostgreSQL shell (psql)
```

### Configuration

```bash
make config-validate  # Валидация config.json против схемы
make config-check-env # Проверка environment variables
```

### Monitoring

```bash
make prometheus       # Открыть Prometheus UI
make grafana          # Открыть Grafana UI
make jaeger           # Открыть Jaeger UI (требует настройку)
```

### Maintenance

```bash
make clean            # Очистка временных файлов (__pycache__, .pytest_cache)
make clean-all        # Полная очистка (включая .venv, volumes)
make security-check   # Проверка безопасности (bandit)
make audit            # Аудит зависимостей (pip-audit)
make prod-check       # Все проверки перед prod (lint+test+security)
make prod-build       # Сборка production образа
```

---

## 🌍 Окружения

### Development

```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://oneflow:password@localhost:5432/oneflow_dev
REDIS_URL=redis://localhost:6379/0
ENABLE_METRICS=true
ENABLE_TRACING=false
```

### Staging

```bash
ENVIRONMENT=staging
LOG_LEVEL=INFO
DATABASE_URL=postgresql://oneflow:password@staging-db:5432/oneflow_staging
REDIS_URL=redis://staging-redis:6379/0
ENABLE_TRACING=true
ENABLE_METRICS=true
```

### Production

```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://oneflow:secure_password@prod-db:5432/oneflow_prod
REDIS_URL=redis://prod-redis:6379/0
ENABLE_METRICS=true
ENABLE_TRACING=true
DATABASE_POOL_SIZE=30
DATABASE_MAX_OVERFLOW=10
```

---

## 🔄 CI/CD Pipeline (Planned)

### GitHub Actions (Coming Soon)

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: make test-coverage
      - name: Security check
        run: make security-check
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: make docker-build
      - name: Push to registry
        run: docker push oneflow-ai:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to K8s
        run: kubectl set image deployment/oneflow-ai oneflow-ai=oneflow-ai:${{ github.sha }}
```

---

## 🐛 Troubleshooting

### Проблема: API не отвечает

```bash
# Проверить логи
docker-compose logs -f oneflow-ai

# Проверить health
curl http://localhost:8000/health

# Проверить readiness
curl http://localhost:8000/ready

# Перезапустить
docker-compose restart oneflow-ai
```

### Проблема: High latency

```bash
# Проверить метрики
curl http://localhost:8000/metrics | grep http_request_duration

# Проверить circuit breaker
curl http://localhost:8000/metrics | grep circuit_breaker_state

# Проверить статус сервисов
docker-compose ps

# Увеличить timeout в .env
HTTP_TIMEOUT=60
```

### Проблема: Database connection errors

```bash
# Проверить PostgreSQL
docker-compose exec postgres psql -U oneflow -d oneflow_dev

# Проверить connection pool
curl http://localhost:8000/metrics | grep db_pool

# Проверить миграции
alembic current
alembic history

# Увеличить pool size в .env
DATABASE_POOL_SIZE=30
DATABASE_MAX_OVERFLOW=10
```

### Проблема: Circuit breaker открывается слишком часто

```bash
# Проверить метрики ошибок провайдера
curl http://localhost:8000/metrics | grep provider_errors

# Увеличить failure threshold в config/config.json
{
  "retries": {
    "max_attempts": 5
  }
}
```

### Проблема: Неправильная конфигурация провайдеров

```bash
# Валидация конфигурации
make config-validate

# Проверка environment variables
make config-check-env

# Просмотр актуальной конфигурации
cat config/config.json
```

---

## 📞 Поддержка

### Документация

- 📖 [Provider Configuration](config/README.md)
- 📖 [Deployment Guide](DEPLOYMENT.md)
- ✅ [Production Checklist](PRODUCTION_CHECKLIST.md)
- 📝 [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
- 🔧 [API Reference](http://localhost:8000/docs)

### Контакты

- **Email**: voroninsergeiai@gmail.com
- **GitHub**: [@voroninsergei](https://github.com/voroninsergei)
- **Issues**: [GitHub Issues](https://github.com/voroninsergei/oneflow-ai/issues)

### Коммьюнити

- 💬 Задать вопрос: [Discussions](https://github.com/voroninsergei/oneflow-ai/discussions)
- 🐛 Сообщить о баге: [Issues](https://github.com/voroninsergei/oneflow-ai/issues)
- 🎉 Предложить feature: [Feature Requests](https://github.com/voroninsergei/oneflow-ai/discussions/categories/ideas)

---

## 🤝 Contributing

Мы приветствуем вклад в проект! Пожалуйста:

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Code Style

```bash
# Перед коммитом
make format       # Black + isort
make lint         # Flake8
make type-check   # Mypy
make test         # Pytest

# Или все сразу:
make prod-check
```

### Требования к PR

- ✅ Все тесты проходят
- ✅ Coverage не снижается
- ✅ Код отформатирован (black, isort)
- ✅ Нет warnings от flake8 и mypy
- ✅ Добавлены тесты для новой функциональности
- ✅ Обновлена документация

---

## 📜 License

Proprietary License - Copyright (c) 2025 Sergey Voronin. All rights reserved.

See [LICENSE](LICENSE) file for details.

---

## 🙏 Благодарности

Построено с использованием:

- **FastAPI** - Modern web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **Prometheus** - Monitoring and alerting
- **OpenTelemetry** - Observability framework
- **Kubernetes** - Container orchestration
- **Docker** - Containerization
- **PostgreSQL** - Relational database
- **Redis** - In-memory data store

---

## 📊 Статистика проекта

```
┌─────────────────────────────────────────┐
│  Project Status:        Beta Preview    │
│  Version:               0.1.0            │
├─────────────────────────────────────────┤
│  👀 Observability:       🚧 In Progress  │
│  🔧 Reliability:         ✅ Core Ready    │
│  🔒 Security:            ✅ First‑class   │
│  🚀 Performance:         🚧 Tuning       │
│  🏗️ Infrastructure:      ✅ Docker Ready  │
│  ☸️  Kubernetes:         🚧 Experimental │
├─────────────────────────────────────────┤
│  📝 Files:               50+             │
│  🧪 Test Coverage:       ~80%            │
│  📚 Documentation:       Extensive       │
│  🐳 Docker:              ✅ Supported     │
│  🔄 CI/CD:               🚧 Planned       │
└─────────────────────────────────────────┘
```

### Legend
- ✅ **Ready**: Функциональность реализована и протестирована
- 🚧 **In Progress**: Активная разработка или настройка
- 🔮 **Planned**: Запланировано на будущее

---

**Made with ❤️ by Sergey Voronin**

*OneFlow.AI - Simplifying AI Model Integration since 2025*
