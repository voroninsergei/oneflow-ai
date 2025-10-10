# OneFlow.AI - Docker Compose

## 🚀 Быстрый старт

### Минимальная конфигурация (только приложение)
```bash
# Запуск приложения с Redis и PostgreSQL
docker-compose up -d
```

### Полная конфигурация (с мониторингом)
```bash
# Запуск всех сервисов
docker-compose --profile full up -d
```

### Выборочный запуск

**Только база данных:**
```bash
docker-compose --profile db up -d
```

**С мониторингом:**
```bash
docker-compose --profile monitoring up -d
```

**С трейсингом:**
```bash
docker-compose --profile tracing up -d
```

**Комбинация профилей:**
```bash
docker-compose --profile db --profile monitoring up -d
```

## 📋 Доступные профили

| Профиль | Сервисы | Описание |
|---------|---------|----------|
| `(default)` | app, postgres, redis | Минимальная конфигурация для разработки |
| `full` | все сервисы | Полный стек с мониторингом и трейсингом |
| `db` | postgres, pgadmin | Только база данных и админка |
| `monitoring` | prometheus, grafana | Метрики и дашборды |
| `tracing` | jaeger | Распределенный трейсинг |

## 🔧 Настройка

### 1. Создайте файлы окружения

Скопируйте шаблоны и заполните значения:

```bash
cp .env.example .env
cp .env.postgres.example .env.postgres
cp .env.redis.example .env.redis
cp .env.grafana.example .env.grafana
cp .env.pgadmin.example .env.pgadmin
```

### 2. Настройте секреты

**Для разработки:**
- Используйте значения по умолчанию из примеров

**Для продакшена:**
- Сгенерируйте случайные пароли
- Используйте Docker Secrets или переменные окружения

```bash
# Генерация JWT секрета
openssl rand -hex 32

# Генерация паролей
openssl rand -base64 32
```

### 3. Создайте необходимые директории

```bash
mkdir -p logs backups monitoring/{prometheus,grafana/{dashboards,datasources}}
```

## 🌐 Доступ к сервисам

| Сервис | URL | Credentials |
|--------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **Swagger** | http://localhost:8000/docs | - |
| **PostgreSQL** | localhost:5432 | oneflow / oneflow_password |
| **Redis** | localhost:6379 | password: redis_password |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **Jaeger UI** | http://localhost:16686 | - |
| **pgAdmin** | http://localhost:5050 | admin@oneflow.ai / admin |

## 📊 Мониторинг

### Prometheus

Метрики доступны на `http://localhost:9090`

Основные метрики приложения:
- `http_requests_total` - количество HTTP запросов
- `http_request_duration_seconds` - длительность запросов
- `app_errors_total` - количество ошибок

### Grafana

Дашборды доступны на `http://localhost:3000`

Предустановленные дашборды:
- Application Overview
- API Performance
- Database Metrics
- Redis Metrics

### Jaeger

Трейсы доступны на `http://localhost:16686`

## 🔍 Управление

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f app

# Последние N строк
docker-compose logs --tail=100 app
```

### Проверка состояния

```bash
# Статус всех контейнеров
docker-compose ps

# Проверка здоровья
docker-compose ps --format json | jq '.[].Health'
```

### Рестарт сервисов

```bash
# Все сервисы
docker-compose restart

# Конкретный сервис
docker-compose restart app
```

### Обновление

```bash
# Пересборка с обновлением
docker-compose build --no-cache
docker-compose up -d

# Обновление образов
docker-compose pull
docker-compose up -d
```

## 💾 Резервное копирование

### PostgreSQL

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U oneflow oneflow > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление
docker-compose exec -T postgres psql -U oneflow oneflow < backups/backup_20250101_120000.sql
```

### Redis

```bash
# Создание снапшота
docker-compose exec redis redis-cli --no-auth-warning -a redis_password SAVE

# Копирование RDB файла
docker cp oneflow-redis:/data/dump.rdb backups/redis_$(date +%Y%m%d_%H%M%S).rdb
```

## 🧹 Очистка

### Остановка и удаление контейнеров

```bash
# Остановка
docker-compose down

# Остановка с удалением volume
docker-compose down -v

# Полная очистка (включая образы)
docker-compose down -v --rmi all
```

### Очистка только данных

```bash
# Удаление конкретного volume
docker volume rm oneflow_postgres_data

# Удаление всех volume проекта
docker volume ls -q -f name=oneflow | xargs docker volume rm
```

## 🔒 Безопасность

### Для продакшена обязательно:

1. **Смените все пароли по умолчанию**
   - PostgreSQL: `POSTGRES_PASSWORD`
   - Redis: `REDIS_PASSWORD`
   - Grafana: `GF_SECURITY_ADMIN_PASSWORD`
   - JWT: `JWT_SECRET`

2. **Используйте HTTPS**
   - Настройте reverse proxy (nginx/traefik)
   - Получите SSL сертификаты

3. **Ограничьте доступ к портам**
   - Не expose порты БД в интернет
   - Используйте firewall

4. **Настройте лимиты ресурсов**
   - Уже настроены в `deploy.resources`
   - Отрегулируйте под ваше железо

5. **Регулярные бэкапы**
   - Настройте автоматическое резервное копирование
   - Храните бэкапы в безопасном месте

## 🐛 Troubleshooting

### Контейнер не стартует

```bash
# Проверка логов
docker-compose logs app

# Проверка healthcheck
docker inspect oneflow-ai-app | jq '.[0].State.Health'
```

### Проблемы с зависимостями

```bash
# Пересоздание контейнеров
docker-compose up -d --force-recreate

# Проверка сети
docker network inspect oneflow_network
```

### База данных не доступна

```bash
# Проверка PostgreSQL
docker-compose exec postgres pg_isready -U oneflow

# Подключение к БД
docker-compose exec postgres psql -U oneflow -d oneflow
```

### Redis проблемы

```bash
# Проверка Redis
docker-compose exec redis redis-cli --no-auth-warning -a redis_password ping

# Просмотр конфигурации
docker-compose exec redis redis-cli --no-auth-warning -a redis_password CONFIG GET '*'
```

## 📝 Переменные окружения

### Основные переменные (.env)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `ENVIRONMENT` | Окружение (development/production) | development |
| `LOG_LEVEL` | Уровень логирования | INFO |
| `APP_PORT` | Порт приложения | 8000 |
| `DATABASE_URL` | URL подключения к БД | - |
| `REDIS_URL` | URL подключения к Redis | - |
| `JWT_SECRET` | Секрет для JWT токенов | - |
| `ENABLE_METRICS` | Включить метрики | true |
| `ENABLE_TRACING` | Включить трейсинг | false |

### Настройка портов

Все порты можно переопределить через переменные окружения:

```bash
APP_PORT=8080
POSTGRES_PORT=5433
REDIS_PORT=6380
GRAFANA_PORT=3001
PROMETHEUS_PORT=9091
JAEGER_UI_PORT=16687
PGADMIN_PORT=5051
```

## 📚 Дополнительные ресурсы

- [Docker Compose документация](https://docs.docker.com/compose/)
- [Best practices для production](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL в Docker](https://hub.docker.com/_/postgres)
- [Redis в Docker](https://hub.docker.com/_/redis)