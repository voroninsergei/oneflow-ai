# ⚡ Быстрое руководство по внедрению изменений

## 📋 Что нужно сделать

Все файлы разделены на **3 категории** по приоритету.

---

## 🔴 КРИТИЧНО - Внедрить немедленно (День 1)

### 1. Создать новые файлы

Скопируйте эти файлы **как есть** в указанные места:

```bash
# Инфраструктура
Dockerfile                          # В корень проекта
.dockerignore                       # В корень проекта
docker-compose.yml                  # В корень проекта
.env.example                        # В корень проекта

# Kubernetes
mkdir -p k8s/
k8s/deployment.yaml                 # Создать файл

# Monitoring
mkdir -p monitoring/
monitoring/prometheus.yml           # Создать файл
```

### 2. Обновить существующие файлы

**⚠️ ВАЖНО: Сделайте backup перед заменой!**

```bash
# Backup
cp web_server.py web_server.py.backup
cp requirements.txt requirements.txt.backup

# Замените эти файлы
web_server.py                       # ПОЛНОСТЬЮ ЗАМЕНИТЬ
requirements.txt                    # ПОЛНОСТЬЮ ЗАМЕНИТЬ
```

### 3. Создать .env файл

```bash
cp .env.example .env

# Добавить обязательные значения:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - JWT_SECRET (openssl rand -hex 32)
# - DATABASE_URL
# - REDIS_URL
```

---

## 🟡 ВАЖНО - Внедрить в течение недели (Неделя 1)

### 4. Новые модули

Создайте эти файлы в соответствующих директориях:

```bash
# Middleware
mkdir -p src/middleware/
src/middleware/__init__.py          # Пустой файл
src/middleware/circuit_breaker.py   # Скопировать код

# Обновлённые модули
src/pricing_v2.py                   # Новый файл (не заменяет pricing.py!)
src/auth_v2.py                      # Новый файл (не заменяет auth_module.py!)
```

### 5. Тесты

```bash
# Property-based тесты
tests/test_pricing_properties.py    # Создать файл

# Запустить тесты
make test-property
```

### 6. Скрипты

```bash
mkdir -p scripts/

# Health check
scripts/health_check.sh             # Создать файл
chmod +x scripts/health_check.sh

# Key rotation
scripts/rotate_api_keys.py          # Создать файл
chmod +x scripts/rotate_api_keys.py
```

---

## 🟢 ОПЦИОНАЛЬНО - Внедрить по мере необходимости

### 7. Документация

```bash
DEPLOYMENT.md                       # Справочное руководство
PRODUCTION_CHECKLIST.md             # Чеклист перед релизом
IMPLEMENTATION_SUMMARY.md           # Сводка изменений
README.md                           # Обновлённый README
```

### 8. Утилиты

```bash
Makefile                            # Удобные команды
```

---

## 🔧 Пошаговая интеграция

### Шаг 1: Подготовка (30 минут)

```bash
# 1. Создайте backup
git checkout -b production-ready-backup
git add .
git commit -m "Backup before production updates"

# 2. Создайте новую ветку
git checkout -b feature/production-ready

# 3. Создайте необходимые директории
mkdir -p k8s/ monitoring/ scripts/ src/middleware/
```

### Шаг 2: Критические файлы (1 час)

```bash
# 1. Скопируйте файлы инфраструктуры
# Dockerfile, .dockerignore, docker-compose.yml, .env.example

# 2. Обновите зависимости
cp requirements.txt requirements.txt.backup
# Замените requirements.txt новым

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Создайте .env
cp .env.example .env
nano .env  # Добавьте ваши API ключи
```

### Шаг 3: Обновление web_server.py (30 минут)

**Вариант A: Постепенная интеграция (рекомендуется)**

```python
# В вашем текущем web_server.py добавьте:

# 1. Импорты для observability
from prometheus_fastapi_instrumentator import Instrumentator
import structlog

# 2. Middleware
from web_server import SecurityHeadersMiddleware  # из нового файла

app.add_middleware(SecurityHeadersMiddleware)

# 3. Prometheus
@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

**Вариант B: Полная замена**

```bash
# Backup
cp web_server.py web_server.py.backup

# Замените файл полностью
# Затем перенесите ваши существующие endpoints в новый файл
```

### Шаг 4: Новые модули (1 час)

```bash
# 1. Circuit breaker
# Скопируйте src/middleware/circuit_breaker.py

# 2. Pricing v2
# Скопируйте src/pricing_v2.py

# 3. Auth v2
# Скопируйте src/auth_v2.py

# 4. Тесты
# Скопируйте tests/test_pricing_properties.py

# 5. Запустите тесты
pytest tests/ -v
```

### Шаг 5: Docker (30 минут)

```bash
# 1. Сборка образа
docker build -t oneflow-ai:2.0.0 .

# 2. Тест запуска
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./oneflow.db \
  -e REDIS_URL=redis://localhost:6379/0 \
  oneflow-ai:2.0.0

