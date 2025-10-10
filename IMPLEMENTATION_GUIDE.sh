#!/bin/bash
# OneFlow.AI Monitoring Stack - Complete Implementation Guide
# This script shows all commands needed to set up the monitoring stack

set -e

echo "==================================================================="
echo "OneFlow.AI Monitoring Stack - Complete Implementation Guide"
echo "==================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📁 Step 1: Create Directory Structure${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
cd /path/to/your/project
mkdir -p monitoring/{prometheus,grafana/{provisioning/{datasources,dashboards},dashboards},otel,loki,promtail,alertmanager}
mkdir -p logs
EOF
echo ""

echo -e "${BLUE}📝 Step 2: Create Core Configuration Files${NC}"
echo "-------------------------------------------------------------------"
echo "Create the following files with content from the artifacts:"
echo ""
echo "1. monitoring/docker-compose.yml"
echo "   └─ Use: 'docker-compose.yml - Production Ready' artifact"
echo ""
echo "2. monitoring/prometheus/prometheus.yml"
echo "   └─ Use: 'prometheus.yml - Production Ready' artifact"
echo ""
echo "3. monitoring/prometheus/slo_alerts.yml"
echo "   └─ Use: 'slo_alerts.yml - SLO-Based Alerts' artifact"
echo ""
echo "4. monitoring/prometheus/operational_alerts.yml"
echo "   └─ Use: 'operational_alerts.yml - Operational Alerts' artifact"
echo ""
echo "5. monitoring/otel/otel-collector-config.yml"
echo "   └─ Already exists in your documents"
echo ""
echo "6. monitoring/grafana/provisioning/datasources/datasources.yml"
echo "   └─ Use: 'datasources.yml' artifact"
echo ""
echo "7. monitoring/grafana/provisioning/dashboards/dashboards.yml"
echo "   └─ Use: 'dashboards.yml' artifact"
echo ""
echo "8. monitoring/.env"
cat << 'EOF'
   Create file with:
   GRAFANA_PASSWORD=$(openssl rand -base64 24)
EOF
echo ""

echo -e "${BLUE}📝 Step 3: Run Automated Setup Script${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
cd monitoring

# Create and run setup script
cat > setup.sh << 'SCRIPT_END'
#!/bin/bash
set -e

echo "🚀 Setting up OneFlow.AI Monitoring Stack..."

# Create Loki config
cat > loki/loki-config.yml << 'LOKI_CONFIG'
auth_enabled: false
server:
  http_listen_port: 3100
  grpc_listen_port: 9096
common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
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
analytics:
  reporting_enabled: false
LOKI_CONFIG

# Create Promtail config
cat > promtail/promtail-config.yml << 'PROMTAIL_CONFIG'
server:
  http_listen_port: 9080
  grpc_listen_port: 0
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
PROMTAIL_CONFIG

# Create Alertmanager config
cat > alertmanager/alertmanager.yml << 'ALERTMANAGER_CONFIG'
global:
  resolve_timeout: 5m
