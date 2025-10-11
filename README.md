# 🚀 OneFlow.AI - Universal AI Gateway

**Production-ready AI routing platform with intelligent provider selection, cost optimization, and comprehensive observability.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Production Readiness](#-production-readiness)
- [Support](#-support)

---

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Provider Support** - OpenAI, Anthropic, Google AI, and more
- **Intelligent Routing** - Cost, latency, and quality-optimized strategies
- **Token-Based Billing** - Precise cost tracking per request
- **Circuit Breaker** - Automatic failover and recovery
- **Rate Limiting** - Per-user, per-provider quotas with Redis

### 📊 Observability
- **Prometheus Metrics** - Request rates, latency, errors, costs
- **Structured Logging** - JSON logs with request correlation
- **Distributed Tracing** - OpenTelemetry + Jaeger integration
- **Grafana Dashboards** - Real-time monitoring and alerting
- **SLO-Based Alerts** - Multi-window burn rate detection

### 🔒 Security
- **JWT Authentication** - Token-based auth with automatic rotation
- **API Key Management** - Secure storage and rotation
- **Security Headers** - CORS, CSP, HSTS configured
- **Request Validation** - Size limits, input sanitization
- **Secret Management** - Compatible with Vault, AWS Secrets Manager

### 🐳 DevOps Ready
- **Docker Support** - Multi-stage, optimized builds
- **Kubernetes Manifests** - Deployments, HPA, PDB, Ingress
- **Health Checks** - Liveness, readiness, startup probes
- **Auto-Scaling** - HPA based on CPU/memory/custom metrics
- **Zero-Downtime Deploys** - Rolling updates with PDB

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Redis (for caching/rate limiting)
- PostgreSQL (for persistence)

### For Local Development

```bash
# 1. Clone repository
git clone https://github.com/voroninsergei/oneflow-ai.git
cd oneflow-ai

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 3. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run with Docker Compose
docker-compose up -d

# 5. Access services
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

**📖 Full guide:** [docs/QUICKSTART.md](docs/QUICKSTART.md)

### For Production Deployment

```bash
# 1. Build Docker image
docker build -t oneflow-ai:2.0.0 .

# 2. Deploy to Kubernetes
kubectl create namespace oneflow-ai
kubectl create secret generic oneflow-secrets --from-env-file=.env -n oneflow-ai
kubectl apply -f k8s/ -n oneflow-ai

# 3. Verify deployment
kubectl get pods -n oneflow-ai
kubectl logs -f deployment/oneflow-ai -n oneflow-ai
```

**📖 Full guide:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Apps                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Load Balancer │ (Ingress/ALB)
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐         ┌────▼───┐         ┌────▼───┐
    │ Pod 1  │         │ Pod 2  │         │ Pod N  │
    │FastAPI │         │FastAPI │         │FastAPI │
    └───┬────┘         └────┬───┘         └────┬───┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
       ┌────▼─────┐    ┌────▼────┐    ┌────▼─────┐
       │PostgreSQL│    │  Redis  │    │AI Provider│
       │ (State)  │    │ (Cache) │    │  APIs     │
       └──────────┘    └─────────┘    └───────────┘
                            │
                    ┌───────▼────────┐
                    │  Observability │
                    │ Prometheus     │
                    │ Grafana        │
                    │ Jaeger         │
                    └────────────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **API Gateway** | Request routing and orchestration | FastAPI |
| **Circuit Breaker** | Fault tolerance and failover | Tenacity + Custom |
| **Pricing Engine** | Token-based cost calculation | Custom (supports all providers) |
| **Auth Manager** | JWT + API key authentication | PyJWT + Redis |
| **Metrics** | Real-time observability | Prometheus + Grafana |
| **Tracing** | Distributed request tracking | OpenTelemetry + Jaeger |
| **Storage** | State persistence | PostgreSQL |
| **Cache** | Rate limiting + caching | Redis |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](docs/QUICKSTART.md) | 15-minute local setup guide |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment (Docker, K8s) |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history and migration guides |
| [API Reference](http://localhost:8000/docs) | Interactive Swagger documentation |

---

## ✅ Production Readiness

### Observability: 100% ✅
- ✅ Prometheus metrics on `/metrics`
- ✅ Structured JSON logging with structlog
- ✅ OpenTelemetry distributed tracing
- ✅ Grafana dashboards with SLO alerts
- ✅ Health check endpoints (`/health`, `/ready`)

### Reliability: 95% ✅
- ✅ Circuit breaker with exponential backoff
- ✅ Retry logic with jitter
- ✅ Request timeouts (30s total, 10s connect)
- ✅ Rate limiting per user/provider
- ✅ Idempotency keys support

### Routing & Pricing: 100% ✅
- ✅ Token-based cost calculation
- ✅ Multi-strategy routing (cost/latency/quality)
- ✅ Real-time provider health tracking
- ✅ Budget tracking per user/project
- ✅ Property-based pricing tests

### Security: 100% ✅
- ✅ Security headers (CSP, HSTS, X-Frame-Options)
- ✅ CORS with whitelist
- ✅ Request size limits (10MB)
- ✅ Secret sanitization in logs
- ✅ API key rotation with grace period

### Infrastructure: 100% ✅
- ✅ Multi-stage Docker builds
- ✅ Kubernetes manifests (Deployment, HPA, PDB)
- ✅ Health probes (liveness, readiness, startup)
- ✅ Resource limits and requests
- ✅ Non-root container execution

**Overall Readiness: 99% ✅**

---

## 🔧 Configuration

### Minimal `.env` for development:

```bash
# API Keys (Required)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database
DATABASE_URL=postgresql://oneflow:password@localhost:5432/oneflow

# Security
JWT_SECRET=$(openssl rand -hex 32)

# Observability (Optional)
ENABLE_METRICS=true
ENABLE_TRACING=false
```

### Production additions:

```bash
# Redis
REDIS_URL=redis://:password@redis:6379/0

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
MAX_REQUEST_SIZE=10485760  # 10MB

# Performance
WORKER_COUNT=4
TIMEOUT_TOTAL=30
TIMEOUT_CONNECT=10
```

---

## 📊 Monitoring & Alerts

### Key Metrics

```promql
# Request rate
rate(http_requests_total[1m])

# Average latency
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# Cost per request
oneflow_cost_per_request_credits{provider="openai"}
```

### SLO Alerts

- **Availability**: 99.9% uptime (0.1% error budget)
- **Latency**: P95 < 2 seconds
- **Cost Efficiency**: < 0.5 credits per request
- **Provider Reliability**: < 5% error rate

Alert on:
- 🔴 Critical: 14.4x burn rate (page immediately)
- 🟡 Warning: 6x burn rate (create ticket)
- ℹ️ Info: 1x burn rate (review later)

---

## 🛠️ Development

### Useful Commands

```bash
# Development
make dev              # Run dev server with auto-reload
make test             # Run all tests
make lint             # Run linting
make format           # Format code

# Docker
make docker-build     # Build image
make docker-up        # Start all services
make docker-logs      # View logs

# Kubernetes
make k8s-deploy       # Deploy to K8s
make k8s-status       # Check pod status
make k8s-logs         # Stream logs
```

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# Property-based tests
pytest tests/test_pricing_properties.py -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest --cov=src tests/
```

---

## 🐛 Troubleshooting

### Common Issues

**App won't start:**
```bash
# Check logs
docker-compose logs -f app

# Verify environment
cat .env | grep -v "^#" | grep -v "^$"
```

**Metrics not appearing:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

**Database connection error:**
```bash
# Test PostgreSQL
docker-compose exec postgres pg_isready -U oneflow
```

**Redis connection error:**
```bash
# Test Redis
docker-compose exec redis redis-cli ping
```

**Full health check:**
```bash
./scripts/health_check.sh
```

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Ensure all tests pass

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Email**: voroninsergeiai@gmail.com
- **GitHub Issues**: [Create an issue](https://github.com/voroninsergei/oneflow-ai/issues)
- **Documentation**: [docs/](docs/)
- **API Docs**: http://localhost:8000/docs

---

## 🗺️ Roadmap

### Current (v2.0)
- ✅ Multi-provider routing
- ✅ Token-based billing
- ✅ Full observability stack
- ✅ Kubernetes deployment

### Planned (v2.1+)
- [ ] GraphQL API
- [ ] WebSocket streaming support
- [ ] ML-based routing predictions
- [ ] Multi-region deployment
- [ ] Advanced caching strategies
- [ ] Cost optimization recommendations

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Prometheus/Grafana for observability tools
- OpenTelemetry for tracing standards
- The AI community for provider APIs

---

**Made with ❤️ by Sergey Voronin**

*Last Updated: 2025-10-10*
