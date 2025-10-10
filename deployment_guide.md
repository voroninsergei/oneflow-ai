# OneFlow.AI - Production Deployment Guide
## Руководство по развертыванию в production

---

## 🎯 Этап 6: Docker & Deployment - Complete

### ✅ Что создано:

1. **Production Dockerfile**
   - Multi-stage build для оптимизации размера
   - Non-root user для безопасности
   - Health checks
   - Оптимизированные layers

2. **Docker Compose**
   - PostgreSQL база данных
   - Redis для кеширования
   - Nginx reverse proxy
   - Prometheus мониторинг
   - Grafana dashboards
   - Полная оркестрация сервисов

3. **CI/CD Pipeline**
   - GitHub Actions
   - Автоматическое тестирование
   - Автоматический deployment

4. **Production Configuration**
   - Environment variables
   - Security settings
   - Logging configuration
   - Monitoring setup

---

## 📦 Структура файлов Deployment

```
OneFlow.AI/
├── Dockerfile                  # ← Production image
├── docker-compose.yml          # ← Orchestration
├── .dockerignore               # ← Exclude files
├── .env.example                # ← Environment template
├── .github/
│   └── workflows/
│       └── deploy.yml          # ← CI/CD pipeline
├── nginx/
│   ├── nginx.conf              # ← Nginx config
│   └── ssl/                    # ← SSL certificates
├── monitoring/
│   ├── prometheus.yml          # ← Prometheus config
│   └── grafana/
│       ├── dashboards/         # ← Grafana dashboards
│       └── datasources/        # ← Data sources
├── scripts/
│   ├── backup.sh               # ← Backup script
│   ├── restore.sh              # ← Restore script
│   └── deploy.sh               # ← Deployment script
└── k8s/                        # ← Kubernetes manifests (optional)
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

---

## 🚀 Quick Start - Local Development

### Шаг 1: Клонировать и настроить

```bash
# Клонировать репозиторий
git clone https://github.com/yourorg/OneFlow.AI.git
cd OneFlow.AI

# Создать .env из примера
cp .env.example .env

# Отредактировать .env
nano .env
```

### Шаг 2: Настроить .env файл

```bash
# .env
# Database
POSTGRES_DB=oneflow
POSTGRES_USER=oneflow
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# JWT
JWT_SECRET_KEY=your_jwt_secret_key_here_min_32_chars

# API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
STABILITY_API_KEY=sk-your-stability-key
ELEVENLABS_API_KEY=your-elevenlabs-key

# Application
ENVIRONMENT=development
LOG_LEVEL=debug
WORKERS=2

# Grafana
GRAFANA_PASSWORD=admin
```

### Шаг 3: Запустить с Docker Compose

```bash
# Собрать и запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотреть логи
docker-compose logs -f app
```

### Шаг 4: Проверить работу

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Grafana dashboard
open http://localhost:3000
```

---

## 🏭 Production Deployment

### Вариант 1: VPS/Dedicated Server

#### 1.1 Подготовка сервера

```bash
# Подключиться к серверу
ssh root@your-server-ip

# Обновить систему
apt update && apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установить Docker Compose
apt install docker-compose-plugin

# Создать пользователя
adduser oneflow
usermod -aG docker oneflow
su - oneflow
```

#### 1.2 Клонировать и настроить

```bash
# Клонировать репозиторий
git clone https://github.com/yourorg/OneFlow.AI.git
cd OneFlow.AI

# Создать production .env
cp .env.example .env
nano .env

# ВАЖНО: Установите сильные пароли и секретные ключи!
```

#### 1.3 Настроить SSL (Let's Encrypt)

```bash
# Установить certbot
apt install certbot python3-certbot-nginx

# Получить SSL сертификат
certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Скопировать сертификаты
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Настроить auto-renewal
certbot renew --dry-run
```

#### 1.4 Запустить в production

```bash
# Собрать production image
docker-compose build

# Запустить сервисы
docker-compose up -d

# Проверить логи
docker-compose logs -f

# Проверить статус
docker-compose ps
```

#### 1.5 Настроить автозапуск

```bash
# Создать systemd service
sudo nano /etc/systemd/system/oneflow.service
```

```ini
[Unit]
Description=OneFlow.AI Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/oneflow/OneFlow.AI
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=oneflow

[Install]
WantedBy=multi-user.target
```

```bash
# Включить автозапуск
sudo systemctl enable oneflow
sudo systemctl start oneflow
```

---

### Вариант 2: AWS Deployment

#### 2.1 EC2 Instance

```bash
# Создать EC2 instance
# - AMI: Ubuntu 22.04 LTS
# - Instance type: t3.medium (минимум)
# - Storage: 30GB SSD
# - Security Group: HTTP (80), HTTPS (443), SSH (22)

# Подключиться
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# Установить Docker
# ... (те же шаги что и для VPS)
```

#### 2.2 RDS для PostgreSQL

```bash
# В AWS Console создать RDS PostgreSQL
# Получить connection string

# Обновить .env
DATABASE_URL=postgresql://user:pass@rds-endpoint.region.rds.amazonaws.com:5432/oneflow
```

#### 2.3 ElastiCache для Redis

```bash
# Создать ElastiCache Redis
# Получить endpoint

# Обновить .env
REDIS_URL=redis://elasticache-endpoint:6379/0
```

#### 2.4 S3 для файлов

```bash
# Создать S3 bucket для логов и данных
# Настроить IAM роль

# Обновить код для использования S3
```

---

### Вариант 3: Kubernetes Deployment

#### 3.1 Создать манифесты

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oneflow-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oneflow
  template:
    metadata:
      labels:
        app: oneflow
    spec:
      containers:
      - name: app
        image: yourdockerhub/oneflow:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: oneflow-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: oneflow-secrets
              key: jwt-secret
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

```bash
# Применить манифесты
kubectl apply -f k8s/

# Проверить статус
kubectl get pods
kubectl get services
```

---

## 🔧 Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        least_conn;
        server app:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Auth endpoints with stricter rate limiting
        location /auth/ {
            limit_req zone=auth_limit burst=5 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # All other endpoints
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support (if needed)
        location /ws {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

---

## 📊 Monitoring Setup

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'oneflow-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
```

### Grafana Dashboard

```json
// monitoring/grafana/dashboards/oneflow.json
{
  "dashboard": {
    "title": "OneFlow.AI Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

``