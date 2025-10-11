# Grafana Dashboards Guide

## 📊 Dashboard Overview

This guide provides PromQL queries and configuration for monitoring OneFlow.AI with comprehensive SLO tracking, provider health, cost analysis, and infrastructure metrics.

### Dashboard Naming Convention

All dashboards follow this naming pattern: `OneFlow - [Category] - [Purpose]`

**Available Dashboards:**
1. **OneFlow - SLO - Overview** - Error budget and SLI tracking
2. **OneFlow - Providers - Health** - Provider availability and performance
3. **OneFlow - Application - Overview** - Request metrics and traffic patterns
4. **OneFlow - Cost - Analysis** - Budget utilization and cost tracking
5. **OneFlow - Infrastructure - Resources** - System and container metrics

---

## 🎯 SLO Metrics Reference

### Service Level Objectives (SLOs)

| Metric | Target | Measurement Window | Error Budget |
|--------|--------|-------------------|--------------|
| **Availability** | 99.9% | 30 days rolling | 0.1% (43.2 min/month) |
| **Latency (P95)** | < 2.0s | 5 minutes | N/A |
| **Cost per Request** | < 0.5 credits | 1 hour rolling | N/A |

### Key Metric Definitions

**Error Rate:**
```
Percentage of failed requests (5xx, errors) vs total requests
Formula: (failed_requests / total_requests) * 100
```

**Burn Rate:**
```
Rate at which error budget is consumed relative to SLO target
Formula: (current_error_rate / slo_error_budget) 
Example: 2x burn rate = consuming budget twice as fast as acceptable
```

**Error Budget Remaining:**
```
Percentage of allowed errors still available in the measurement window
Formula: ((slo_target - current_error_rate) / slo_target) * 100
```

---

## 📈 Dashboard 1: OneFlow - SLO - Overview

**Purpose:** Track SLO compliance, error budgets, and burn rates

### Panel: Error Budget Status (Gauge)

**Query:**
```promql
# Error Budget Remaining (percentage)
(0.001 - (1 - (
  sum(rate(oneflow_requests_total{status=~"success|2.."}[30d]))
  /
  sum(rate(oneflow_requests_total[30d]))
))) / 0.001 * 100
```

**Configuration:**
- **Type:** Gauge
- **Unit:** Percent (0-100)
- **Thresholds:**
  - 🔴 Red: 0-20% (Critical - SLO at risk)
  - 🟠 Orange: 20-50% (Warning - monitor closely)
  - 🟡 Yellow: 50-80% (Caution)
  - 🟢 Green: 80-100% (Healthy)

---

### Panel: Availability SLI (Time Series)

**Query:**
```promql
# Success Rate over time (1h windows)
sum(rate(oneflow_requests_total{status=~"success|2.."}[1h]))
/
sum(rate(oneflow_requests_total[1h]))
* 100
```

**Configuration:**
- **Type:** Time series
- **Unit:** Percent (%)
- **Y-axis:** 99.0 - 100.0
- **Target line:** 99.9% (SLO threshold)
- **Legend:** "Availability %"

---

### Panel: Latency SLI (Gauge)

**Query:**
```promql
# P95 Latency
histogram_quantile(0.95,
  sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le)
)
```

**Configuration:**
- **Type:** Gauge
- **Unit:** Seconds (s)
- **Max:** 5
- **Thresholds:**
  - 🟢 Green: < 1s
  - 🟡 Yellow: 1-2s
  - 🔴 Red: > 2s

---

### Panel: Cost SLI (Stat Panel)

**Query:**
```promql
# Average Cost Per Request
sum(rate(oneflow_total_cost_credits[1h]))
/
sum(rate(oneflow_requests_total{status="success"}[1h]))
```

**Configuration:**
- **Type:** Stat
- **Unit:** Credits
- **Decimals:** 3
- **Thresholds:**
  - 🟢 Green: < 0.3
  - 🟡 Yellow: 0.3-0.5
  - 🔴 Red: > 0.5

---

### Panel: Burn Rate Heatmap

**Query 1 (1-hour):**
```promql
# 1-hour burn rate
(
  sum(rate(oneflow_requests_total{status=~"error|5.."}[1h]))
  /
  sum(rate(oneflow_requests_total[1h]))
) / 0.001
```

**Query 2 (6-hour):**
```promql
# 6-hour burn rate
(
  sum(rate(oneflow_requests_total{status=~"error|5.."}[6h]))
  /
  sum(rate(oneflow_requests_total[6h]))
) / 0.001
```

