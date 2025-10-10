# Grafana Dashboards Guide

## 📊 Required Dashboards

Create the following dashboards in Grafana:

### 1. SLO Overview Dashboard

**Key Panels:**

#### Error Budget Status
```promql
# Current Error Rate (30d rolling window)
1 - (
  sum(rate(oneflow_requests_total{status=~"success|2.."}[30d]))
  /
  sum(rate(oneflow_requests_total[30d]))
)

# Error Budget Remaining
(0.001 - (1 - (
  sum(rate(oneflow_requests_total{status=~"success|2.."}[30d]))
  /
  sum(rate(oneflow_requests_total[30d]))
))) / 0.001 * 100
```

#### Availability SLI (Time Series)
```promql
# Success Rate (1h windows)
sum(rate(oneflow_requests_total{status=~"success|2.."}[1h]))
/
sum(rate(oneflow_requests_total[1h]))

# Display as percentage (multiply by 100)
```

#### Latency SLI (Gauge)
```promql
# P95 Latency
histogram_quantile(0.95,
  sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le)
)

# Threshold: 2.0 seconds
```

#### Cost SLI (Stat)
```promql
# Average Cost Per Request
sum(rate(oneflow_total_cost_credits[1h]))
/
sum(rate(oneflow_requests_total{status="success"}[1h]))

# Threshold: 0.5 credits
```

#### Burn Rate Visualization (Heatmap)
```promql
# 1-hour burn rate
(
  sum(rate(oneflow_requests_total{status=~"error|5.."}[1h]))
  /
  sum(rate(oneflow_requests_total[1h]))
) / 0.001

# 6-hour burn rate
(
  sum(rate(oneflow_requests_total{status=~"error|5.."}[6h]))
  /
  sum(rate(oneflow_requests_total[6h]))
) / 0.001
```

### 2. Provider Health Dashboard

**Key Panels:**

#### Provider Availability
```promql
# Per-Provider Success Rate
sum(rate(oneflow_requests_total{status="success"}[5m])) by (provider)
/
sum(rate(oneflow_requests_total[5m])) by (provider)
```

#### Provider Latency
```promql
# P95 by Provider
histogram_quantile(0.95,
  sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le, provider)
)
```

#### Provider Cost Efficiency
```promql
# Cost per request by provider
sum(rate(oneflow_total_cost_credits[1h])) by (provider)
/
sum(rate(oneflow_requests_total{status="success"}[1h])) by (provider)
```

#### Circuit Breaker Status
```promql
# Circuit breaker states
oneflow_circuit_breaker_state{provider!=""}

# 0 = closed (healthy)
# 1 = open (failing)
# 2 = half-open (testing)
```

### 3. Application Overview Dashboard

**Key Panels:**

#### Request Rate
```promql
sum(rate(oneflow_requests_total[5m]))
```

#### Error Rate
```promql
sum(rate(oneflow_requests_total{status=~"error|5.."}[5m]))
/
sum(rate(oneflow_requests_total[5m]))
* 100
```

#### Request Duration Distribution
```promql
# Histogram of request durations
sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le)
```

#### Top Endpoints by Traffic
```promql
topk(10,
  sum(rate(oneflow_requests_total[5m])) by (endpoint)
)
```

#### Top Endpoints by Latency
```promql
topk(10,
  histogram_quantile(0.95,
    sum(rate(oneflow_request_duration_seconds_bucket[5m])) by (le, endpoint)
  )
)
```

### 4. Cost Analysis Dashboard

**Key Panels:**

#### Total Cost Over Time
```promql
sum(increase(oneflow_total_cost_credits[1h]))
```

#### Cost by Provider
```promql
sum(increase(oneflow_total_cost_credits[1h])) by (provider)
```

#### Top Users by Cost
```promql
topk(10,
  sum(increase(oneflow_total_cost_credits[24h])) by (user_id)
)
```

#### Budget Utilization
```promql
oneflow_budget_utilization_percent{period="daily"}
oneflow_budget_utilization_percent{period="monthly"}
```

### 5. Infrastructure Dashboard

**Key Panels:**

#### CPU Usage
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

#### Memory Usage
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

#### Disk Usage
```promql
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

#### Network I/O
```promql
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

## 🎨 Dashboard Creation Steps

### Using Grafana UI

1. **Log in to Grafana**: http://localhost:3000
2. Click **+** → **Dashboard** → **Add new panel**
3. Select **Prometheus** as data source
4. Enter query from above
5. Configure visualization type (Time series, Stat, Gauge, etc.)
6. Set thresholds and colors
7. Save panel and dashboard

### Color Coding Standards

**SLO Status:**
- 🟢 Green: Within SLO (< 80% budget consumed)
- 🟡 Yellow: Warning (80-95% budget consumed)
- 🔴 Red: Critical (> 95% budget consumed)

**Latency:**
- 🟢 Green: < 1s
- 🟡 Yellow: 1-2s
- 🔴 Red: > 2s

