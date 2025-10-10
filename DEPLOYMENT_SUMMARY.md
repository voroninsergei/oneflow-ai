# OneFlow.AI Monitoring Stack - Deployment Summary

## 🎯 What Was Configured

### ✅ Complete Monitoring Stack
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards
- **Jaeger** - Distributed tracing
- **Loki** - Log aggregation
- **Promtail** - Log shipping
- **Alertmanager** - Alert routing and management
- **Node Exporter** - System metrics
- **cAdvisor** - Container metrics
- **OpenTelemetry Collector** - Unified telemetry

### ✅ SLO-Based Alerting
Multi-window, multi-burn-rate alerts for:
- **Availability SLO**: 99.9% uptime (0.1% error budget)
- **Latency SLO**: P95 < 2 seconds
- **Cost Efficiency SLO**: < 0.5 credits per request
- **Provider Reliability SLO**: < 5% error rate per provider
- **User Experience SLO**: 95% good requests

### ✅ Operational Alerts
- System resources (CPU, memory, disk)
- Container health
- Database performance
- Rate limiting
- Monitoring stack health

## 📂 File Structure Created

```
monitoring/
├── docker-compose.yml               # Main orchestration
├── .env                            # Environment variables
├── setup.sh                        # Automated setup script
├── README.md                       # Full documentation
├── VERIFICATION.md                 # Testing guide
│
├── prometheus/
│   ├── prometheus.yml              # Scrape configs
│   ├── slo_alerts.yml              # SLO-based alerts ⭐
│   └── operational_alerts.yml      # Infrastructure alerts
│
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── datasources.yml     # Auto-provision datasources
│   │   └── dashboards/
│   │       └── dashboards.yml      # Auto-provision dashboards
│   └── dashboards/
│       └── README.md               # Dashboard creation guide
│
├── otel/
│   └── otel-collector-config.yml   # OTEL configuration
│
├── loki/
│   └── loki-config.yml             # Log aggregation config
│
├── promtail/
│   └── promtail-config.yml         # Log shipping config
│
└── alertmanager/
    └── alertmanager.yml            # Alert routing config
```

## 🚀 Quick Start Commands

### 1. Initial Setup

```bash
cd monitoring

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup:
# 1. Create configs (see README.md)
# 2. Set GRAFANA_PASSWORD in .env
# 3. Copy alert rules to prometheus/
```

### 2. Start Stack

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / (from .env) |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |
| Jaeger UI | http://localhost:16686 | - |
| Loki | http://localhost:3100 | API only |
| Node Exporter | http://localhost:9100/metrics | - |
| cAdvisor | http://localhost:8080 | - |

### 4. Verify Deployment

```bash
# Check all services are up
docker-compose ps

# Validate Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'

# Check Grafana health
curl -s http://localhost:3000/api/health

# Verify alert rules loaded
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | .name'
```

## 📊 Key Metrics to Instrument

### Required Application Metrics

```python
# Request metrics
oneflow_requests_total{status, provider, endpoint}  # Counter
oneflow_request_duration_seconds{provider}          # Histogram

# Provider health
oneflow_provider_health_status{provider}            # Gauge (0/1)
oneflow_provider_error_rate{provider}               # Gauge

# Circuit breaker
oneflow_circuit_breaker_state{provider}             # Gauge (0=closed, 1=open, 2=half-open)

# Cost metrics
oneflow_total_cost_credits{provider}                # Counter
oneflow_cost_per_request_credits{provider}          # Gauge

# Rate limiting
oneflow_rate_limit_exceeded_total{user_id}          # Counter
oneflow_quota_exceeded_total{user_id}               # Counter

# Budget tracking
oneflow_budget_utilization_percent{user_id,period}  # Gauge

# Routing
oneflow_fallback_activations_total{reason}          # Counter
oneflow_routing_decision_duration_seconds           # Histogram
```

### Instrumentation Example

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
requests_total = Counter(
    'oneflow_requests_total',
    'Total requests',
    ['status', 'provider', 'endpoint']
)