**Configuration:**
- **Type:** Time series (multi-line)
- **Legend:** "1h burn rate", "6h burn rate"
- **Alert thresholds:**
  - 1h > 14.4 (budget consumed in 2 days)
  - 6h > 6 (budget consumed in 5 days)

---

## 🏥 Dashboard 2: OneFlow - Providers - Health

**Purpose:** Monitor provider availability, latency, and circuit breaker status

### Panel: Provider Availability (Bar Gauge)

**Query:**
```promql
# Per-Provider Success Rate
sum(rate(oneflow_requests_total{status="success"}[5m])) by (provider)
/
sum(rate(oneflow_requests_total[5m])) by (provider)
* 100
```

**Configuration:**
- **Type:** Bar gauge (horizontal)
- **Unit:** Percent (%)
- **Min:** 95, **Max:** 100
- **Thresholds:**
  - 🟢 Green: > 99.5%
  - 🟡 Yellow: 99.0-99.5%
  - 🔴 Red: < 99.0%

---

### Panel: Provider Latency Comparison (Time Series)

**Query:**
```promql
# P95 by Provider
histogram_quantile(0.95,
  sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le, provider)
)
```

**Configuration:**
- **Type:** Time series
- **Unit:** Seconds
- **Legend:** {{provider}}
- **Reference line:** 2.0s (SLO threshold)

---

### Panel: Provider Cost Efficiency (Table)

**Query:**
```promql
# Cost per request by provider
sum(rate(oneflow_total_cost_credits[1h])) by (provider)
/
sum(rate(oneflow_requests_total{status="success"}[1h])) by (provider)
```

**Configuration:**
- **Type:** Table
- **Columns:** Provider, Cost/Request, Change (1h)
- **Sort:** Cost/Request (descending)
- **Cell colors:** Gradient (low cost = green)

---

### Panel: Circuit Breaker Status (Stat Panel)

**Query:**
```promql
# Circuit breaker states
oneflow_circuit_breaker_state{provider!=""}
```

**Configuration:**
- **Type:** Stat panel (multi-instance)
- **Value mappings:**
  - 0 = "🟢 Closed (Healthy)"
  - 1 = "🔴 Open (Failing)"
  - 2 = "🟡 Half-Open (Testing)"
- **Repeat:** by provider variable

---

## 🚀 Dashboard 3: OneFlow - Application - Overview

**Purpose:** General application health and traffic patterns

### Panel: Request Rate (Time Series)

**Query:**
```promql
sum(rate(oneflow_requests_total[5m]))
```

**Configuration:**
- **Type:** Time series
- **Unit:** req/s
- **Legend:** "Total Requests/sec"

---

### Panel: Error Rate (Graph)

**Query:**
```promql
sum(rate(oneflow_requests_total{status=~"error|5.."}[5m]))
/
sum(rate(oneflow_requests_total[5m]))
* 100
```

**Configuration:**
- **Type:** Time series
- **Unit:** Percent
- **Alert line:** 0.1% (SLO threshold)
- **Fill:** gradient (opacity 0.2)

---

### Panel: Request Duration Distribution (Histogram)

**Query:**
```promql
# Histogram of request durations
sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le)
```

**Configuration:**
- **Type:** Heatmap
- **Unit:** Seconds
- **Color scheme:** Blue-Green-Yellow-Red
- **Data format:** Time series buckets

---

### Panel: Top Endpoints by Traffic (Bar Chart)

**Query:**
```promql
topk(10,
  sum(rate(oneflow_requests_total[5m])) by (endpoint)
)
```

**Configuration:**
- **Type:** Bar chart
- **Orientation:** Horizontal
- **Sort:** Descending
- **Legend:** {{endpoint}}

---

### Panel: Top Endpoints by Latency (Table)

**Query:**
```promql
topk(10,
  histogram_quantile(0.95,
    sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le, endpoint)
  )
)
```

**Configuration:**
- **Type:** Table
- **Columns:** Endpoint, P95 Latency, Request Count
- **Sort:** P95 Latency (descending)
- **Threshold:** > 2s (red highlight)

---

## 💰 Dashboard 4: OneFlow - Cost - Analysis

**Purpose:** Track spending, budget utilization, and cost optimization

### Panel: Total Cost Over Time (Graph)

**Query:**
```promql
sum(increase(oneflow_total_cost_credits[1h]))
```

**Configuration:**
- **Type:** Time series
- **Unit:** Credits
- **Legend:** "Total Cost (1h)"
- **Fill:** gradient