# 3. Проверка health
curl http://localhost:8000/health
```

### Шаг 6: Docker Compose (15 минут)

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка
docker-compose ps
docker-compose logs -f app

# Health check
./scripts/health_check.sh
```

### Шаг 7: Kubernetes (опционально, 1 час)

```bash
# 1. Создайте secrets
kubectl create namespace oneflow-ai

kubectl create secret generic oneflow-secrets \
  --namespace=oneflow-ai \
  --from-literal=JWT_SECRET=$(openssl rand -hex 32) \
  --from-file=.env

# 2. Развёртывание
kubectl apply -f k8s/deployment.yaml

# 3. Проверка
kubectl get pods -n oneflow-ai
kubectl logs -f deployment/oneflow-ai -n oneflow-ai
```

---

## ✅ Проверка работоспособности

### После внедрения выполните:

```bash
# 1. Health checks
curl http://localhost:8000/health
curl http://localhost:8000/ready

# 2. Metrics
curl http://localhost:8000/metrics

# 3. API документация
open http://localhost:8000/docs

# 4. Полный health check
./scripts/health_check.sh

# 5. Тесты
make test

# 6. Property тесты
make test-property
```

---

## 🔄 Миграция существующей логики

### Если у вас есть существующий код:

#### 1. Pricing

```python
# Старый код (src/pricing.py)
cost = calculate_cost(word_count)

# Новый код (src/pricing_v2.py)
from pricing_v2 import PricingEngine, ProviderModel

engine = PricingEngine()
cost = engine.estimate_cost(
    model=ProviderModel.GPT_4,
    input_tokens=input_tokens,
    output_tokens=output_tokens
)
```

#### 2. Provider calls

```python
# Старый код
response = requests.post(url, json=data, headers=headers)

# Новый код
from middleware.circuit_breaker import ResilientHTTPClient

client = ResilientHTTPClient(provider_name="openai")
response = await client.post(
    url=url,
    json=data,
    headers=headers,
    idempotency_key="req-123"
)
```

#### 3. Authentication

```python
# Старый код
from auth_module import verify_token

# Новый код (постепенно мигрируйте)
from auth_v2 import JWTManager, APIKeyManager

jwt_manager = JWTManager(secret_key=settings.JWT_SECRET)
payload = jwt_manager.verify_token(token)
```

---

## 🚨 Частые проблемы и решения

### Проблема 1: ImportError при старте

```bash
# Решение: Переустановите зависимости
pip install --upgrade -r requirements.txt
pip install -e .
```

### Проблема 2: Database connection error

```bash
# Решение: Проверьте DATABASE_URL в .env
# Для локального теста используйте SQLite:
DATABASE_URL=sqlite:///./oneflow.db
```

### Проблема 3: Redis connection error

```bash
# Решение: Запустите Redis через docker-compose
docker-compose up -d redis

# Или используйте mock для разработки
REDIS_URL=redis://localhost:6379/0
```

### Проблема 4: Prometheus metrics не работают

```bash
# Решение: Проверьте, установлен ли instrumentator
pip install prometheus-fastapi-instrumentator

# Проверьте .env
ENABLE_METRICS=true
```

---

## 📊 Чеклист внедрения

Отмечайте по мере выполнения:

**Критично (День 1):**
- [ ] Dockerfile создан
- [ ] .dockerignore создан
- [ ] docker-compose.yml создан
- [ ] .env файл создан и заполнен
- [ ] requirements.txt обновлён
- [ ] web_server.py обновлён
- [ ] Docker образ собирается
- [ ] Приложение запускается

**Важно (Неделя 1):**
- [ ] src/middleware/circuit_breaker.py создан
- [ ] src/pricing_v2.py создан
- [ ] src/auth_v2.py создан
- [ ] tests/test_pricing_properties.py создан
- [ ] scripts/health_check.sh создан
- [ ] scripts/rotate_api_keys.py создан
- [ ] Makefile создан
- [ ] Все тесты проходят

**Опционально:**
- [ ] k8s/deployment.yaml создан
- [ ] Prometheus настроен
- [ ] Grafana настроена
- [ ] Документация обновлена
- [ ] CI/CD pipeline настроен

---

## 💡 Советы

1. **Не торопитесь** - внедряйте постепенно
2. **Тестируйте каждый шаг** - запускайте тесты после каждого изменения
3. **Делайте backup** - перед каждым изменением
4. **Используйте feature branches** - не коммитьте сразу в main
5. **Документируйте проблемы** - записывайте, что не работает
6. **Просите помощь** - если что-то непонятно

---

## 📞 Получить помощь

Если возникли проблемы:

1. **Проверьте логи**: `docker-compose logs -f app`
2. **Запустите health check**: `./scripts/health_check.sh`
3. **Проверьте документацию**: `DEPLOYMENT.md`
4. **Откройте issue**: GitHub Issues
5. **Напишите email**: voroninsergeiai@gmail.com

---

**Удачи с внедрением! 🚀**