request_duration = Histogram(
    'oneflow_request_duration_seconds',
    'Request duration',
    ['provider'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Use in code
@app.post("/api/v1/completion")
async def completion(request: Request):
    start_time = time.time()
    
    try:
        result = await process_request(request)
        requests_total.labels(
            status='success',
            provider=result.provider,
            endpoint='/api/v1/completion'
        ).inc()
        return result
    except Exception as e:
        requests_total.labels(
            status='error',
            provider='unknown',
            endpoint='/api/v1/completion'
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        request_duration.labels(provider=result.provider).observe(duration)
```

## 🚨 Alert Severity Levels

### Critical (Page Immediately)
- Application down
- Error budget burning at 14.4x rate
- Provider completely unavailable
- System resources exhausted (>95% CPU/memory)
- Alertmanager down

### Warning (Create Ticket)
- Error budget burning at 6x rate
- High latency (P95 > 2s)
- Provider reliability degraded
- High resource usage (>80%)
- Database connection pool saturated

### Info (Review Later)
- Slow error budget burn (1x rate)
- Cost efficiency threshold exceeded
- Low cache hit rate
- Frequent quota violations

## 🔧 Common Operations

### Reload Configurations

```bash
# Reload Prometheus
curl -X POST http://localhost:9090/-/reload

# Reload Alertmanager
docker-compose exec alertmanager kill -HUP 1

# Restart Grafana
docker-compose restart grafana
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f alertmanager
```

### Scale Down Resources

```bash
# Stop optional services
docker-compose stop jaeger otel-collector

# Reduce Prometheus retention
# Edit docker-compose.yml:
# --storage.tsdb.retention.time=15d  # instead of 30d
```

### Backup Data

```bash
# Backup Grafana dashboards
docker cp oneflow-grafana:/var/lib/grafana/grafana.db ./backup/grafana.db

# Backup Prometheus data
docker cp oneflow-prometheus:/prometheus ./backup/prometheus

# Export alert rules
cp prometheus/*.yml ./backup/
```

### Clean Up

```bash
# Stop all services
docker-compose down

# Remove all data (WARNING: destructive!)
docker-compose down -v

# Remove only specific volumes
docker volume rm oneflow-prometheus-data
```

## 📈 Performance Tuning

### Prometheus
```yaml
# In docker-compose.yml, adjust:
--storage.tsdb.retention.time=15d      # Reduce if disk space limited
--storage.tsdb.retention.size=5GB      # Add size limit
```

### Grafana
```yaml
# In docker-compose.yml, add:
- GF_DATABASE_WAL=true                 # Enable WAL for better performance
- GF_ALERTING_ENABLED=false            # Disable if using Prometheus alerts only
```

### Loki
```yaml
# In loki-config.yml:
limits_config:
  max_query_length: 721h               # Reduce query window
  max_entries_limit_per_query: 5000    # Limit results
```

## 🔐 Security Hardening

### 1. Change Default Passwords
```bash
# Generate secure password
openssl rand -base64 32

# Update .env
echo "GRAFANA_PASSWORD=$(openssl rand -base64 32)" > .env
```

### 2. Enable Authentication
```yaml
# In prometheus.yml:
basic_auth:
  username: prometheus
  password: <secure_password>
```

### 3. Configure Network Security
```yaml
# In docker-compose.yml, expose only necessary ports
# Remove public exposure for internal services
```

### 4. Enable HTTPS
Use a reverse proxy (nginx, Traefik) for SSL termination

## 📚 Additional Resources

### Documentation
- [Prometheus Best Practices](https://prometheus.io/docs/practices/alerting/)
- [Grafana Dashboard Design](https://grafana.com/docs/grafana/latest/dashboards/)
- [SLO Implementation Guide](https://sre.google/workbook/implementing-slos/)

### Community Dashboards
- Node Exporter Full: `1860`
- Docker & System Monitoring: `893`
- Loki Dashboard: `13639`

### Troubleshooting
- Check VERIFICATION.md for detailed testing steps
- Review logs: `docker-compose logs -f <service>`
- Validate configs before deploying
- Use Prometheus query browser for metric debugging

## 🎓 Training Your Team

### Day 1: Basics
- Understanding metrics, logs, and traces
- Navigating Grafana
- Reading alert notifications
- Basic PromQL queries

### Day 2: Operations
- Responding to alerts
- Creating silences
- Dashboard customization
- Log queries in Loki

### Day 3: Advanced
- SLO concepts and error budgets
- Custom alert rules
- Dashboard templating
- Trace analysis in Jaeger

## ✅ Success Checklist

- [ ] All services running and healthy
- [ ] Prometheus scraping all targets
- [ ] Grafana datasources connected
- [ ] Alert rules loaded
- [ ] Test alert successfully fired
- [ ] Application metrics visible
- [ ] Dashboards displaying data
- [ ] Team trained on basic operations
- [ ] Runbooks documented
- [ ] On-call rotation configured
- [ ] Backup strategy in place

## 🎯 Next Steps

1. **Week 1**: Deploy and stabilize
   - Ensure all services are running
   - Verify metrics are being collected
   - Test alert notifications

2. **Week 2**: Customize
   - Create team-specific dashboards
   - Tune alert thresholds
   - Configure notification channels

3. **Week 3**: Optimize
   - Review and adjust SLOs
   - Implement cost optimizations
   - Add custom metrics

4. **Week 4**: Scale
   - Set up long-term storage
   - Implement high availability
   - Document operational procedures

---

**Need Help?**
- Check README.md for full documentation
- Review VERIFICATION.md for troubleshooting
- See grafana/dashboards/README.md for dashboard creation

**Stack Version**: Production-Ready v1.0
**Last Updated**: 2025-10-10
