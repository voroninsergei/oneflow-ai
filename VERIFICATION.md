# Monitoring Stack Verification Guide

## ✅ Pre-Deployment Checklist

### 1. File Structure Verification

```bash
# Check all required files exist
ls -la monitoring/

# Expected structure:
# monitoring/
# ├── docker-compose.yml
# ├── .env
# ├── prometheus/
# │   ├── prometheus.yml
# │   ├── slo_alerts.yml
# │   └── operational_alerts.yml
# ├── grafana/
# │   ├── provisioning/
# │   │   ├── datasources/datasources.yml
# │   │   └── dashboards/dashboards.yml
# │   └── dashboards/
# ├── otel/
# │   └── otel-collector-config.yml
# ├── loki/
# │   └── loki-config.yml
# ├── promtail/
# │   └── promtail-config.yml
# └── alertmanager/
#     └── alertmanager.yml
```

### 2. Configuration Validation

```bash
# Validate Prometheus config
docker run --rm -v $(pwd)/prometheus:/etc/prometheus prom/prometheus:latest promtool check config /etc/prometheus/prometheus.yml

# Validate alert rules
docker run --rm -v $(pwd)/prometheus:/etc/prometheus prom/prometheus:latest promtool check rules /etc/prometheus/slo_alerts.yml
docker run --rm -v $(pwd)/prometheus:/etc/prometheus prom/prometheus:latest promtool check rules /etc/prometheus/operational_alerts.yml

# Validate Alertmanager config
docker run --rm -v $(pwd)/alertmanager:/etc/alertmanager prom/alertmanager:latest amtool check-config /etc/alertmanager/alertmanager.yml
```

### 3. Environment Setup

```bash
# Check .env file exists
cat .env

# Should contain:
# GRAFANA_PASSWORD=<your_password>

# Set secure password if using default
sed -i 's/GRAFANA_PASSWORD=admin/GRAFANA_PASSWORD='$(openssl rand -base64 24)'/' .env
```

## 🚀 Deployment Steps

### Step 1: Start Monitoring Stack

```bash
cd monitoring

# Pull all images first
docker-compose pull

# Start services
docker-compose up -d

# Watch logs
docker-compose logs -f
```

### Step 2: Wait for Services to Start

```bash
# Wait for all services to be healthy (may take 1-2 minutes)
watch docker-compose ps

# All services should show "Up" status
# Health checks should pass
```

### Step 3: Verify Each Service

```bash
# Prometheus
curl -s http://localhost:9090/-/healthy
# Expected: Prometheus is Healthy.

# Grafana
curl -s http://localhost:3000/api/health
# Expected: {"database":"ok","version":"..."}

# Alertmanager
curl -s http://localhost:9093/-/healthy
# Expected: Alertmanager is Healthy.

# Jaeger
curl -s http://localhost:14269/
# Expected: {"status":"Server available"}

# Loki
curl -s http://localhost:3100/ready
# Expected: ready

# Node Exporter
curl -s http://localhost:9100/metrics | head -n 5
# Expected: Prometheus metrics output

# cAdvisor
curl -s http://localhost:8080/healthz
# Expected: ok

# OpenTelemetry Collector
curl -s http://localhost:13133/
# Expected: {"status":"Server available"}
```

## 🔍 Functional Testing

### Test 1: Prometheus Targets

```bash
# Check Prometheus targets status
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# All targets should be "up"
```

Expected output:
```json
{"job":"prometheus","health":"up"}
{"job":"node-exporter","health":"up"}
{"job":"cadvisor","health":"up"}
{"job":"otel-collector","health":"up"}
{"job":"grafana","health":"up"}
{"job":"loki","health":"up"}
{"job":"alertmanager","health":"up"}
{"job":"jaeger","health":"up"}
```

### Test 2: Prometheus Metrics

```bash
# Query Prometheus for basic metrics
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq '.data.result[] | {job: .metric.job, value: .value[1]}'

# All values should be "1"
```

### Test 3: Alert Rules Loaded

```bash
# Check alert rules are loaded
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | {name: .name, rules: (.rules | length)}'

# Should show all alert groups
```

Expected output:
```json
{"name":"slo_availability","rules":4}
{"name":"slo_latency","rules":3}
{"name":"slo_cost","rules":3}
{"name":"slo_provider_reliability","rules":2}
{"name":"system_health","rules":2}
{"name":"resources","rules":8}
```

### Test 4: Grafana Datasources

```bash
# Login to Grafana (get session cookie)
GRAFANA_PASSWORD=$(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)
SESSION=$(curl -s -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d "{\"user\":\"admin\",\"password\":\"$GRAFANA_PASSWORD\"}" \
  -c - | grep grafana_session | awk '{print $7}')

# Check datasources
curl -s http://localhost:3000/api/datasources \
  -H "Cookie: grafana_session=$SESSION" | jq '.[] | {name: .name, type: .type}'
```

Expected output:
```json
{"name":"Prometheus","type":"prometheus"}
{"name":"Loki","type":"loki"}
{"name":"Jaeger","type":"jaeger"}
```

### Test 5: Alertmanager Configuration

```bash
# Check Alertmanager status
curl -s http://localhost:9093/api/v2/status | jq '{cluster: .cluster.status, uptime: .uptime}'

# Check alert receivers
curl -s http://localhost:9093/api/v2/receivers | jq '.[] | .name'
```

### Test 6: Log Ingestion (Loki)