---

### Panel: Cost by Provider (Pie Chart)

**Query:**
```promql
sum(increase(oneflow_total_cost_credits[1h])) by (provider)
```

**Configuration:**
- **Type:** Pie chart
- **Legend:** {{provider}}
- **Value:** Credits
- **Display:** Percentage + value

---

### Panel: Top Users by Cost (Table)

**Query:**
```promql
topk(10,
  sum(increase(oneflow_total_cost_credits[24h])) by (user_id)
)
```

**Configuration:**
- **Type:** Table
- **Columns:** User ID, 24h Cost, 7d Cost, 30d Cost
- **Sort:** 24h Cost (descending)

---

### Panel: Budget Utilization (Gauge)

**Query:**
```promql
# Daily budget utilization
oneflow_budget_utilization_percent{period="daily"}
```

**Query 2:**
```promql
# Monthly budget utilization
oneflow_budget_utilization_percent{period="monthly"}
```

**Configuration:**
- **Type:** Gauge (2 panels side-by-side)
- **Unit:** Percent
- **Thresholds:**
  - 🟢 Green: < 80%
  - 🟡 Yellow: 80-95%
  - 🔴 Red: > 95%

---

## 🖥️ Dashboard 5: OneFlow - Infrastructure - Resources

**Purpose:** Monitor system resources and container performance

### Panel: CPU Usage (Time Series)

**Query:**
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Configuration:**
- **Type:** Time series
- **Unit:** Percent
- **Max:** 100
- **Alert line:** 80%

---

### Panel: Memory Usage (Gauge)

**Query:**
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Configuration:**
- **Type:** Gauge
- **Unit:** Percent
- **Thresholds:**
  - 🟢 Green: < 70%
  - 🟡 Yellow: 70-85%
  - 🔴 Red: > 85%

---

### Panel: Disk Usage (Bar Gauge)

**Query:**
```promql
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100
```

**Configuration:**
- **Type:** Bar gauge
- **Unit:** Percent
- **Max:** 100
- **Critical:** 85%

---

### Panel: Network I/O (Graph)

**Query (Receive):**
```promql
rate(node_network_receive_bytes_total{device!="lo"}[5m])
```

**Query (Transmit):**
```promql
rate(node_network_transmit_bytes_total{device!="lo"}[5m])
```

**Configuration:**
- **Type:** Time series
- **Unit:** Bytes/sec
- **Legend:** "Receive", "Transmit"
- **Stack:** No

---

## 🎨 Dashboard Variables

Add these template variables for dynamic filtering:

### Variable: provider
```
Type: Query
Query: label_values(oneflow_requests_total, provider)
Name: provider
Multi-value: Yes
Include All: Yes
Refresh: On Dashboard Load
```

### Variable: environment
```
Type: Custom
Name: environment
Values: production,staging,development
Default: production
```

### Variable: interval
```
Type: Interval
Name: interval
Values: 1m,5m,10m,30m,1h,6h,12h,1d
Auto: Yes
Default: 5m
```

### Variable: user_id
```
Type: Query
Query: label_values(oneflow_requests_total, user_id)
Name: user_id
Multi-value: Yes
Include All: Yes
```

---

## 📥 Quick Import Instructions

### Method 1: Manual Dashboard Creation

1. **Access Grafana:** http://localhost:3000
2. **Login:** admin / admin (or your configured password)
3. **Create Dashboard:**
   - Click **+ → Dashboard → Add new panel**
   - Select **Prometheus** data source
   - Copy-paste queries from this guide
   - Configure visualization type and thresholds
   - Click **Apply** → **Save Dashboard**
4. **Add Variables:**
   - Dashboard settings (gear icon) → Variables → Add variable
   - Configure as per "Dashboard Variables" section

### Method 2: Import Community Dashboards

**Useful Community Dashboards:**

| Dashboard | ID | Purpose |
|-----------|----|---------| 
| Node Exporter Full | 1860 | System metrics (CPU, RAM, Disk, Network) |
| Docker Container Metrics | 193 | Container monitoring via cAdvisor |
| Prometheus 2.0 Stats | 3662 | Prometheus internal metrics |

**Import Process:**
1. Go to **Dashboards → Import**
2. Enter dashboard ID (e.g., 1860)
3. Select **Prometheus** as data source
4. Click **Import**

### Method 3: Provision via Configuration

**Create:** `monitoring/grafana/provisioning/dashboards/oneflow.yml`

