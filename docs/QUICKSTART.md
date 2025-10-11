# 🚀 OneFlow.AI - Quick Start Guide

Get OneFlow.AI running locally in **15 minutes** with full monitoring stack.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Setup (15 min)](#quick-setup-15-min)
3. [Docker Compose Profiles](#docker-compose-profiles)
4. [Accessing Services](#accessing-services)
5. [Development Workflow](#development-workflow)
6. [Monitoring Stack](#monitoring-stack)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- **Docker**: 20.10+ & Docker Compose 2.0+
- **Python**: 3.11+ (for local development)
- **Resources**: 8GB RAM, 10GB disk space

### Optional
- **Make**: For convenient commands
- **curl/httpie**: For API testing
- **jq**: For JSON parsing

---

## Quick Setup (15 min)

### Option 1: Minimal Stack (App Only)

**Perfect for:** API development, testing routing logic

```bash
# 1. Clone repository (1 min)
git clone https://github.com/voroninsergei/oneflow-ai.git
cd oneflow-ai

# 2. Setup environment (2 min)
cp .env.example .env

# Edit with your API keys
nano .env
# Required:
# OPENAI_API_KEY=sk-your-key
# ANTHROPIC_API_KEY=sk-ant-your-key
# JWT_SECRET=$(openssl rand -hex 32)

# 3. Start minimal stack (2 min)
docker-compose up -d

# 4. Verify (1 min)
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**Services started:**
- ✅ OneFlow API (port 8000)
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)

---

### Option 2: Full Stack (With Monitoring)

**Perfect for:** Production-like environment, testing observability

```bash
# 1-2. Same as Option 1

# 3. Start full stack (5 min)
docker-compose --profile full up -d

# 4. Wait for services to start
sleep 60

# 5. Verify (2 min)
./scripts/health_check.sh
```

**Services started:**
- ✅ All from Option 1, plus:
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3000)
- ✅ Jaeger (port 16686)
- ✅ Loki (port 3100)
- ✅ Alertmanager (port 9093)
- ✅ Node Exporter (port 9100)
- ✅ cAdvisor (port 8080)

---

## Docker Compose Profiles

### Available Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| **(default)** | app, postgres, redis | Minimal development |
| `full` | all services | Production-like with monitoring |
| `db` | postgres, pgadmin | Database development |
| `monitoring` | prometheus, grafana | Add monitoring to running app |
| `tracing` | jaeger | Add distributed tracing |

### Usage Examples

**Start with specific profile:**
```bash
# Only database services
docker-compose --profile db up -d

# Monitoring only (app must be running separately)
docker-compose --profile monitoring up -d

# Combine multiple profiles
docker-compose --profile db --profile monitoring up -d

# Full stack
docker-compose --profile full up -d
```

**Check what's running:**
```bash
docker-compose ps

# Or with make
make docker-ps
```

---

## Accessing Services

### Primary Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **Swagger UI** | http://localhost:8000/docs | - |
| **ReDoc** | http://localhost:8000/redoc | - |
| **Health Check** | http://localhost:8000/health | - |
| **Metrics** | http://localhost:8000/metrics | - |

### Database Services

| Service | Connection | Credentials |
|---------|------------|-------------|
| **PostgreSQL** | `localhost:5432` | `oneflow` / `oneflow_password` |
| **pgAdmin** | http://localhost:5050 | `admin@oneflow.ai` / `admin` |
| **Redis** | `localhost:6379` | password: `redis_password` |

### Monitoring Services (with `--profile full` or `--profile monitoring`)

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | `admin` / `admin` |
| **Prometheus** | http://localhost:9090 | - |
| **Alertmanager** | http://localhost:9093 | - |
| **Jaeger UI** | http://localhost:16686 | - |
| **Node Exporter** | http://localhost:9100/metrics | - |
| **cAdvisor** | http://localhost:8080 | - |

---

## Development Workflow

### 1. Make Code Changes

```bash
# Edit source files
nano src/routing.py

# Rebuild and restart
docker-compose build app
docker-compose up -d app
```

### 2. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

### 3. Run Tests

```bash
# Inside container
docker-compose exec app pytest tests/ -v

# Or locally (if venv setup)
source venv/bin/activate
pytest tests/ -v
```

### 4. Database Operations

**Connect to PostgreSQL:**
```bash
# Via docker
docker-compose exec postgres psql -U oneflow -d oneflow

# Or use pgAdmin at http://localhost:5050
```

**Run migrations:**
```bash
docker-compose exec app alembic upgrade head
```

**Create backup:**
```bash
docker-compose exec postgres pg_dump -U oneflow oneflow > backup_$(date +%Y%m%d).sql
```

**Restore backup:**
```bash
docker-compose exec -T postgres psql -U oneflow oneflow < backup_20250110.sql
```

### 5. Redis Operations

**Connect to Redis:**
```bash
docker-compose exec redis redis-cli -a redis_password
```

**Check rate limits:**
```bash
docker-compose exec redis redis-cli -a redis_password --no-auth-warning KEYS "ratelimit:*"
```

**Clear cache:**
```bash
docker-compose exec redis redis-cli -a redis_password FLUSHDB
```

---

## Monitoring Stack

### Setting Up Monitoring (10 min)

**1. Start monitoring stack:**
```bash
docker-compose --profile monitoring up -d

# Or full stack
docker-compose --profile full up -d
```

**2. Access Grafana:**
- URL: http://localhost:3000
- Login: `admin` / `admin`
- Change password on first login

**3. Verify datasources:**
- Go to: **Configuration → Data Sources**
- Should see 3 datasources connected:
  - ✅ Prometheus
  - ✅ Loki
  - ✅ Jaeger

**4. Import dashboards:**

| Dashboard | ID | Purpose |
|-----------|-----|---------|
| Node Exporter Full | `1860` | System metrics |
| Docker & System | `893` | Container metrics |
| Loki Dashboard | `13639` | Log analysis |

**How to import:**
1. Grafana → **Dashboards → Import**
2. Enter dashboard ID
3. Select **Prometheus** as datasource
4. Click **Import**

### Key Metrics to Monitor

**Application Metrics:**
```promql
# Request rate
rate(http_requests_total[1m])

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# Cost per request
oneflow_cost_per_request_credits
```

**System Metrics:**
```promql
# CPU usage
rate(process_cpu_seconds_total[1m])

# Memory usage
process_resident_memory_bytes

# Active connections
http_requests_inprogress
```

### Using Jaeger for Tracing

**1. Enable tracing in .env:**
```bash
ENABLE_TRACING=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
```

**2. Restart app:**
```bash
docker-compose restart app
```

**3. Generate traces:**
```bash
# Send test requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/completion \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Hello", "max_tokens": 10}'
  sleep 1
done
```

**4. View in Jaeger:**
- URL: http://localhost:16686
- Service: `oneflow-ai`
- Operation: `POST /api/v1/completion`

### Alert Testing

**1. Check alert rules:**
```bash
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | .name'
```

**2. Trigger test alert:**
```bash
# Simulate high error rate
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/v1/invalid-endpoint
done
```

**3. Check Alertmanager:**
- URL: http://localhost:9093
- Should see alerts firing

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Common fix: Port already in use
docker-compose down
sudo lsof -ti:8000 | xargs kill -9
docker-compose up -d

# Force recreate
docker-compose up -d --force-recreate
```

#### 2. App Can't Connect to Database

```bash
# Test PostgreSQL connection
docker-compose exec postgres pg_isready -U oneflow

# Check if database exists
docker-compose exec postgres psql -U oneflow -c "\l"

# Recreate database
docker-compose down -v
docker-compose up -d
```

#### 3. Prometheus Can't Scrape App

**If app is on host (not in Docker):**

Edit `monitoring/prometheus/prometheus.yml`:
```yaml
# Change from:
- targets: ['host.docker.internal:8000']

# To (Linux):
- targets: ['172.17.0.1:8000']
```

Then reload:
```bash
curl -X POST http://localhost:9090/-/reload
```

#### 4. Grafana Datasource Not Working

```bash
# Test from inside Grafana container
docker-compose exec grafana wget -O- http://prometheus:9090/api/v1/query?query=up

# If fails, check network
docker network inspect oneflow_network

# Restart both services
docker-compose restart prometheus grafana
```

#### 5. High Memory Usage

**Reduce Prometheus retention:**

Edit `docker-compose.yml`:
```yaml
services:
  prometheus:
    command:
      - '--storage.tsdb.retention.time=7d'  # was 30d
```

Then:
```bash
docker-compose up -d prometheus
```

#### 6. Redis Connection Issues

```bash
# Test Redis
docker-compose exec redis redis-cli -a redis_password ping
# Expected: PONG

# Check config
docker-compose exec redis redis-cli -a redis_password CONFIG GET maxmemory
```

### Health Check Script

```bash
# Run comprehensive health check
./scripts/health_check.sh

# Or manually:
curl http://localhost:8000/health
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
curl http://localhost:9093/-/healthy
```

### Debug Commands

**Check all containers:**
```bash
docker-compose ps --format json | jq '.[].Health'
```

**Inspect network:**
```bash
docker network inspect oneflow_network
```

**Check resource usage:**
```bash
docker stats
```

**Get into container shell:**
```bash
docker-compose exec app /bin/bash
docker-compose exec postgres /bin/bash
docker-compose exec redis /bin/sh
```

---

## Environment Variables

### Core Configuration (.env)

```bash
# Environment
ENVIRONMENT=development              # development | production
LOG_LEVEL=INFO                      # DEBUG | INFO | WARNING | ERROR

# API
APP_PORT=8000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://oneflow:oneflow_password@postgres:5432/oneflow
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://:redis_password@redis:6379/0
REDIS_MAX_CONNECTIONS=50

# Security
JWT_SECRET=<generate with: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Observability
ENABLE_METRICS=true
ENABLE_TRACING=false
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### Override Ports

```bash
# In .env or shell:
APP_PORT=8080
POSTGRES_PORT=5433
REDIS_PORT=6380
GRAFANA_PORT=3001
PROMETHEUS_PORT=9091
```

---

## Useful Commands

### Make Commands (if Makefile present)

```bash
make dev              # Start dev server
make docker-up        # Start Docker stack
make docker-down      # Stop Docker stack
make docker-logs      # View logs
make docker-clean     # Clean everything
make test             # Run tests
make lint             # Run linting
```

### Manual Commands

**Start/Stop:**
```bash
docker-compose up -d                    # Start in background
docker-compose down                     # Stop all services
docker-compose down -v                  # Stop and remove volumes
docker-compose restart <service>        # Restart specific service
```

**Logs:**
```bash
docker-compose logs -f                  # Follow all logs
docker-compose logs -f app              # Follow app logs only
docker-compose logs --tail=50 app       # Last 50 lines
```

**Execute:**
```bash
docker-compose exec app pytest          # Run tests
docker-compose exec app python          # Open Python REPL
docker-compose exec postgres psql -U oneflow   # Database shell
```

**Maintenance:**
```bash
docker-compose pull                     # Update images
docker-compose build --no-cache         # Rebuild from scratch
docker system prune -a                  # Clean Docker system
```

---

## Testing the Setup

### 1. Basic API Test

```bash
# Health check
curl http://localhost:8000/health

# Swagger docs
open http://localhost:8000/docs
```

### 2. Test Completion Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Say hello",
    "max_tokens": 10,
    "strategy": "cost_optimized"
  }'
```

### 3. Check Metrics

```bash
# Raw metrics
curl http://localhost:8000/metrics

# Query via Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=http_requests_total' | jq
```

### 4. Generate Test Load

```bash
# Simple load test
for i in {1..50}; do
  curl -s http://localhost:8000/metrics > /dev/null
  sleep 0.5
done

# Check if metrics appear
curl -s 'http://localhost:9090/api/v1/query?query=http_requests_total' | jq
```

---

## Next Steps

### Immediate (Today)
1. ✅ Verify all services are healthy
2. ✅ Test API endpoints in Swagger UI
3. ✅ Import Grafana dashboards
4. ✅ Configure alert notifications

### This Week
1. 📊 Create custom Grafana dashboard
2. 🔔 Set up Slack/email alerts
3. 📈 Instrument custom metrics
4. 🧪 Add integration tests

### Production Ready
1. 🔒 Change all default passwords
2. 🌐 Set up reverse proxy (nginx/traefik)
3. 📜 Get SSL certificates
4. 💾 Configure automated backups
5. 📖 Write runbooks for alerts

---

## Additional Resources

### Documentation
- **API Docs**: http://localhost:8000/docs
- **Deployment Guide**: [docs/DEPLOYMENT.md](DEPLOYMENT.md)
- **Changelog**: [docs/CHANGELOG.md](CHANGELOG.md)

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Tutorials](https://grafana.com/tutorials/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

### Community
- GitHub Issues: [Report bugs](https://github.com/voroninsergei/oneflow-ai/issues)
- Email: voroninsergeiai@gmail.com

---

## Summary

You now have:
- ✅ OneFlow.AI API running on port 8000
- ✅ PostgreSQL database with pgAdmin
- ✅ Redis for caching and rate limiting
- ✅ (Optional) Full monitoring stack with Prometheus, Grafana, Jaeger
- ✅ Health checks and metrics exposed
- ✅ Development workflow established

**Time to complete**: 15-30 minutes (depending on options)

**What's next?** 
- Test the API: http://localhost:8000/docs
- View metrics: http://localhost:3000 (Grafana)
- Deploy to production: [docs/DEPLOYMENT.md](DEPLOYMENT.md)

**Happy coding! 🚀**
