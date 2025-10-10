# 🚀 OneFlow.AI Monitoring - 15-Minute Quickstart

Get your complete monitoring stack running in 15 minutes.

## ⏱️ Quick Setup (15 minutes)

### Prerequisites
- Docker & Docker Compose installed
- 8GB RAM available
- 10GB disk space

### Step 1: Download Files (2 min)

```bash
# Clone or create monitoring directory
mkdir -p monitoring && cd monitoring

# Create directory structure
mkdir -p {prometheus,grafana/{provisioning/{datasources,dashboards},dashboards},otel,loki,promtail,alertmanager}
```

### Step 2: Copy Configuration Files (5 min)

Copy these files from the artifacts I created:

| File | Artifact Name | Destination |
|------|---------------|-------------|
| docker-compose.yml | "docker-compose.yml - Production Ready" | `monitoring/docker-compose.yml` |
| prometheus.yml | "prometheus.yml - Production Ready" | `monitoring/prometheus/prometheus.yml` |
| slo_alerts.yml | "slo_alerts.yml - SLO-Based Alerts" | `monitoring/prometheus/slo_alerts.yml` |
| operational_alerts.yml | "operational_alerts.yml" | `monitoring/prometheus/operational_alerts.yml` |
| datasources.yml | "datasources.yml" | `monitoring/grafana/provisioning/datasources/datasources.yml` |
| dashboards.yml | "dashboards.yml" | `monitoring/grafana/provisioning/dashboards/dashboards.yml` |
| otel-collector-config.yml | From your documents | `monitoring/otel/otel-collector-config.yml` |

### Step 3: Run Quick Setup Script (3 min)

```bash
cd monitoring

# Create and run setup
cat > setup-quick.sh << 'EOF'
#!/bin/bash
set -e

# Loki config
cat > loki/loki-config.yml << 'LOKI'
auth_enabled: false
server:
  http_listen_port: 3100
common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h
LOKI

# Promtail config
cat > promtail/promtail-config.yml << 'PROMTAIL'
server:
  http_listen_port: 9080
positions:
  filename: /tmp/positions.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
  - job_name: system
    static_configs:
      - targets: [localhost]
        labels:
          job: varlogs
          __path__: /var/log/*log
  - job_name: oneflow
    static_configs:
      - targets: [localhost]
        labels:
          job: oneflow
          __path__: /var/lib/oneflow/logs/*.log
PROMTAIL

# Alertmanager config
cat > alertmanager/alertmanager.yml << 'ALERTMGR'
global:
  resolve_timeout: 5m
route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical'
      repeat_interval: 4h
    - match:
        category: slo
      receiver: 'slo'
      repeat_interval: 6h
receivers:
  - name: 'default'
  - name: 'critical'
  - name: 'slo'
ALERTMGR

# .env file
echo "GRAFANA_PASSWORD=$(openssl rand -base64 24 2>/dev/null || echo 'admin123')" > .env

echo "✅ Setup complete!"
EOF

chmod +x setup-quick.sh
./setup-quick.sh
```

### Step 4: Start Stack (2 min)

```bash
# Pull images (first time only)
docker-compose pull

# Start all services
docker-compose up -d

# Watch startup logs
docker-compose logs -f
```

### Step 5: Verify (3 min)

```bash
# Wait 60 seconds for services to start
sleep 60

# Quick health check
curl -s http://localhost:9090/-/healthy && echo "✅ Prometheus OK"
curl -s http://localhost:3000/api/health | grep -q ok && echo "✅ Grafana OK"
curl -s http://localhost:9093/-/healthy && echo "✅ Alertmanager OK"

# Check all targets
docker-compose ps
```

Expected output: All services should be "Up (healthy)"

## 🌐 Access Your Stack

| Service | URL | Login |
|---------|-----|-------|
| **Grafana** | http://localhost:3000 | admin / (check `.env`) |
| **Prometheus** | http://localhost:9090 | - |
| **Alertmanager** | http://localhost:9093 | - |
| **Jaeger** | http://localhost:16686 | - |

## ✅ 5-Minute Validation

### 1. Check Prometheus Targets (1 min)

Visit: http://localhost:9090/targets

All should be **UP** (green):
- ✅ prometheus
- ✅ oneflow-api (may be down if app not running yet)
- ✅ node-exporter
- ✅ cadvisor
- ✅ otel-collector
- ✅ grafana
- ✅ loki
- ✅ alertmanager
- ✅ jaeger

### 2. Check Alert Rules (1 min)

Visit: http://localhost:9090/alerts