**Error Rate:**
- 🟢 Green: < 0.05%
- 🟡 Yellow: 0.05-0.1%
- 🔴 Red: > 0.1%

## 📥 Import Pre-built Dashboards

You can import community dashboards:

1. **Node Exporter Full**: Dashboard ID `1860`
   - System metrics (CPU, Memory, Disk, Network)

2. **Docker Container & Host Metrics**: Dashboard ID `193`
   - Container metrics from cAdvisor

3. **Prometheus Stats**: Dashboard ID `3662`
   - Prometheus internal metrics

### Import Process

1. Go to Grafana → **Dashboards** → **Import**
2. Enter dashboard ID
3. Select **Prometheus** as data source
4. Click **Import**

## 🔧 Dashboard Variables

Add these variables for filtering:

### Provider Variable
```
Query: label_values(oneflow_requests_total, provider)
Name: provider
Type: Query
Multi-value: Yes
Include All: Yes
```

### Time Range Variable
```
Type: Interval
Name: interval
Values: 1m,5m,10m,30m,1h,6h,12h,1d
Auto: Yes
```

### Environment Variable
```
Name: environment
Type: Custom
Values: production,staging,development
```

## 📊 Panel Examples in JSON

### Error Budget Panel (Gauge)

```json
{
  "type": "gauge",
  "title": "Error Budget Remaining",
  "targets": [
    {
      "expr": "(0.001 - (1 - (sum(rate(oneflow_requests_total{status=~\"success|2..\"}[30d])) / sum(rate(oneflow_requests_total[30d]))))) / 0.001 * 100",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": 0, "color": "red" },
          { "value": 20, "color": "orange" },
          { "value": 50, "color": "yellow" },
          { "value": 80, "color": "green" }
        ]
      }
    }
  }
}
```

### Request Rate Panel (Time Series)

```json
{
  "type": "timeseries",
  "title": "Request Rate",
  "targets": [
    {
      "expr": "sum(rate(oneflow_requests_total[5m]))",
      "legendFormat": "Total Requests",
      "refId": "A"
    },
    {
      "expr": "sum(rate(oneflow_requests_total{status='success'}[5m]))",
      "legendFormat": "Successful",
      "refId": "B"
    },
    {
      "expr": "sum(rate(oneflow_requests_total{status='error'}[5m]))",
      "legendFormat": "Errors",
      "refId": "C"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "custom": {
        "drawStyle": "line",
        "fillOpacity": 10
      }
    }
  }
}
```

## 🎯 Alert Annotations

Add alert annotations to dashboards:

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
        "titleFormat": "Alert"
      }
    ]
  }
}
```

## 📱 Responsive Design Tips

1. Use **rows** to organize panels logically
2. Set panel heights appropriately (6-8 units for graphs)
3. Use **stat** panels for single values
4. Use **time series** for trends
5. Use **tables** for detailed breakdowns
6. Keep critical metrics above the fold

## 🔍 Useful Panel Configurations

### SLO Compliance Table

```promql
# Query for table
label_replace(
  (
    1 - (
      sum(rate(oneflow_requests_total{status=~"success|2.."}[30d])) by (provider)
      /
      sum(rate(oneflow_requests_total[30d])) by (provider)
    )
  ) < bool 0.001,
  "status", "✅ Compliant", "", ""
)
or
label_replace(
  (
    1 - (
      sum(rate(oneflow_requests_total{status=~"success|2.."}[30d])) by (provider)
      /
      sum(rate(oneflow_requests_total[30d])) by (provider)
    )
  ) >= bool 0.001,
  "status", "❌ Violation", "", ""
)
```

### Burn Rate Heatmap

- **Type**: Heatmap
- **Data format**: Time series buckets
- **Y-Axis**: Burn rate multiplier
- **Color scheme**: Red-Yellow-Green (reversed)

## 💡 Best Practices

1. **Start Simple**: Begin with basic metrics, add complexity as needed
2. **Use Templating**: Variables make dashboards reusable
3. **Set Appropriate Time Ranges**: Use `$__interval` for auto-adjustment
4. **Add Descriptions**: Panel descriptions help team understanding
5. **Link Dashboards**: Create drill-down paths (Overview → Provider Detail → Trace)
6. **Test Queries**: Verify in Prometheus before adding to Grafana
7. **Version Control**: Export dashboards as JSON and commit to git
8. **Consistent Naming**: Use clear, descriptive panel titles
9. **Group Related Metrics**: Use rows to organize panels
10. **Document Thresholds**: Note SLO targets in panel descriptions

## 🚀 Quick Dashboard Setup

Run this in your terminal to create a basic SLO dashboard:

```bash
# This would be a Python script to auto-generate dashboards
# For now, use the Grafana UI or import community dashboards
```

## 📖 Additional Resources

- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [SLO Workshop Dashboards](https://github.com/grafana/slo-workshop)
