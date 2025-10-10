# OneFlow.AI - Database Integration Guide
## Руководство по интеграции базы данных

---

## 🎯 Что добавлено

### 1. **Полная персистентность данных**
- ✅ История всех AI запросов
- ✅ История транзакций кошелька
- ✅ Конфигурация провайдеров
- ✅ Бюджеты и лимиты
- ✅ Поддержка множества пользователей

### 2. **Гибкая архитектура БД**
- ✅ SQLite для разработки (без установки)
- ✅ PostgreSQL для продакшена
- ✅ SQLAlchemy ORM
- ✅ Автоматическое создание таблиц

### 3. **Расширенная аналитика**
- ✅ Статистика из БД
- ✅ История операций
- ✅ Детальные отчёты

---

## 📦 Установка

### Шаг 1: Установите зависимости

```bash
pip install sqlalchemy
```

Для PostgreSQL дополнительно:
```bash
pip install psycopg2-binary
```

### Шаг 2: Сохраните файлы

1. Сохраните **Database Module** в `src/database.py`
2. Сохраните **Main Module with Database** в `src/main_with_db.py`

### Шаг 3: Структура проекта

```
OneFlow.AI/
├── src/
│   ├── database.py          # ← Новый модуль БД
│   ├── main_with_db.py      # ← Главный модуль с БД
│   ├── main.py              # Старый модуль (без БД)
│   ├── router.py
│   ├── pricing.py
│   ├── wallet.py
│   ├── analytics.py
│   ├── budget.py
│   └── ...
├── data/
│   └── oneflow.db           # ← SQLite база (создастся автоматически)
└── requirements.txt
```

---

## 🚀 Быстрый старт

### Вариант 1: SQLite (Рекомендуется для начала)

```bash
# Просто запустите - БД создастся автоматически
python -m src.main_with_db
```

База данных будет создана в `data/oneflow.db`

### Вариант 2: PostgreSQL (Для продакшена)

```python
from src.main_with_db import OneFlowAIWithDB

# Укажите URL PostgreSQL
system = OneFlowAIWithDB(
    initial_balance=100,
    database_url='postgresql://user:password@localhost:5432/oneflow'
)
```

---

## 📊 Схема базы данных

### Таблица: users
Пользователи системы
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    api_key VARCHAR(64) UNIQUE,
    balance FLOAT,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Таблица: requests
История AI запросов
```sql
CREATE TABLE requests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    provider VARCHAR(50),
    model VARCHAR(50),
    prompt TEXT,
    response TEXT,
    cost FLOAT,
    status VARCHAR(20),
    error_message TEXT,
    metadata JSON,
    created_at TIMESTAMP
);
```