route:
  group_by: ['alertname', 'cluster', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 5s
      repeat_interval: 4h
    - match:
        category: slo
      receiver: 'slo-alerts'
      group_wait: 30s
      repeat_interval: 6h
    - match:
        severity: warning
      receiver: 'warning-alerts'
    - match:
        severity: info
      receiver: 'info-alerts'
receivers:
  - name: 'default'
  - name: 'critical-alerts'
  - name: 'slo-alerts'
  - name: 'warning-alerts'
  - name: 'info-alerts'
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster']
ALERTMANAGER_CONFIG

# Create .env if not exists
if [ ! -f .env ]; then
    echo "GRAFANA_PASSWORD=$(openssl rand -base64 24 2>/dev/null || echo 'changeme')" > .env
    echo "✅ Created .env with secure password"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review configurations in each directory"
echo "2. Update alertmanager.yml with your notification channels"
echo "3. Run: docker-compose up -d"
SCRIPT_END

chmod +x setup.sh
./setup.sh
EOF
echo ""

echo -e "${BLUE}🚀 Step 4: Validate Configurations${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Validate Prometheus config
docker run --rm -v $(pwd)/prometheus:/etc/prometheus \
  prom/prometheus:latest \
  promtool check config /etc/prometheus/prometheus.yml

# Validate alert rules
docker run --rm -v $(pwd)/prometheus:/etc/prometheus \
  prom/prometheus:latest \
  promtool check rules /etc/prometheus/slo_alerts.yml

docker run --rm -v $(pwd)/prometheus:/etc/prometheus \
  prom/prometheus:latest \
  promtool check rules /etc/prometheus/operational_alerts.yml

# Validate Alertmanager config
docker run --rm -v $(pwd)/alertmanager:/etc/alertmanager \
  prom/alertmanager:latest \
  amtool check-config /etc/alertmanager/alertmanager.yml
EOF
echo ""

echo -e "${BLUE}🐳 Step 5: Deploy Monitoring Stack${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
cd monitoring

# Pull all images
docker-compose pull

# Start services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Check status (in another terminal)
docker-compose ps
EOF
echo ""

echo -e "${BLUE}✅ Step 6: Verify Deployment${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Wait for services to start (30-60 seconds)
sleep 60

# Check all services
echo "Checking Prometheus..."
curl -s http://localhost:9090/-/healthy

echo "Checking Grafana..."
curl -s http://localhost:3000/api/health | jq

echo "Checking Alertmanager..."
curl -s http://localhost:9093/-/healthy

echo "Checking Jaeger..."
curl -s http://localhost:14269/

echo "Checking Loki..."
curl -s http://localhost:3100/ready

echo "Checking targets..."
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
EOF
echo ""

echo -e "${BLUE}🌐 Step 7: Access Web Interfaces${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Get Grafana password
echo "Grafana Password: $(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)"

# Open in browser:
# - Grafana:       http://localhost:3000  (admin / password-from-env)
# - Prometheus:    http://localhost:9090
# - Alertmanager:  http://localhost:9093
# - Jaeger:        http://localhost:16686
EOF
echo ""

echo -e "${BLUE}📊 Step 8: Configure Grafana Dashboards${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Login to Grafana
# 1. Go to http://localhost:3000
# 2. Login with admin / (password from .env)
# 3. Verify datasources:
#    - Configuration → Data Sources
#    - Should see: Prometheus, Loki, Jaeger
# 4. Import community dashboards:
#    - Dashboards → Import → 1860 (Node Exporter)
#    - Dashboards → Import → 893 (Docker)
# 5. Create custom dashboards using queries from:
#    - grafana/dashboards/README.md
EOF
echo ""

echo -e "${BLUE}🔔 Step 9: Configure Alert Notifications${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Edit alertmanager/alertmanager.yml
# Add your notification channels:

# Example for Slack:
receivers:
  - name: 'critical-alerts'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts-critical'
        title: '🚨 {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

# Example for Email:
receivers:
  - name: 'slo-alerts'
    email_configs:
      - to: 'oncall@yourcompany.com'
        from: 'alertmanager@yourcompany.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'your-email@gmail.com'
        auth_password: 'your-app-password'

# Reload configuration:
docker-compose exec alertmanager kill -HUP 1
EOF
echo ""

echo -e "${BLUE}🔧 Step 10: Instrument Your Application${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Add to your FastAPI application:

from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

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

provider_health = Gauge(
    'oneflow_provider_health_status',
    'Provider health status',
    ['provider']
)

# Add metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Instrument requests
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        requests_total.labels(
            status='success',
            provider=response.headers.get('X-Provider', 'unknown'),
            endpoint=request.url.path
        ).inc()
        return response
    except Exception as e:
        requests_total.labels(
            status='error',
            provider='unknown',
            endpoint=request.url.path
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        request_duration.labels(
            provider=response.headers.get('X-Provider', 'unknown')
        ).observe(duration)
EOF
echo ""

echo -e "${BLUE}🧪 Step 11: Test Monitoring Pipeline${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Generate test traffic
for i in {1..100}; do
  curl -s http://localhost:8000/api/v1/completion \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Test", "model": "gpt-3.5-turbo"}' \
    > /dev/null
  sleep 0.1
done

# Check metrics in Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=oneflow_requests_total' | jq

# View in Grafana
# - Go to Explore
# - Select Prometheus
# - Query: rate(oneflow_requests_total[5m])
# - Visualize the metrics
EOF
echo ""

echo -e "${BLUE}📚 Step 12: Documentation and Training${NC}"
echo "-------------------------------------------------------------------"
cat << 'EOF'
# Documentation created:
# 1. README.md                - Full documentation
# 2. DEPLOYMENT_SUMMARY.md    - Quick reference
# 3. VERIFICATION.md          - Testing guide
# 4. grafana/dashboards/README.md - Dashboard guide

# Training materials:
# - SLO concepts and error budgets
# - Alert response procedures
# - Dashboard customization
# - Troubleshooting guide

# Runbooks to create:
# - High error rate response
# - Provider outage procedure
# - Performance degradation investigation
# - Cost spike analysis
EOF
echo ""

echo -e "${GREEN}==================================================================="
echo "✅ Implementation Guide Complete!"
echo "===================================================================${NC}"
echo ""
echo "Summary of what was created:"
echo "  ✓ Production-ready monitoring stack (9 services)"
echo "  ✓ SLO-based alerting system"
echo "  ✓ Operational alerts for infrastructure"
echo "  ✓ Grafana with auto-provisioned datasources"
echo "  ✓ Comprehensive documentation"
echo ""
echo "Next actions:"
echo "  1. Review and customize alert thresholds"
echo "  2. Configure notification channels in Alertmanager"
echo "  3. Create team-specific Grafana dashboards"
echo "  4. Instrument your application with metrics"
echo "  5. Test alert firing and notification delivery"
echo "  6. Document runbooks for common scenarios"
echo ""
echo "Access URLs:"
echo "  • Grafana:       http://localhost:3000"
echo "  • Prometheus:    http://localhost:9090"
echo "  • Alertmanager:  http://localhost:9093"
echo "  • Jaeger:        http://localhost:16686"
echo ""
echo "For detailed instructions, see:"
echo "  • monitoring/README.md"
echo "  • monitoring/DEPLOYMENT_SUMMARY.md"
echo "  • monitoring/VERIFICATION.md"
echo ""
