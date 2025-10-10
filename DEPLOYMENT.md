# 🚀 OneFlow.AI - Production Deployment Guide

Комплексное руководство по развёртыванию OneFlow.AI в production-среде.

---

## 📋 Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Локальная разработка](#локальная-разработка)
3. [Docker развёртывание](#docker-развёртывание)
4. [Kubernetes развёртывание](#kubernetes-развёртывание)
5. [Мониторинг и наблюдаемость](#мониторинг-и-наблюдаемость)
6. [Безопасность](#безопасность)
7. [Обслуживание](#обслуживание)

---

## 🔧 Предварительные требования

### Минимальные требования

- **Python**: 3.11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Kubernetes**: 1.24+ (для K8s развёртывания)
- **PostgreSQL**: 14+
- **Redis**: 7+

### Рекомендуемые ресурсы

**Для одного инстанса:**
- CPU: 2 cores
- RAM: 2 GB
- Disk: 10 GB SSD

**Для production кластера:**
- CPU: 4+ cores per node
- RAM: 8+ GB per node
- Disk: 50+ GB SSD

---

## 💻 Локальная разработка

### 1. Клонирование репозитория

```bash
git clone https://github.com/voroninsergei/oneflow-ai.git
cd oneflow-ai
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
make install-dev
```

### 3. Конфигурация

```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование .env файла
nano .env
```

**Минимальная конфигурация:**

```bash
# API Keys (ОБЯЗАТЕЛЬНО!)
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# Database
DATABASE_URL=postgresql://oneflow:password@localhost:5432/oneflow

# Security
JWT_SECRET=$(openssl rand -hex 32)
```

### 4. Запуск базы данных

```bash
# Запуск PostgreSQL и Redis
docker-compose up -d postgres redis

# Применение миграций
make db-migrate
```

### 5. Запуск приложения

```bash
# Development сервер с auto-reload
make dev

# Открыть документацию API
open http://localhost:8000/docs
```

---

## 🐳 Docker развёртывание

### 1. Подготовка

```bash
# Создание .env файла с production значениями
cp .env.example .env

# Редактирование конфигурации
nano .env
```

### 2. Сборка образа

```bash
# Сборка Docker образа
make docker-build

# Проверка образа
docker images | grep oneflow-ai
```

### 3. Запуск stack

```bash
# Запуск всех сервисов
make docker-up

# Проверка статуса
docker-compose ps

# Просмотр логов
make docker-logs
```

### 4. Проверка работоспособности

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# API документация
open http://localhost:8000/docs
```

### 5. Управление сервисами

```bash
# Перезапуск приложения
make docker-restart

# Остановка всех сервисов
make docker-down

# Полная очистка
make docker-clean
```

---

## ☸️ Kubernetes развёртывание

### 1. Подготовка кластера

```bash
# Проверка доступности кластера
kubectl cluster-info

# Создание namespace
kubectl create namespace oneflow-ai

# Переключение контекста
kubectl config set-context --current --namespace=oneflow-ai
```

### 2. Secrets и ConfigMaps

```bash
# Создание Secret с API ключами
kubectl create secret generic oneflow-secrets \
  --from-literal=JWT_SECRET=$(openssl rand -hex 32) \
  --from-literal=OPENAI_API_KEY=sk-your-key \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-your-key \
  --from-literal=DATABASE_URL=postgresql://user:pass@postgres:5432/oneflow \
  -n oneflow-ai
```

**Или использовать External Secrets Operator (рекомендуется):**

```yaml
# external-secret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: oneflow-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager  # или vault, gcp, azure
    kind: SecretStore
  target:
    name: oneflow-secrets
  data:
  - secretKey: OPENAI_API_KEY
    remoteRef:
      key: prod/oneflow/openai-api-key
```

### 3. Развёртывание PostgreSQL (опционально)

Если используете внешнюю БД (RDS, Cloud SQL), пропустите этот шаг.

```bash
# Установка PostgreSQL через Helm
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install postgres bitnami/postgresql \
  --set auth.username=oneflow \
  --set auth.password=secure-password \
  --set auth.database=oneflow \
  --set primary.persistence.size=50Gi \
  -n oneflow-ai
```

### 4. Развёртывание Redis

```bash
helm install redis bitnami/redis \
  --set auth.password=redis-password \
  --set master.persistence.size=10Gi \
  -n oneflow-ai
```

### 5. Развёртывание приложения

```bash
# Применение всех манифестов
make k8s-deploy

# Или вручную
kubectl apply -f k8s/

# Проверка статуса
make k8s-status
```

### 6. Настройка Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oneflow-ai
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: oneflow-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: oneflow-ai
            port:
              number: 8000
```

### 7. Проверка

```bash
# Port-forward для локального доступа
make k8s-port-forward

# Проверка health
curl http://localhost:8000/health

# Просмотр логов
make k8s-logs
```

---

## 📊 Мониторинг и наблюдаемость

### Prometheus Metrics

**Доступные метрики:**

- `http_requests_total` - Общее количество запросов
- `http_request_duration_seconds` - Длительность запросов
- `http_requests_inprogress` - Текущие запросы
- `python_gc_*` - Сборка мусора Python
- `process_*` - Метрики процесса

**Запросы в Prometheus:**

```promql
# Request rate per minute
rate(http_requests_total[1m])

# Average latency
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### Grafana Dashboards

```bash
# Доступ к Grafana
make grafana

# Default credentials: admin/admin
```

**Импорт готовых дашбордов:**

1. FastAPI Dashboard: ID 11713
2. PostgreSQL Dashboard: ID 9628
3. Redis Dashboard: ID 11835

### Distributed Tracing

```bash
# Включение tracing в .env
ENABLE_TRACING=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318

# Доступ к Jaeger UI
make jaeger
```

### Логирование

**Structured logs в JSON:**

```json
{
  "event": "http_request",
  "level": "info",
  "timestamp": "2025-01-10T12:34:56.789Z",
  "method": "POST",
  "path": "/api/v1/request",
  "status_code": 200,
  "duration_ms": 245.67,
  "user_id": "user_abc123"
}
```

**Агрегация логов:**

- **ELK Stack**: Elasticsearch + Logstash + Kibana
- **Loki**: Grafana Loki + Promtail
- **CloudWatch**: AWS CloudWatch Logs

---

## 🔒 Безопасность

### 1. Секреты

**НЕ КОММИТИТЬ в git:**
- `.env` файл
- API ключи провайдеров
- JWT секрет
- Пароли БД

**Использовать:**
- HashiCorp Vault
- AWS Secrets Manager
- GCP Secret Manager
- Azure Key Vault
- Kubernetes External Secrets Operator

### 2. Network Policies

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: oneflow-ai-policy
spec:
  podSelector:
    matchLabels:
      app: oneflow-ai
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:  # API провайдеры
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

### 3. RBAC

```yaml
# k8s/rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind:Role
metadata:
  name: oneflow-ai-role
rules:
- apiGroups: [""]
  resources: ["secrets", "configmaps"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: oneflow-ai-binding
subjects:
- kind: ServiceAccount
  name: oneflow-ai
roleRef:
  kind: Role
  name: oneflow-ai-role
  apiGroup: rbac.authorization.k8s.io
```

### 4. Security Scanning

```bash
# Сканирование Docker образа
docker scan oneflow-ai:2.0.0

# Trivy scan
trivy image oneflow-ai:2.0.0

# Проверка зависимостей
make security-check
```

---

## 🔧 Обслуживание

### Backup и Restore

**PostgreSQL:**

```bash
# Backup
kubectl exec -it postgres-0 -n oneflow-ai -- \
  pg_dump -U oneflow oneflow > backup.sql

# Restore
kubectl exec -i postgres-0 -n oneflow-ai -- \
  psql -U oneflow oneflow < backup.sql
```

### Обновление версии

```bash
# 1. Сборка нового образа
docker build -t oneflow-ai:2.1.0 .

# 2. Обновление в K8s
kubectl set image deployment/oneflow-ai \
  oneflow-ai=oneflow-ai:2.1.0 \
  -n oneflow-ai

# 3. Откат при проблемах
kubectl rollout undo deployment/oneflow-ai -n oneflow-ai
```

### Масштабирование

```bash
# Ручное масштабирование
kubectl scale deployment oneflow-ai --replicas=5 -n oneflow-ai

# Автомасштабирование (HPA уже настроен)
kubectl get hpa -n oneflow-ai
```

### Troubleshooting

```bash
# Проверка логов
kubectl logs -f deployment/oneflow-ai -n oneflow-ai

# Exec в pod
kubectl exec -it <pod-name> -n oneflow-ai -- /bin/bash

# Проверка events
kubectl get events -n oneflow-ai --sort-by='.lastTimestamp'

# Описание pod
kubectl describe pod <pod-name> -n oneflow-ai
```

---

## 📞 Поддержка

- **Email**: voroninsergeiai@gmail.com
- **GitHub Issues**: https://github.com/voroninsergei