### Таблица: transactions
История транзакций
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    type VARCHAR(20),           -- add, deduct, refund
    amount FLOAT,
    balance_before FLOAT,
    balance_after FLOAT,
    description VARCHAR(200),
    request_id INTEGER,
    created_at TIMESTAMP
);
```

### Таблица: provider_configs
Конфигурация провайдеров
```sql
CREATE TABLE provider_configs (
    id INTEGER PRIMARY KEY,
    provider_name VARCHAR(50) UNIQUE,
    rate_per_unit FLOAT,
    is_active BOOLEAN,
    budget_limit FLOAT,
    spent_amount FLOAT,
    metadata JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Таблица: budget_configs
Конфигурация бюджетов
```sql
CREATE TABLE budget_configs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    period VARCHAR(20),          -- daily, weekly, monthly, total
    limit_amount FLOAT,
    spent_amount FLOAT,
    reset_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 💻 Примеры использования

### Пример 1: Базовое использование

```python
from src.main_with_db import OneFlowAIWithDB

# Инициализация с SQLite (по умолчанию)
system = OneFlowAIWithDB(initial_balance=100)

# Делаем запрос (автоматически сохраняется в БД)
result = system.process_request('gpt', 'Hello world')
print(f"Request ID: {result['request_id']}")

# Получаем историю запросов
history = system.get_request_history(limit=10)
for req in history:
    print(f"{req['provider']}: {req['prompt']} - {req['status']}")
```

### Пример 2: Работа с транзакциями

```python
# Пополнить кредиты
result = system.add_credits(50, description="Monthly top-up")
print(f"New balance: {result['balance']}")

# Получить историю транзакций
transactions = system.get_transaction_history(limit=10)
for trans in transactions:
    print(f"{trans['type']}: {trans['amount']} - {trans['description']}")
```

### Пример 3: Аналитика из БД

```python
# Получить полную аналитику
analytics = system.get_database_analytics()

print(f"Total requests: {analytics['total_requests']}")
print(f"Total cost: {analytics['total_cost']}")

# Статистика по провайдерам
for provider, stats in analytics['provider_stats'].items():
    print(f"{provider}:")
    print(f"  Count: {stats['count']}")
    print(f"  Total cost: {stats['total_cost']}")
    print(f"  Success rate: {stats['success_count']/stats['count']*100:.1f}%")
```

### Пример 4: Многопользовательский режим

```python
from src.database import get_db_manager

# Создать пользователей
db = get_db_manager()
user1 = db.create_user("alice", "alice@example.com", initial_balance=100)
user2 = db.create_user("bob", "bob@example.com", initial_balance=200)

# Работа от имени Alice
system_alice = OneFlowAIWithDB(user_id=user1.id)
system_alice.process_request('gpt', 'Hello from Alice')

# Работа от имени Bob
system_bob = OneFlowAIWithDB(user_id=user2.id)
system_bob.process_request('image', 'Beautiful sunset')

# Каждый пользователь видит только свои данные
alice_history = system_alice.get_request_history()
bob_history = system_bob.get_request_history()
```

### Пример 5: Прямая работа с БД

```python
from src.database import get_db_manager

db = get_db_manager()

# Получить все запросы для провайдера
gpt_requests = db.get_requests_by_provider('gpt')
print(f"Total GPT requests: {len(gpt_requests)}")

# Получить конфигурацию провайдера
provider = db.get_provider('gpt')
print(f"GPT rate: {provider.rate_per_unit}")

# Получить статистику
total_cost = db.get_total_cost()
request_count = db.get_request_count()
print(f"Total: {request_count} requests, {total_cost} credits")
```

---

## 🔧 Интеграция с FastAPI

Обновите веб-сервер для использования БД:

```python
# В web_server.py
from src.main_with_db import OneFlowAIWithDB

# Инициализация с БД
system = OneFlowAIWithDB(
    initial_balance=1000,
    use_real_api=False,
    database_url='sqlite:///data/oneflow.db'  # или PostgreSQL URL
)

# Новый endpoint для истории
@app.get("/api/history")
async def get_history(limit: int = 20):
    """Get request history from database."""
    return {
        "requests": system.get_request_history(limit=limit),
        "transactions": system.get_transaction_history(limit=limit)
    }

# Endpoint для аналитики из БД
@app.get("/api/analytics/database")
async def get_db_analytics():
    """Get comprehensive analytics from database."""
    return system.get_database_analytics()
```

---

## 📊 Миграция данных

### Миграция из старой версии (без БД)

```python
from src.analytics import Analytics
from src.database import get_db_manager

# Загрузить старую аналитику
old_analytics = Analytics()
# (загрузить данные из JSON или другого источника)

# Мигрировать в новую БД
db = get_db_manager()

for request in old_analytics.requests:
    db.create_request(
        user_id=None,
        provider=request['provider'],
        model=request['provider'],
        prompt=request['prompt'],
        response=request['response'],
        cost=request['cost'],
        status=request['status']
    )

print("✓ Migration completed!")
```

---

## 🗄️ Управление БД

### Просмотр данных (SQLite)

```bash
# Установите sqlite3 (обычно уже установлен)
sqlite3 data/oneflow.db

# SQL команды
sqlite> SELECT * FROM users;
sqlite> SELECT * FROM requests ORDER BY created_at DESC LIMIT 10;
sqlite> SELECT provider, COUNT(*), SUM(cost) FROM requests GROUP BY provider;
sqlite> .quit
```

### Бэкап БД

```bash
# SQLite
cp data/oneflow.db data/oneflow_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump oneflow > oneflow_backup_$(date +%Y%m%d).sql
```

### Очистка БД

```python
from src.database import get_db_manager

db = get_db_manager()

# ВНИМАНИЕ: Удаляет все данные!
db.drop_all_tables()
db.create_tables()
```

---

## ⚡ Производительность

### Индексы (для больших объёмов данных)

```python
# Добавьте в database.py после определения моделей:

from sqlalchemy import Index

# Индекс для быстрого поиска по пользователю
Index('idx_requests_user_id', Request.user_id)
Index('idx_requests_created_at', Request.created_at)
Index('idx_transactions_user_id', Transaction.user_id)

# Композитный индекс
Index('idx_requests_user_provider', Request.user_id, Request.provider)
```

### Оптимизация запросов

```python
# Использование пагинации
def get_requests_paginated(page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    session = db.get_session()
    try:
        requests = session.query(Request).offset(offset).limit(per_page).all()
        return requests
    finally:
        session.close()
```

---

## 🐛 Troubleshooting

### Проблема: "Table already exists"

```python
# Пересоздайте таблицы
from src.database import get_db_manager

db = get_db_manager()
db.drop_all_tables()
db.create_tables()
```

### Проблема: "Database is locked" (SQLite)

```python
# Используйте timeout
from sqlalchemy import create_engine

engine = create_engine(
    'sqlite:///data/oneflow.db',
    connect_args={'timeout': 30}
)
```

### Проблема: PostgreSQL connection error

```python
# Проверьте строку подключения
database_url = 'postgresql://username:password@localhost:5432/dbname'

# Убедитесь, что PostgreSQL запущен
# sudo service postgresql start
```

---

## 🎓 Следующие шаги

После настройки БД можно:

1. ✅ **Запустить с БД** - использовать новый функционал
2. 🌐 **Обновить Web API** - добавить endpoints для истории
3. 📊 **Создать дашборды** - визуализация данных из БД
4. 👥 **Добавить аутентификацию** - JWT tokens для пользователей
5. 🔍 **Расширенная аналитика** - графики и отчёты

---

## ✅ Чек-лист готовности

- [ ] Установлен SQLAlchemy: `pip install sqlalchemy`
- [ ] Сохранён `src/database.py`
- [ ] Сохранён `src/main_with_db.py`
- [ ] Запущен demo: `python -m src.main_with_db`
- [ ] БД создана автоматически в `data/oneflow.db`
- [ ] Сделан тестовый запрос и проверена история
- [ ] Проверена аналитика из БД

---

## 📚 Дополнительные ресурсы

- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **DB Browser for SQLite**: https://sqlitebrowser.org/ (GUI для просмотра SQLite)

---

**🎉 Database Integration готова к использованию!**

Теперь OneFlow.AI имеет полную персистентность данных с поддержкой множества пользователей!
