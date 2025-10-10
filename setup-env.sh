#!/bin/bash
# ===== Setup Environment Files Script =====
# Путь: setup-env.sh (корень проекта, рядом с docker-compose.yml)
# Использование: chmod +x setup-env.sh && ./setup-env.sh

set -e

echo "🚀 OneFlow.AI - Environment Setup"
echo "=================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для генерации случайного пароля
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Функция для генерации JWT секрета
generate_jwt_secret() {
    openssl rand -hex 32
}

# Проверка наличия openssl
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ OpenSSL не установлен. Установите его для генерации паролей.${NC}"
    exit 1
fi

echo "📁 Создание конфигурационных файлов..."
echo ""

# 1. Основной .env
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  Файл .env уже существует. Пропускаю...${NC}"
else
    cat > .env << EOF
# ===== OneFlow.AI - Main Application Configuration =====
# Generated: $(date)

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
APP_PORT=8000

# Database
DATABASE_URL=postgresql://oneflow:oneflow_password@postgres:5432/oneflow

# Redis
REDIS_URL=redis://:redis_password@redis:6379/0

# Security
JWT_SECRET=$(generate_jwt_secret)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Features
ENABLE_METRICS=true
ENABLE_TRACING=false

# API Keys (добавьте свои ключи)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
EOF
    echo -e "${GREEN}✅ Создан: .env${NC}"
fi

# 2. PostgreSQL
if [ -f .env.postgres ]; then
    echo -e "${YELLOW}⚠️  Файл .env.postgres уже существует. Пропускаю...${NC}"
else
    cat > .env.postgres << EOF
# ===== PostgreSQL Configuration =====
# Generated: $(date)

POSTGRES_USER=oneflow
POSTGRES_PASSWORD=oneflow_password
POSTGRES_DB=oneflow
PGDATA=/var/lib/postgresql/data/pgdata
POSTGRES_PORT=5432

# Дополнительные настройки PostgreSQL
POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
EOF
    echo -e "${GREEN}✅ Создан: .env.postgres${NC}"
fi

# 3. Redis
if [ -f .env.redis ]; then
    echo -e "${YELLOW}⚠️  Файл .env.redis уже существует. Пропускаю...${NC}"
else
    cat > .env.redis << EOF
# ===== Redis Configuration =====
# Generated: $(date)

REDIS_PASSWORD=redis_password
REDIS_PORT=6379
EOF
    echo -e "${GREEN}✅ Создан: .env.redis${NC}"
fi

# 4. Grafana
if [ -f .env.grafana ]; then
    echo -e "${YELLOW}⚠️  Файл .env.grafana уже существует. Пропускаю...${NC}"
else
    cat > .env.grafana << EOF
# ===== Grafana Configuration =====
# Generated: $(date)

GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
GF_USERS_ALLOW_SIGN_UP=false
GF_SERVER_HTTP_PORT=3000
GF_ANALYTICS_REPORTING_ENABLED=false
GF_INSTALL_PLUGINS=
GRAFANA_PORT=3000
EOF
    echo -e "${GREEN}✅ Создан: .env.grafana${NC}"
fi

# 5. pgAdmin
if [ -f .env.pgadmin ]; then
    echo -e "${YELLOW}⚠️  Файл .env.pgadmin уже существует. Пропускаю...${NC}"
else
    cat > .env.pgadmin << EOF
# ===== pgAdmin Configuration =====
# Generated: $(date)

PGADMIN_DEFAULT_EMAIL=admin@oneflow.ai
PGADMIN_DEFAULT_PASSWORD=admin
PGADMIN_DISABLE_POSTFIX=true
PGADMIN_PORT=5050
EOF
    echo -e "${GREEN}✅ Создан: .env.pgadmin${NC}"
fi

# 6. Production files (с безопасными паролями)
echo ""
echo "🔒 Создание production конфигурации с безопасными паролями..."

