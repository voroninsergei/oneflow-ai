#!/bin/bash

# ===== OneFlow.AI - Local Development Setup =====
# This script creates .env files for local development

set -e

echo "🚀 Setting up OneFlow.AI for local development..."

# Check if .env already exists
if [ -f .env ]; then
    read -p "⚠️  .env already exists. Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping .env creation"
        exit 0
    fi
fi

# Generate secure random passwords
JWT_SECRET=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
GRAFANA_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
PGADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)

# Create main .env file
cat > .env << EOF
# ===== OneFlow.AI - Local Development Configuration =====
# Generated on $(date)
# DO NOT COMMIT THIS FILE

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
APP_PORT=8000

# Database
DATABASE_URL=postgresql://oneflow:${POSTGRES_PASSWORD}@postgres:5432/oneflow

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Security
JWT_SECRET=${JWT_SECRET}
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Features
ENABLE_METRICS=true
ENABLE_TRACING=false

# API Keys (you need to add these manually)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
EOF

# Create PostgreSQL .env
cat > .env.postgres << EOF
POSTGRES_USER=oneflow
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=oneflow
PGDATA=/var/lib/postgresql/data/pgdata
POSTGRES_PORT=5432
POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
EOF

# Create Redis .env
cat > .env.redis << EOF
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_PORT=6379
EOF

# Create Grafana .env
cat > .env.grafana << EOF
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
GF_USERS_ALLOW_SIGN_UP=false
GF_SERVER_HTTP_PORT=3000
GF_ANALYTICS_REPORTING_ENABLED=false
GF_INSTALL_PLUGINS=
GRAFANA_PORT=3000
EOF

# Create pgAdmin .env
cat > .env.pgadmin << EOF
PGADMIN_DEFAULT_EMAIL=admin@oneflow.local
PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASSWORD}
PGADMIN_DISABLE_POSTFIX=true
PGADMIN_PORT=5050
EOF

# Create credentials file for reference
cat > .credentials.local.txt << EOF
===== OneFlow.AI Local Development Credentials =====
Generated on $(date)

🔐 Security Warning: Keep this file secure and never commit it!

PostgreSQL:
  Host: localhost:5432
  User: oneflow
  Password: ${POSTGRES_PASSWORD}
  Database: oneflow

Redis:
  Host: localhost:6379
  Password: ${REDIS_PASSWORD}

Grafana:
  URL: http://localhost:3000
  User: admin
  Password: ${GRAFANA_PASSWORD}

pgAdmin:
  URL: http://localhost:5050
  Email: admin@oneflow.local
  Password: ${PGADMIN_PASSWORD}

JWT Secret: ${JWT_SECRET}

⚠️  Don't forget to add your API keys to .env:
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - GOOGLE_API_KEY
EOF

echo "✅ Local development environment files created!"
echo ""
echo "📝 Next steps:"
echo "1. Review .credentials.local.txt for all passwords"
echo "2. Add your API keys to .env file"
echo "3. Run: docker-compose up -d"
echo ""
echo "⚠️  IMPORTANT: Never commit .env* files (except .example files) to git!"