Should see alert groups:
- ✅ slo_availability (4 rules)
- ✅ slo_latency (3 rules)
- ✅ slo_cost (3 rules)
- ✅ system_health (2 rules)
- ✅ resources (8 rules)

### 3. Login to Grafana (2 min)

1. Visit: http://localhost:3000
2. Login: `admin` / (password from `.env`)
3. Go to **Configuration** → **Data Sources**
4. Verify 3 datasources are connected:
   - ✅ Prometheus (green)
   - ✅ Loki (green)
   - ✅ Jaeger (green)

### 4. Import First Dashboard (1 min)

1. In Grafana: **Dashboards** → **Import**
2. Enter dashboard ID: `1860` (Node Exporter Full)
3. Select **Prometheus** as datasource
4. Click **Import**
5. Should see system metrics!

## 🔧 Common Issues & Fixes

### Issue: Service won't start

```bash
# Check logs
docker-compose logs <service-name>

# Common fix: Port in use
docker-compose down
sudo lsof -ti:3000 | xargs kill -9  # Kill process using port
docker-compose up -d
```

### Issue: Prometheus can't scrape app

```bash
# If your app is running locally (not in Docker):
# Edit prometheus/prometheus.yml:
# Change: host.docker.internal:8000
# To: 172.17.0.1:8000  (Docker bridge IP on Linux)

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### Issue: Grafana datasource not working

```bash
# Test from Grafana container
docker-compose exec grafana wget -O- http://prometheus:9090/api/v1/query?query=up

# If fails, restart stack
docker-compose restart
```

### Issue: High memory usage

```bash
# Reduce Prometheus retention
# Edit docker-compose.yml:
# Change: --storage.tsdb.retention.time=30d
# To: --storage.tsdb.retention.time=7d

docker-compose up -d prometheus
```

## 🎯 Next Steps (After Setup)

### Immediate (Today)
1. ✅ Verify all services are healthy
2. ✅ Import Node Exporter dashboard (ID: 1860)
3. ✅ Get Grafana password from `.env`

### This Week
1. 📊 Create SLO dashboard (see `grafana/dashboards/README.md`)
2. 🔔 Configure Slack/email alerts in `alertmanager/alertmanager.yml`
3. 📈 Instrument your application with metrics
4. 🧪 Send test traffic and verify metrics appear

### This Month
1. 📚 Document runbooks for alerts
2. 🎓 Train team on using Grafana
3. 🔒 Change default passwords
4. 💾 Set up backup strategy

## 📊 Quick Test of Your Application

Once your app is running:

```bash
# Generate test traffic
for i in {1..50}; do
  curl -s http://localhost:8000/metrics > /dev/null
  sleep 0.5
done

# Check if metrics appear in Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=oneflow_requests_total' | jq

# If you see data, success! 🎉
```

## 🆘 Getting Help

### Check Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### Restart Everything
```bash
docker-compose restart
```

### Complete Reset
```bash
# WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d
```

### Check Service Health
```bash
# Create quick health check script
cat > check-health.sh << 'EOF'
#!/bin/bash
echo "Checking services..."
curl -sf http://localhost:9090/-/healthy && echo "✅ Prometheus" || echo "❌ Prometheus"
curl -sf http://localhost:3000/api/health | grep -q ok && echo "✅ Grafana" || echo "❌ Grafana"
curl -sf http://localhost:9093/-/healthy && echo "✅ Alertmanager" || echo "❌ Alertmanager"
curl -sf http://localhost:14269/ && echo "✅ Jaeger" || echo "❌ Jaeger"
curl -sf http://localhost:3100/ready && echo "✅ Loki" || echo "❌ Loki"
curl -sf http://localhost:9100/metrics > /dev/null && echo "✅ Node Exporter" || echo "❌ Node Exporter"
EOF

chmod +x check-health.sh
./check-health.sh
```

## 📖 Full Documentation

For detailed information, see:
- **README.md** - Complete documentation
- **DEPLOYMENT_SUMMARY.md** - Quick reference guide
- **VERIFICATION.md** - Detailed testing procedures
- **grafana/dashboards/README.md** - Dashboard creation guide

## 🎉 Success!

If you can see:
- ✅ All Docker containers running
- ✅ Grafana login page works
- ✅ Prometheus shows targets
- ✅ Node Exporter dashboard displays data

**You're done!** Your monitoring stack is ready. 🚀

---

**Time to complete**: ~15 minutes
**Services deployed**: 9 containers
**Storage used**: ~500MB (initial)
**Memory used**: ~2-3GB

**Pro Tip**: Bookmark these URLs for quick access:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090/graph
- Alerts: http://localhost:9090/alerts

Now instrument your application and start monitoring! 📈