PROD_POSTGRES_PASSWORD=$(generate_password)
PROD_REDIS_PASSWORD=$(generate_password)
PROD_JWT_SECRET=$(generate_jwt_secret)

if [ -f .env.production ]; then
    echo -e "${YELLOW}⚠️  Файл .env.production уже существует. Пропускаю...${NC}"
else
    cat > .env.production << EOF
# ===== OneFlow.AI - Production Configuration =====
# Generated: $(date)
# ⚠️  ВАЖНО: Замените ALLOWED_ORIGINS и API ключи!

# Application
ENVIRONMENT=production
LOG_LEVEL=WARNING
APP_PORT=8000

# Database
DATABASE_URL=postgresql://oneflow:${PROD_POSTGRES_PASSWORD}@postgres:5432/oneflow

# Redis
REDIS_URL=redis://:${PROD_REDIS_PASSWORD}@redis:6379/0

# Security
JWT_SECRET=${PROD_JWT_SECRET}
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Features
ENABLE_METRICS=true
ENABLE_TRACING=true

# API Keys (ЗАМЕНИТЕ НА РЕАЛЬНЫЕ!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
EOF
    echo -e "${GREEN}✅ Создан: .env.production${NC}"
fi

if [ -f .env.postgres.production ]; then
    echo -e "${YELLOW}⚠️  Файл .env.postgres.production уже существует. Пропускаю...${NC}"
else
    cat > .env.postgres.production << EOF
# ===== PostgreSQL Production Configuration =====
# Generated: $(date)

POSTGRES_USER=oneflow
POSTGRES_PASSWORD=${PROD_POSTGRES_PASSWORD}
POSTGRES_DB=oneflow
PGDATA=/var/lib/postgresql/data/pgdata
POSTGRES_PORT=5432

# Дополнительные настройки PostgreSQL
POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
EOF
    echo -e "${GREEN}✅ Создан: .env.postgres.production${NC}"
fi

if [ -f .env.redis.production ]; then
    echo -e "${YELLOW}⚠️  Файл .env.redis.production уже существует. Пропускаю...${NC}"
else
    cat > .env.redis.production << EOF
# ===== Redis Production Configuration =====
# Generated: $(date)

REDIS_PASSWORD=${PROD_REDIS_PASSWORD}
REDIS_PORT=6379
EOF
    echo -e "${GREEN}✅ Создан: .env.redis.production${NC}"
fi

# Создание директорий
echo ""
echo "📂 Создание необходимых директорий..."
mkdir -p logs backups monitoring/{prometheus,grafana/{dashboards,datasources}}
echo -e "${GREEN}✅ Директории созданы${NC}"

# Установка прав доступа
echo ""
echo "🔐 Установка прав доступа..."
chmod 600 .env* 2>/dev/null || true
echo -e "${GREEN}✅ Права установлены${NC}"

# Итоговая информация
echo ""
echo "=================================="
echo -e "${GREEN}✨ Настройка завершена!${NC}"
echo ""
echo "📋 Созданные файлы:"
echo "   - .env (разработка)"
echo "   - .env.postgres"
echo "   - .env.redis"
echo "   - .env.grafana"
echo "   - .env.pgadmin"
echo "   - .env.production (с безопасными паролями)"
echo "   - .env.postgres.production"
echo "   - .env.redis.production"
echo ""
echo "🚀 Следующие шаги:"
echo "   1. Отредактируйте .env файлы и добавьте API ключи"
echo "   2. Для продакшена: замените ALLOWED_ORIGINS в .env.production"
echo "   3. Запустите: docker-compose up -d"
echo ""
echo "💡 Полезные команды:"
echo "   - docker-compose up -d              # Запуск (dev)"
echo "   - docker-compose --profile full up -d  # Запуск с мониторингом"
echo "   - docker-compose logs -f            # Просмотр логов"
echo ""
echo -e "${YELLOW}⚠️  Не забудьте добавить .env* в .gitignore!${NC}"
echo ""