```yaml
apiVersion: 1

providers:
  - name: 'OneFlow Dashboards'
    orgId: 1
    folder: 'OneFlow'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

Then place JSON dashboard files in: `monitoring/grafana/dashboards/`

---

## 🔧 Alert Annotations

Add alert markers to dashboards:

```json
{
  "annotations": {
    "list": [
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "ALERTS{alertstate=\"firing\"}",
        "iconColor": "red",
        "name": "Active Alerts",
        "tagKeys": "alertname,severity",
        "textFormat": "{{alertname}}: {{annotations.summary}}",
        "titleFormat": "🚨 Alert"
      },
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "ALERTS{alertstate=\"pending\"}",
        "iconColor": "orange",
        "name": "Pending Alerts",
        "titleFormat": "⚠️ Warning"
      }
    ]
  }
}
```

---

## 📊 Color Coding Standards

### SLO Status
- 🟢 **Green (Healthy):** Error budget > 80% remaining
- 🟡 **Yellow (Warning):** Error budget 50-80% remaining
- 🟠 **Orange (Critical):** Error budget 20-50% remaining
- 🔴 **Red (Violation):** Error budget < 20% remaining

### Performance Metrics
**Latency:**
- 🟢 Green: < 1s (Excellent)
- 🟡 Yellow: 1-2s (Acceptable)
- 🔴 Red: > 2s (SLO violation)

**Error Rate:**
- 🟢 Green: < 0.05% (Well within SLO)
- 🟡 Yellow: 0.05-0.1% (Approaching SLO)
- 🔴 Red: > 0.1% (SLO violation)

**Cost:**
- 🟢 Green: < 0.3 credits (Efficient)
- 🟡 Yellow: 0.3-0.5 credits (Target)
- 🔴 Red: > 0.5 credits (Over budget)

---

## 💡 Best Practices

### Dashboard Design
1. **Start with SLO Dashboard** - Most critical metrics first
2. **Use Rows for Organization** - Group related panels
3. **Optimize Panel Heights** - 6-8 units for graphs, 4 for stats
4. **Mobile Responsive** - Test on smaller screens
5. **Consistent Time Ranges** - Use $__interval variable

### Query Optimization
1. **Use Recording Rules** - Pre-calculate complex queries in Prometheus
2. **Appropriate Time Windows** - Match to data granularity
3. **Avoid High Cardinality** - Limit `by` clause labels
4. **Test in Prometheus First** - Verify queries before adding to Grafana
5. **Use `rate()` for Counters** - Never use raw counter values

### Performance Tips
1. **Limit Data Points** - Use `max_data_points` parameter
2. **Dashboard Caching** - Enable for static dashboards
3. **Reduce Panel Count** - < 20 panels per dashboard ideal
4. **Use Variables** - Reuse queries with filters
5. **Set Query Timeout** - Prevent slow queries from blocking

### Maintenance
1. **Version Control** - Export dashboards to git as JSON
2. **Documentation** - Add panel descriptions
3. **Regular Reviews** - Update queries quarterly
4. **Test Alerts** - Verify firing conditions
5. **Archive Unused** - Remove deprecated dashboards

---

## 🔍 Troubleshooting

### Common Issues

**No Data Displayed:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify metrics exist
curl http://localhost:9090/api/v1/label/__name__/values | grep oneflow

# Check application metrics endpoint
curl http://localhost:8000/metrics
```

**Slow Queries:**
- Add `step` parameter to reduce resolution
- Use recording rules for complex calculations
- Increase Prometheus retention for aggregations

**Missing Labels:**
- Verify relabel_configs in prometheus.yml
- Check metric exposition format
- Ensure labels are applied consistently

---

## 📚 Additional Resources

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [PromQL Tutorial](https://promlabs.com/promql-cheat-sheet/)
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [SLO Workshop](https://github.com/grafana/slo-workshop)
- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)

---

## 🚀 Quick Start Checklist

- [ ] Start monitoring stack: `docker-compose up -d`
- [ ] Access Grafana: http://localhost:3000
- [ ] Verify Prometheus data source connection
- [ ] Import Node Exporter dashboard (ID: 1860)
- [ ] Create SLO Overview dashboard
- [ ] Configure dashboard variables (provider, interval)
- [ ] Set up alert annotations
- [ ] Add team members and set permissions
- [ ] Export dashboards to version control
- [ ] Schedule regular dashboard reviews

---

**Last Updated:** October 2025  
**Maintainer:** Platform Team  
**Slack Channel:** #observability
