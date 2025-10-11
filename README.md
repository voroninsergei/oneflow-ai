# OneFlow.AI v0.1.0 – Beta Preview 🚧

> **Note:** This project is currently in **beta**. While many of the building blocks for a production-grade system are in place, we are still collecting real-world telemetry and iterating on the architecture. Please treat it as a preview rather than a finished, battle-hardened product.

> Enterprise-grade AI Model Aggregator с маршрутизацией, ценообразованием, аналитикой и полной observability

[![Status](https://img.shields.io/badge/status-beta-yellow)](/)
[![Test Coverage](https://img.shields.io/badge/coverage-~80%25-brightgreen)](/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-experimental-lightblue)](/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](/)

---

## 🎯 Что это?

OneFlow.AI — это **ценовой и маршрутизирующий слой** для AI-моделей. Он предоставляет общую точку входа к нескольким провайдерам искусственного интеллекта, оценивает стоимость запроса по числу токенов, выбирает наиболее подходящую модель и обеспечивает мониторинг и безопасность.

**Ключевые возможности:**
- 🔀 **Автоматически выбирает** оптимальную модель (цена/скорость/качество)
- 💰 **Прозрачное ценообразование** на основе токенов с нормализацией к кредитам
- 🔄 **Умные fallback** при недоступности провайдеров
- 📊 **Детальная аналитика** использования и затрат
- 🔐 **Enterprise security** с JWT, API keys rotation, CORS
- 📈 **Observability** с Prometheus, Grafana, OpenTelemetry

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

### 💎 Реализованные возможности

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
- Quotas per-user/per-provider/per-project (🚧 в тестировании)

✅ **Security**
- JWT authentication + refresh tokens
- API keys с автоматической ротацией (🚧 тестируется grace period)
- Security headers (HSTS, CSP, X-Frame-Options)
- Request size limits (10MB)
- Secrets sanitization в логах
- Rate limiting (60/min, 1000/hour) — базовая реализация

✅ **Smart Routing**
- Cost-optimized: минимальная стоимость
- Latency-optimized: максимальная скорость
- Quality-optimized: лучшее качество
- Balanced: оптимальный баланс

✅ **Token-Based Billing**
- Точный расчёт входящих и исходящих токенов для каждого запроса
- Нормализация стоимости к кредитам (по умолчанию 1 USD = 100 кредитов)
- Поддержка нескольких провайдеров и моделей
- Property-based тесты (Hypothesis)

> Стоимость запроса вычисляется в модуле `pricing_v2.py`. Этот модуль оперирует токенами (не словами) и учитывает различную стоимость входящих и исходящих токенов для каждого провайдера. Подробнее см. [src/pricing_v2.py](src/pricing_v2.py).

---

## 🚀 Быстрый старт

> 📖 **Детальная документация по развёртыванию:** См. [DEPLOYMENT.md](DEPLOYMENT.md) для полного руководства по установке и настройке во всех окружениях.

### Предварительные требования

- **Python 3.11+** (tested on 3.11, 3.12)
- Docker 20.10+ и Docker Compose 2.0+
- PostgreSQL 14+ (или используйте docker-compose)
- Redis 7+ (или используйте docker-compose)

### Локальная разработка

```bash
# 1. Клонирование репозитория
git clone https://github.com/voroninsergei/oneflow-ai.git
cd oneflow-ai

# 2. Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# 3. Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Для разработки

# 4. Конфигурация
cp .env.example .env
nano .env  # Добавить API ключи провайдеров

# 5. Запуск зависимостей
docker-compose up -d postgres redis

# 6. Применение миграций
alembic upgrade head

# 7. Запуск development сервера
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
# Или: make dev

# 8. Открыть API документацию
open http://localhost:8000/docs
```

### Docker развёртывание

```bash
# Сборка образа
docker build -t oneflow-ai:0.1.0 .
# Или: make docker-build

# Запуск полного stack
docker-compose up -d

# Проверка здоровья
./scripts/health_check.sh

# Просмотр метрик
open http://localhost:8000/metrics
```

### Kubernetes развёртывание (Experimental)

> **Warning:** Kubernetes конфигурация находится в экспериментальной стадии. Перед использованием требуется дополнительная настройка StatefulSets, PVC, и ingress. См. [DEPLOYMENT.md](DEPLOYMENT.md) для деталей.

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

# Documentation
http://localhost:8000/docs    # Swagger UI
http://localhost:8000/redoc   # ReDoc
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

> 📖 **Полная документация по мониторингу:** См. [DEPLOYMENT.md](DEPLOYMENT.md) раздел "Monitoring & Observability"

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

- **[QUICKSTART.md](QUICKSTART.md)** - Быстрое начало работы (если есть)
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

---

## 📈 Performance & Observability

### Целевые показатели (Beta Goals)

Во время бета-фазы мы собираем реальные метрики для формирования целевых уровней обслуживания (SLO). Таблица ниже отражает **предварительные цели**, которые будут уточняться по мере накопления статистики.

| Метрика | Целевое значение | Текущий статус | Комментарий |
|---------|------------------|----------------|-------------|
| **Доступность** | ≥ 95% | 🚧 Измеряется | Улучшается за счёт fallback-механизмов |
| **Latency p95** | < 2s | 🚧 Измеряется | Зависит от выбранного провайдера |
| **Latency p99** | < 5s | 🚧 Измеряется | Время ответа для 99% запросов |
| **Ошибка 5xx** | < 1% | 🚧 Измеряется | Доля серверных ошибок |
| **Throughput** | 100-500 req/s | 🚧 Настраивается | Single-node; масштабируется горизонтально |

> **Note:** Эти цели будут уточнены после накопления статистики. Фактическая производительность сильно зависит от инфраструктуры, нагрузки и выбранных провайдеров. **Рекомендуется проводить собственные нагрузочные тесты** в целевом окружении.

### Нагрузочное тестирование

```bash
# Пример нагрузочного теста с k6
k6 run --vus 10 --duration 30s tests/load/scenario.js

# С помощью Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# С помощью Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000
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

# Увеличить failure threshold в .env
CIRCUIT_BREAKER_FAILURE_THRESHOLD=10

# Увеличить timeout window
CIRCUIT_BREAKER_TIMEOUT=120
```

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

## 📞 Поддержка

### Документация

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
│  🔒 Security:            ✅ Implemented   │
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