```bash
# Send test log to Loki via Promtail
echo '{"timestamp":"'$(date -u +%s%N)'","level":"info","message":"Test log entry"}' > /tmp/test.log

# Check Loki has logs
curl -s 'http://localhost:3100/loki/api/v1/query?query={job="system"}' | jq '.data.result | length'

# Should return > 0
```

### Test 7: Trace Collection (Jaeger)

```bash
# Check Jaeger is collecting traces
curl -s 'http://localhost:16686/api/services' | jq '.data[]'

# Initially may be empty, should populate after application sends traces
```

## 🧪 Application Integration Tests

### Test 1: Application Metrics Endpoint

```bash
# Check if your application exposes /metrics
curl -s http://localhost:8000/metrics | grep oneflow_

# Should see OneFlow metrics
```

### Test 2: Simulate Application Traffic

```bash
# Send test requests to your application
for i in {1..100}; do
  curl -s http://localhost:8000/api/v1/some-endpoint > /dev/null
  sleep 0.1
done

# Check metrics updated in Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=oneflow_requests_total' | jq '.data.result[0].value[1]'
```

### Test 3: Trigger Test Alert

```bash
# Force an alert to fire (for testing)
# This simulates high error rate

# Method 1: Via Prometheus (manual evaluation)
# Go to http://localhost:9090/alerts and check alert states

# Method 2: Check Alertmanager for active alerts
curl -s http://localhost:9093/api/v2/alerts | jq '.[] | {name: .labels.alertname, state: .status.state}'
```

### Test 4: Verify SLO Metrics

```bash
# Check SLO metrics exist
curl -s 'http://localhost:9090/api/v1/query?query=oneflow_requests_total' | jq '.data.result | length'

# Calculate current error rate
curl -s 'http://localhost:9090/api/v1/query?query=(sum(rate(oneflow_requests_total{status="error"}[5m]))/sum(rate(oneflow_requests_total[5m])))*100' | jq '.data.result[0].value[1]'
```

## 📊 Dashboard Verification

### Access Dashboards

1. **Grafana**: http://localhost:3000
   - Login: admin / (from .env)
   - Check datasources are connected
   - Import example dashboards

2. **Prometheus**: http://localhost:9090
   - Check targets: Status → Targets
   - Check alerts: Alerts
   - Execute test queries

3. **Alertmanager**: http://localhost:9093
   - View alert groups
   - Check silence rules
   - Test notifications

4. **Jaeger**: http://localhost:16686
   - Search for traces
   - View service graph
   - Analyze dependencies

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Common issues:
# 1. Port already in use
netstat -tulpn | grep -E '(3000|9090|9093|16686|3100)'

# 2. Volume permission issues
sudo chown -R 472:472 grafana/  # Grafana UID
sudo chown -R 65534:65534 prometheus/  # Prometheus UID

# 3. Config file syntax error
# Validate configs as shown in Pre-Deployment section
```

### Targets Down in Prometheus

```bash
# Check if service is reachable
docker-compose exec prometheus wget -O- http://node-exporter:9100/metrics

# Check network connectivity
docker network inspect oneflow-monitoring

# Verify service names in prometheus.yml match service names in docker-compose.yml
```

### No Metrics from Application

```bash
# Verify application is in same network or accessible
docker network connect oneflow-monitoring <your-app-container>

# Or update prometheus.yml to use correct target:
# - For Docker Desktop: host.docker.internal:8000
# - For Docker on Linux: 172.17.0.1:8000
# - For same network: app:8000
```

### Grafana Can't Connect to Prometheus

```bash
# Test from Grafana container
docker-compose exec grafana wget -O- http://prometheus:9090/api/v1/query?query=up

# Check datasource URL in Grafana UI
# Should be: http://prometheus:9090
```

### Alerts Not Firing

```bash
# Check alert rule evaluation
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.type=="alerting") | {alert: .name, state: .state, health: .health}'

# Check Alertmanager connection
curl -s http://localhost:9090/api/v1/alertmanagers | jq

# Test alert manually
curl -X POST http://localhost:9093/api/v2/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {"alertname":"TestAlert","severity":"warning"},
    "annotations": {"summary":"Test alert"},
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'"
  }]'
```

## 📈 Performance Benchmarks

After deployment, measure:

```bash
# Prometheus query performance
time curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(up[5m]))'

# Grafana dashboard load time
# Should load in < 2 seconds

# Alert evaluation time
# Check prometheus_rule_evaluation_duration_seconds

# Loki query performance
time curl -s 'http://localhost:3100/loki/api/v1/query?query={job="system"}'
```

## ✅ Success Criteria

- [ ] All Docker containers are running and healthy
- [ ] All Prometheus targets are UP
- [ ] Grafana shows all 3 datasources as connected
- [ ] Alert rules are loaded (check `/rules` endpoint)
- [ ] Alertmanager is receiving alerts from Prometheus
- [ ] Application metrics are visible in Prometheus
- [ ] Logs are flowing to Loki
- [ ] Traces are visible in Jaeger (if instrumented)
- [ ] Dashboards display data correctly
- [ ] Test alert can fire and be silenced

## 🎯 Next Steps

Once verification is complete:

1. ✅ Create custom Grafana dashboards
2. ✅ Configure alert notification channels (Slack, email, PagerDuty)
3. ✅ Set up backup strategy for dashboards and configs
4. ✅ Document runbooks for common alerts
5. ✅ Schedule regular review of SLO thresholds
6. ✅ Implement long-term metrics storage (if needed)
7. ✅ Set up authentication and access control
8. ✅ Configure SSL/TLS for production

---

**Last Updated**: 2025-10-10
**Stack Version**: Prometheus 2.47, Grafana 10.1, Jaeger 1.50, Loki 2.9
