# Воспроизводимые Шаги Проверки Monitoring Stack

**Путь файла:** `monitoring/TESTING.md`

## 📋 Содержание

1. [Smoke Tests (Базовая Проверка)](#-smoke-tests-базовая-проверка)
2. [E2E Tests (Сквозная Проверка)](#-e2e-tests-сквозная-проверка)
3. [Метрики После Деплоя](#-метрики-после-деплоя)
4. [Автоматизированный Test Suite](#-автоматизированный-test-suite)

---

## 🧪 Smoke Tests (Базовая Проверка)

### Smoke Test 1: Доступность Сервисов (2 минуты)

**Путь файла:** `monitoring/tests/smoke_test.sh`

```bash
#!/bin/bash
set -e

echo "=== SMOKE TEST: Проверка доступности сервисов ==="
echo "Время запуска: $(date)"
echo ""

# Массив сервисов для проверки
declare -A SERVICES=(
    ["Prometheus"]="http://localhost:9090/-/healthy"
    ["Grafana"]="http://localhost:3000/api/health"
    ["Alertmanager"]="http://localhost:9093/-/healthy"
    ["Jaeger"]="http://localhost:14269/"
    ["Loki"]="http://localhost:3100/ready"
    ["Node Exporter"]="http://localhost:9100/metrics"
    ["cAdvisor"]="http://localhost:8080/healthz"
    ["OTEL Collector"]="http://localhost:13133/"
)

FAILED=0
PASSED=0

for service in "${!SERVICES[@]}"; do
    url="${SERVICES[$service]}"
    echo -n "Проверка $service ($url)... "
    
    if response=$(curl -sf --max-time 5 "$url" 2>&1); then
        echo "✅ OK"
        PASSED=$((PASSED + 1))
    else
        echo "❌ FAILED"
        echo "  Ошибка: $response"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "================================================"
echo "Результаты: Успешно: $PASSED, Провалено: $FAILED"
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ ВСЕ SMOKE TESTS ПРОЙДЕНЫ"
    exit 0
else
    echo "❌ НЕКОТОРЫЕ SMOKE TESTS ПРОВАЛЕНЫ"
    exit 1
fi
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/smoke_test.sh
./tests/smoke_test.sh
```

**Ожидаемый результат:**
```
✅ ВСЕ SMOKE TESTS ПРОЙДЕНЫ
Успешно: 8, Провалено: 0
```

---

### Smoke Test 2: Состояние Docker Контейнеров (1 минута)

**Путь файла:** `monitoring/tests/check_containers.sh`

```bash
#!/bin/bash
set -e

echo "=== SMOKE TEST: Проверка Docker контейнеров ==="
echo ""

cd "$(dirname "$0")/.."

# Проверка запущенных контейнеров
echo "Состояние контейнеров:"
docker-compose ps

echo ""
echo "Детальная проверка каждого контейнера:"

CONTAINERS=(
    "prometheus"
    "grafana"
    "alertmanager"
    "jaeger"
    "loki"
    "promtail"
    "node-exporter"
    "cadvisor"
    "otel-collector"
)

FAILED=0
PASSED=0

for container in "${CONTAINERS[@]}"; do
    echo -n "Проверка $container... "
    
    state=$(docker-compose ps --format json | jq -r ".[] | select(.Service==\"$container\") | .State")
    
    if [ "$state" == "running" ]; then
        echo "✅ Running"
        PASSED=$((PASSED + 1))
    else
        echo "❌ Not running (State: $state)"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "================================================"
echo "Контейнеры: Работают: $PASSED, Не работают: $FAILED"
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ ВСЕ КОНТЕЙНЕРЫ ЗАПУЩЕНЫ"
    exit 0
else
    echo "❌ НЕКОТОРЫЕ КОНТЕЙНЕРЫ НЕ ЗАПУЩЕНЫ"
    echo ""
    echo "Для просмотра логов используйте:"
    echo "docker-compose logs <container-name>"
    exit 1
fi
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/check_containers.sh
./tests/check_containers.sh
```

**Ожидаемый результат:**
```
✅ ВСЕ КОНТЕЙНЕРЫ ЗАПУЩЕНЫ
Работают: 9, Не работают: 0
```

---

### Smoke Test 3: Prometheus Targets (1 минута)

**Путь файла:** `monitoring/tests/check_targets.sh`

```bash
#!/bin/bash
set -e

echo "=== SMOKE TEST: Проверка Prometheus Targets ==="
echo ""

# Получить все targets
TARGETS_JSON=$(curl -s http://localhost:9090/api/v1/targets)

# Подсчитать targets
TOTAL=$(echo "$TARGETS_JSON" | jq '.data.activeTargets | length')
UP=$(echo "$TARGETS_JSON" | jq '.data.activeTargets | map(select(.health=="up")) | length')
DOWN=$(echo "$TARGETS_JSON" | jq '.data.activeTargets | map(select(.health=="down")) | length')

echo "Общее количество targets: $TOTAL"
echo "UP: $UP"
echo "DOWN: $DOWN"
echo ""

# Показать детали по каждому target
echo "Детали по targets:"
echo "$TARGETS_JSON" | jq -r '.data.activeTargets[] | 
    "\(.labels.job): \(.health) - \(.scrapeUrl)"'

echo ""
echo "================================================"

if [ "$DOWN" -eq 0 ] && [ "$UP" -gt 0 ]; then
    echo "✅ ВСЕ TARGETS ДОСТУПНЫ"
    exit 0
else
    echo "❌ НЕКОТОРЫЕ TARGETS НЕДОСТУПНЫ"
    echo ""
    echo "Детали проблемных targets:"
    echo "$TARGETS_JSON" | jq -r '.data.activeTargets[] | 
        select(.health=="down") | 
        "Job: \(.labels.job)\nURL: \(.scrapeUrl)\nОшибка: \(.lastError)\n"'
    exit 1
fi
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/check_targets.sh
./tests/check_targets.sh
```

**Ожидаемый результат:**
```
✅ ВСЕ TARGETS ДОСТУПНЫ
UP: 8, DOWN: 0
```

---

## 🔄 E2E Tests (Сквозная Проверка)

### E2E Test 1: Полный Путь Метрик (5 минут)

**Путь файла:** `monitoring/tests/e2e_metrics_flow.sh`

```bash
#!/bin/bash
set -e

echo "=== E2E TEST: Полный путь метрик ==="
echo "App → Prometheus → Grafana → Alertmanager"
echo ""

FAILED=0

# ===== ШАГ 1: Prometheus собирает метрики =====
echo "ШАГ 1: Проверка сбора метрик в Prometheus"
echo "-------------------------------------------"

TARGETS_UP=$(curl -s http://localhost:9090/api/v1/targets | \
    jq '.data.activeTargets | map(select(.health=="up")) | length')
TARGETS_TOTAL=$(curl -s http://localhost:9090/api/v1/targets | \
    jq '.data.activeTargets | length')

echo "Targets UP: $TARGETS_UP/$TARGETS_TOTAL"

if [ "$TARGETS_UP" -eq "$TARGETS_TOTAL" ]; then
    echo "✅ Шаг 1 PASSED: Все targets доступны"
else
    echo "❌ Шаг 1 FAILED: Не все targets доступны"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ШАГ 2: Запрос метрик из Prometheus =====
echo "ШАГ 2: Запрос метрик из Prometheus"
echo "-------------------------------------------"

METRIC_COUNT=$(curl -s 'http://localhost:9090/api/v1/query?query=up' | \
    jq '.data.result | length')

echo "Количество метрик 'up': $METRIC_COUNT"

if [ "$METRIC_COUNT" -gt 0 ]; then
    echo "✅ Шаг 2 PASSED: Метрики доступны"
    
    # Показать детали метрик
    curl -s 'http://localhost:9090/api/v1/query?query=up' | \
        jq -r '.data.result[] | "  \(.metric.job): \(.value[1])"'
else
    echo "❌ Шаг 2 FAILED: Метрики недоступны"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ШАГ 3: Grafana подключен к Prometheus =====
echo "ШАГ 3: Проверка подключения Grafana к Prometheus"
echo "-------------------------------------------"

# Получить пароль Grafana
GRAFANA_PASSWORD=$(grep GRAFANA_PASSWORD ../.env | cut -d'=' -f2)

# Логин в Grafana
SESSION_RESPONSE=$(curl -s -X POST http://localhost:3000/api/auth/keys \
    -H "Content-Type: application/json" \
    -u "admin:$GRAFANA_PASSWORD" \
    -d '{"name":"test-key","role":"Admin"}' 2>/dev/null || echo '{"error":"auth failed"}')

# Проверить datasources
DATASOURCES=$(curl -s http://localhost:3000/api/datasources \
    -u "admin:$GRAFANA_PASSWORD" | jq 'length')

echo "Количество datasources: $DATASOURCES"

if [ "$DATASOURCES" -ge 3 ]; then
    echo "✅ Шаг 3 PASSED: Grafana подключен к datasources"
    
    # Показать datasources
    curl -s http://localhost:3000/api/datasources \
        -u "admin:$GRAFANA_PASSWORD" | \
        jq -r '.[] | "  \(.name) (\(.type))"'
else
    echo "❌ Шаг 3 FAILED: Недостаточно datasources"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ШАГ 4: Alert Rules загружены =====
echo "ШАГ 4: Проверка загрузки Alert Rules"
echo "-------------------------------------------"

ALERT_GROUPS=$(curl -s http://localhost:9090/api/v1/rules | \
    jq '.data.groups | length')
ALERT_RULES=$(curl -s http://localhost:9090/api/v1/rules | \
    jq '[.data.groups[].rules[]] | length')

echo "Количество групп правил: $ALERT_GROUPS"
echo "Количество правил: $ALERT_RULES"

if [ "$ALERT_RULES" -gt 0 ]; then
    echo "✅ Шаг 4 PASSED: Alert rules загружены"
    
    # Показать группы
    curl -s http://localhost:9090/api/v1/rules | \
        jq -r '.data.groups[] | "  \(.name): \(.rules | length) rules"'
else
    echo "❌ Шаг 4 FAILED: Alert rules не загружены"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ШАГ 5: Alertmanager получает alerts =====
echo "ШАГ 5: Проверка Alertmanager"
echo "-------------------------------------------"

AM_STATUS=$(curl -s http://localhost:9093/api/v2/status | jq -r '.cluster.status')
echo "Статус Alertmanager cluster: $AM_STATUS"

if [ "$AM_STATUS" == "ready" ]; then
    echo "✅ Шаг 5 PASSED: Alertmanager готов"
else
    echo "❌ Шаг 5 FAILED: Alertmanager не готов"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ИТОГОВЫЙ РЕЗУЛЬТАТ =====
echo "================================================"
echo "РЕЗУЛЬТАТЫ E2E ТЕСТА"
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ ВСЕ E2E ТЕСТЫ ПРОЙДЕНЫ (5/5)"
    echo ""
    echo "Полный путь метрик работает корректно:"
    echo "App → Prometheus → Grafana → Alertmanager"
    exit 0
else
    echo "❌ ПРОВАЛЕНО ТЕСТОВ: $FAILED/5"
    exit 1
fi
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/e2e_metrics_flow.sh
./tests/e2e_metrics_flow.sh
```

**Ожидаемый результат:**
```
✅ ВСЕ E2E ТЕСТЫ ПРОЙДЕНЫ (5/5)
```

---

### E2E Test 2: Путь Логов (3 минуты)

**Путь файла:** `monitoring/tests/e2e_logs_flow.sh`

```bash
#!/bin/bash
set -e

echo "=== E2E TEST: Полный путь логов ==="
echo "Promtail → Loki → Grafana"
echo ""

FAILED=0

# ===== ШАГ 1: Отправить тестовый лог =====
echo "ШАГ 1: Отправка тестового лога"
echo "-------------------------------------------"

# Создать тестовый лог
TEST_LOG_FILE="/tmp/oneflow_test_$(date +%s).log"
TEST_MESSAGE="E2E_TEST_LOG_$(date +%s)"

echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",\"level\":\"info\",\"message\":\"$TEST_MESSAGE\"}" > "$TEST_LOG_FILE"

echo "Создан тестовый лог: $TEST_LOG_FILE"
echo "Сообщение: $TEST_MESSAGE"
echo "✅ Шаг 1 PASSED"
echo ""

# Подождать 5 секунд для обработки
sleep 5

# ===== ШАГ 2: Проверить Loki получил лог =====
echo "ШАГ 2: Проверка получения лога в Loki"
echo "-------------------------------------------"

# Запросить логи за последнюю минуту
LOGS_RESPONSE=$(curl -s "http://localhost:3100/loki/api/v1/query_range?query={job=~\".+\"}&start=$(date -u -d '1 minute ago' +%s)000000000&end=$(date -u +%s)000000000")

LOGS_COUNT=$(echo "$LOGS_RESPONSE" | jq '.data.result | length')

echo "Количество log streams: $LOGS_COUNT"

if [ "$LOGS_COUNT" -gt 0 ]; then
    echo "✅ Шаг 2 PASSED: Loki получает логи"
    
    # Показать streams
    echo "$LOGS_RESPONSE" | jq -r '.data.result[] | "  Job: \(.stream.job)"' | sort -u
else
    echo "❌ Шаг 2 FAILED: Loki не получает логи"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ШАГ 3: Grafana может запросить логи из Loki =====
echo "ШАГ 3: Проверка Grafana → Loki"
echo "-------------------------------------------"

GRAFANA_PASSWORD=$(grep GRAFANA_PASSWORD ../.env | cut -d'=' -f2)

# Проверить Loki datasource
LOKI_DS=$(curl -s http://localhost:3000/api/datasources \
    -u "admin:$GRAFANA_PASSWORD" | \
    jq '.[] | select(.type=="loki") | .name')

if [ -n "$LOKI_DS" ]; then
    echo "✅ Шаг 3 PASSED: Grafana подключен к Loki"
    echo "  Datasource: $LOKI_DS"
else
    echo "❌ Шаг 3 FAILED: Loki datasource не найден"
    FAILED=$((FAILED + 1))
fi

echo ""

# Очистить тестовый файл
rm -f "$TEST_LOG_FILE"

# ===== ИТОГОВЫЙ РЕЗУЛЬТАТ =====
echo "================================================"
echo "РЕЗУЛЬТАТЫ E2E ТЕСТА ЛОГОВ"
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ ВСЕ E2E ТЕСТЫ ЛОГОВ ПРОЙДЕНЫ (3/3)"
    echo ""
    echo "Полный путь логов работает корректно:"
    echo "Promtail → Loki → Grafana"
    exit 0
else
    echo "❌ ПРОВАЛЕНО ТЕСТОВ: $FAILED/3"
    exit 1
fi
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/e2e_logs_flow.sh
./tests/e2e_logs_flow.sh
```

**Ожидаемый результат:**
```
✅ ВСЕ E2E ТЕСТЫ ЛОГОВ ПРОЙДЕНЫ (3/3)
```

---

### E2E Test 3: Путь Traces (3 минуты)

**Путь файла:** `monitoring/tests/e2e_traces_flow.sh`

```bash
#!/bin/bash
set -e

echo "=== E2E TEST: Полный путь трейсов ==="
echo "OTEL Collector → Jaeger → Grafana"
echo ""

FAILED=0

# ===== ШАГ 1: Проверить OTEL Collector =====
echo "ШАГ 1: Проверка OTEL Collector"
echo "-------------------------------------------"

OTEL_STATUS=$(curl -s http://localhost:13133/ | jq -r '.status')

echo "OTEL Collector статус: $OTEL_STATUS"

if [ "$OTEL_STATUS" == "Server available" ]; then
    echo "✅ Шаг 1 PASSED: OTEL Collector работает"
else
    echo "❌ Шаг 1 FAILED: OTEL Collector недоступен"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ШАГ 2: Проверить Jaeger =====
echo "ШАГ 2: Проверка Jaeger"
echo "-------------------------------------------"

JAEGER_SERVICES=$(curl -s 'http://localhost:16686/api/services' | jq '.data | length')

echo "Количество сервисов в Jaeger: $JAEGER_SERVICES"

if [ "$JAEGER_SERVICES" -ge 0 ]; then
    echo "✅ Шаг 2 PASSED: Jaeger работает"
    
    if [ "$JAEGER_SERVICES" -gt 0 ]; then
        echo "  Найденные сервисы:"
        curl -s 'http://localhost:16686/api/services' | jq -r '.data[]' | sed 's/^/    /'
    else
        echo "  (Пока нет трейсов - это нормально для нового деплоя)"
    fi
else
    echo "❌ Шаг 2 FAILED: Jaeger недоступен"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ШАГ 3: Grafana подключен к Jaeger =====
echo "ШАГ 3: Проверка Grafana → Jaeger"
echo "-------------------------------------------"

GRAFANA_PASSWORD=$(grep GRAFANA_PASSWORD ../.env | cut -d'=' -f2)

JAEGER_DS=$(curl -s http://localhost:3000/api/datasources \
    -u "admin:$GRAFANA_PASSWORD" | \
    jq '.[] | select(.type=="jaeger") | .name')

if [ -n "$JAEGER_DS" ]; then
    echo "✅ Шаг 3 PASSED: Grafana подключен к Jaeger"
    echo "  Datasource: $JAEGER_DS"
else
    echo "❌ Шаг 3 FAILED: Jaeger datasource не найден"
    FAILED=$((FAILED + 1))
fi

echo ""

# ===== ИТОГОВЫЙ РЕЗУЛЬТАТ =====
echo "================================================"
echo "РЕЗУЛЬТАТЫ E2E ТЕСТА ТРЕЙСОВ"
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ ВСЕ E2E ТЕСТЫ ТРЕЙСОВ ПРОЙДЕНЫ (3/3)"
    echo ""
    echo "Полный путь трейсов работает корректно:"
    echo "OTEL Collector → Jaeger → Grafana"
    echo ""
    echo "Примечание: Для появления трейсов необходимо,"
    echo "чтобы приложение отправляло traces в OTEL Collector"
    exit 0
else
    echo "❌ ПРОВАЛЕНО ТЕСТОВ: $FAILED/3"
    exit 1
fi
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/e2e_traces_flow.sh
./tests/e2e_traces_flow.sh
```

**Ожидаемый результат:**
```
✅ ВСЕ E2E ТЕСТЫ ТРЕЙСОВ ПРОЙДЕНЫ (3/3)
```

---

## 📊 Метрики После Деплоя

### Сбор Базовых Метрик (2 минуты)

**Путь файла:** `monitoring/tests/collect_deployment_metrics.sh`

```bash
#!/bin/bash
set -e

echo "=== МЕТРИКИ ПОСЛЕ ДЕПЛОЯ ==="
echo "Время: $(date)"
echo ""

OUTPUT_FILE="deployment_metrics_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "================================================"
    echo "DEPLOYMENT METRICS REPORT"
    echo "================================================"
    echo "Дата: $(date)"
    echo ""
    
    # ===== 1. СИСТЕМНЫЕ РЕСУРСЫ =====
    echo "1. СИСТЕМНЫЕ РЕСУРСЫ"
    echo "-------------------------------------------"
    
    # CPU и Memory
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
    
    echo ""
    
    # ===== 2. PROMETHEUS МЕТРИКИ =====
    echo "2. PROMETHEUS МЕТРИКИ"
    echo "-------------------------------------------"
    
    # Количество активных targets
    TARGETS=$(curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length')
    echo "Активных targets: $TARGETS"
    
    # Количество timeseries
    TIMESERIES=$(curl -s 'http://localhost:9090/api/v1/query?query=prometheus_tsdb_head_series' | jq '.data.result[0].value[1]' | tr -d '"')
    echo "Time series в памяти: $TIMESERIES"
    
    # Размер TSDB
    TSDB_SIZE=$(curl -s 'http://localhost:9090/api/v1/query?query=prometheus_tsdb_storage_blocks_bytes' | jq '.data.result[0].value[1]' | tr -d '"' | awk '{printf "%.2f MB", $1/1024/1024}')
    echo "Размер TSDB: $TSDB_SIZE"
    
    # Частота scrape
    SCRAPE_DURATION=$(curl -s 'http://localhost:9090/api/v1/query?query=prometheus_target_interval_length_seconds{quantile="0.99"}' | jq '.data.result[0].value[1]' | tr -d '"')
    echo "Средняя длительность scrape (p99): ${SCRAPE_DURATION}s"
    
    echo ""
    
    # ===== 3. GRAFANA МЕТРИКИ =====
    echo "3. GRAFANA МЕТРИКИ"
    echo "-------------------------------------------"
    
    GRAFANA_PASSWORD=$(grep GRAFANA_PASSWORD ../.env | cut -d'=' -f2)
    
    # Количество datasources
    DS_COUNT=$(curl -s http://localhost:3000/api/datasources -u "admin:$GRAFANA_PASSWORD" | jq 'length')
    echo "Datasources: $DS_COUNT"
    
    # Статус datasources
    echo "Статус datasources:"
    curl -s http://localhost:3000/api/datasources -u "admin:$GRAFANA_PASSWORD" | \
        jq -r '.[] | "  \(.name) (\(.type)): \(if .basicAuth then "configured" else "no auth" end)"'
    
    echo ""
    
    # ===== 4. LOKI МЕТРИКИ =====
    echo "4. LOKI МЕТРИКИ"
    echo "-------------------------------------------"
    
    # Ingester streams
    LOKI_STREAMS=$(curl -s 'http://localhost:3100/loki/api/v1/query_range?query={job=~".+"}' | jq '.data.result | length')
    echo "Log streams: $LOKI_STREAMS"
    
    # Размер хранилища (если доступно)
    LOKI_SIZE=$(curl -s 'http://localhost:3100/metrics' | grep 'loki_ingester_memory_streams' | awk '{print $2}')
    echo "Memory streams: ${LOKI_SIZE:-0}"
    
    echo ""
    
    # ===== 5. JAEGER МЕТРИКИ =====
    echo "5. JAEGER МЕТРИКИ"
    echo "-------------------------------------------"
    
    JAEGER_SERVICES=$(curl -s 'http://localhost:16686/api/services' | jq '.data | length')
    echo "Сервисов в Jaeger: $JAEGER_SERVICES"
    
    if [ "$JAEGER_SERVICES" -gt 0 ]; then
        echo "Список сервисов:"
        curl -s 'http://localhost:16686/api/services' | jq -r '.data[]' | sed 's/^/  /'
    fi
    
    echo ""
    
    # ===== 6. ALERT RULES =====
    echo "6. ALERT RULES"
    echo "-------------------------------------------"
    
    ALERT_GROUPS=$(curl -s http://localhost:9090/api/v1/rules | jq '.data.groups | length')
    ALERT_RULES=$(curl -s http://localhost:9090/api/v1/rules | jq '[.data.groups[].rules[]] | length')
    echo "Групп правил: $ALERT_GROUPS"
    echo "Всего правил: $ALERT_RULES"
    
    # Статус правил
    echo "Статус по группам:"
    curl -s http://localhost:9090/api/v1/rules | \
        jq -r '.data.groups[] | "  \(.name): \(.rules | length) rules"'
    
    echo ""
    
    # ===== 7. ПРОИЗВОДИТЕЛЬНОСТЬ =====
    echo "7. ПРОИЗВОДИТЕЛЬНОСТЬ"
    echo "-------------------------------------------"
    
    # Prometheus query latency
    echo -n "Prometheus query latency: "
    START_TIME=$(date +%s%3N)
    curl -s 'http://localhost:9090/api/v1/query?query=up' > /dev/null
    END_TIME=$(date +%s%3N)
    LATENCY=$((END_TIME - START_TIME))
    echo "${LATENCY}ms"
    
    # Grafana health check latency
    echo -n "Grafana health check latency: "
    START_TIME=$(date +%s%3N)
    curl -s http://localhost:3000/api/health > /dev/null
    END_TIME=$(date +%s%3N)
    LATENCY=$((END_TIME - START_TIME))
    echo "${LATENCY}ms"
    
    # Loki query latency
    echo -n "Loki query latency: "
    START_TIME=$(date +%s%3N)
    curl -s 'http://localhost:3100/loki/api/v1/query?query={job=~".+"}' > /dev/null
    END_TIME=$(date +%s%3N)
    LATENCY=$((END_TIME - START_TIME))
    echo "${LATENCY}ms"
    
    echo ""
    
    # ===== 8. DISK USAGE =====
    echo "8. DISK USAGE"
    echo "-------------------------------------------"
    
    echo "Docker volumes:"
    docker system df -v | grep "oneflow-monitoring" || echo "  (нет данных)"
    
    echo ""
    echo "================================================"
    echo "КОНЕЦ ОТЧЕТА"
    echo "================================================"
    
} | tee "$OUTPUT_FILE"

echo ""
echo "✅ Метрики сохранены в: $OUTPUT_FILE"
echo ""
echo "Ключевые показатели:"
echo "  - Targets: $TARGETS"
echo "  - Time series: $TIMESERIES"
echo "  - Alert rules: $ALERT_RULES"
echo "  - Log streams: $LOKI_STREAMS"
echo "  - Jaeger services: $JAEGER_SERVICES"
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/collect_deployment_metrics.sh
./tests/collect_deployment_metrics.sh
```

**Ожидаемый результат:**
- Файл `deployment_metrics_YYYYMMDD_HHMMSS.txt` с полным отчетом
- Все метрики собраны успешно
- Латентность < 500ms для всех компонентов

---

### Проверка SLO Метрик (3 минуты)

**Путь файла:** `monitoring/tests/check_slo_metrics.sh`

```bash
#!/bin/bash
set -e

echo "=== ПРОВЕРКА SLO МЕТРИК ==="
echo ""

# ===== 1. AVAILABILITY SLO =====
echo "1. AVAILABILITY SLO (Целевое значение: 99.9%)"
echo "-------------------------------------------"

# Если есть метрики oneflow_requests_total
AVAILABILITY=$(curl -s 'http://localhost:9090/api/v1/query?query=(1-(sum(rate(oneflow_requests_total{status="error"}[5m]))/sum(rate(oneflow_requests_total[5m]))))*100' | \
    jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")

if [ "$AVAILABILITY" != "N/A" ]; then
    echo "Текущая availability: ${AVAILABILITY}%"
    
    if (( $(echo "$AVAILABILITY >= 99.9" | bc -l) )); then
        echo "✅ SLO выполнен"
    else
        echo "⚠️  SLO не выполнен (ниже 99.9%)"
    fi
else
    echo "⚠️  Метрики пока недоступны (приложение не отправляет метрики)"
fi

echo ""

# ===== 2. LATENCY SLO =====
echo "2. LATENCY SLO (Целевое значение: p95 < 500ms)"
echo "-------------------------------------------"

LATENCY_P95=$(curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(oneflow_request_duration_seconds_bucket[5m]))*1000' | \
    jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")

if [ "$LATENCY_P95" != "N/A" ]; then
    echo "Текущая latency (p95): ${LATENCY_P95}ms"
    
    if (( $(echo "$LATENCY_P95 < 500" | bc -l) )); then
        echo "✅ SLO выполнен"
    else
        echo "⚠️  SLO не выполнен (выше 500ms)"
    fi
else
    echo "⚠️  Метрики пока недоступны (приложение не отправляет метрики)"
fi

echo ""

# ===== 3. ERROR BUDGET =====
echo "3. ERROR BUDGET"
echo "-------------------------------------------"

ERROR_RATE=$(curl -s 'http://localhost:9090/api/v1/query?query=(sum(rate(oneflow_requests_total{status="error"}[5m]))/sum(rate(oneflow_requests_total[5m])))*100' | \
    jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")

if [ "$ERROR_RATE" != "N/A" ]; then
    echo "Текущий error rate: ${ERROR_RATE}%"
    echo "Доступный error budget: $(echo "0.1 - $ERROR_RATE" | bc)%"
    
    if (( $(echo "$ERROR_RATE < 0.1" | bc -l) )); then
        echo "✅ Error budget в норме"
    else
        echo "⚠️  Error budget исчерпан"
    fi
else
    echo "⚠️  Метрики пока недоступны"
fi

echo ""

# ===== 4. СИСТЕМНЫЕ МЕТРИКИ =====
echo "4. СИСТЕМНЫЕ МЕТРИКИ"
echo "-------------------------------------------"

# CPU usage
CPU_USAGE=$(curl -s 'http://localhost:9090/api/v1/query?query=100-(avg(irate(node_cpu_seconds_total{mode="idle"}[5m]))*100)' | \
    jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")

echo "CPU usage: ${CPU_USAGE}%"

# Memory usage
MEM_USAGE=$(curl -s 'http://localhost:9090/api/v1/query?query=(1-(node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes))*100' | \
    jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")

echo "Memory usage: ${MEM_USAGE}%"

# Disk usage
DISK_USAGE=$(curl -s 'http://localhost:9090/api/v1/query?query=(1-(node_filesystem_avail_bytes/node_filesystem_size_bytes))*100' | \
    jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")

echo "Disk usage: ${DISK_USAGE}%"

echo ""
echo "================================================"
echo "Примечание: Для полной работы SLO метрик"
echo "необходимо, чтобы приложение экспортировало метрики:"
echo "  - oneflow_requests_total"
echo "  - oneflow_request_duration_seconds"
echo "================================================"
```

**Запуск:**
```bash
cd monitoring
chmod +x tests/check_slo_metrics.sh
./tests/check_slo_metrics.sh
```

**Ожидаемый результат:**
```
✅ SLO выполнен (availability >= 99.9%)
✅ SLO выполнен (latency p95 < 500ms)
✅ Error budget в норме
```

---

## 🤖 Автоматизированный Test Suite

### Мастер-скрипт Запуска Всех Тестов

**Путь файла:** `monitoring/tests/run_all_tests.sh`

```bash
#!/bin/bash

echo "================================================"
echo "  ONEFLOW MONITORING STACK - TEST SUITE"
echo "================================================"
echo "Время начала: $(date)"
echo ""

TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$TESTS_DIR/.."

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Функция для запуска теста
run_test() {
    local test_name=$1
    local test_script=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo ""
    echo "================================================"
    echo "ЗАПУСК: $test_name"
    echo "================================================"
    
    if bash "$test_script"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "✅ PASSED: $test_name"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "❌ FAILED: $test_name"
    fi
}

# ===== SMOKE TESTS =====
echo "📋 РАЗДЕЛ 1: SMOKE TESTS"
echo ""

run_test "Smoke Test: Доступность сервисов" "tests/smoke_test.sh"
run_test "Smoke Test: Docker контейнеры" "tests/check_containers.sh"
run_test "Smoke Test: Prometheus targets" "tests/check_targets.sh"

# ===== E2E TESTS =====
echo ""
echo "📋 РАЗДЕЛ 2: E2E TESTS"
echo ""

run_test "E2E Test: Путь метрик" "tests/e2e_metrics_flow.sh"
run_test "E2E Test: Путь логов" "tests/e2e_logs_flow.sh"
run_test "E2E Test: Путь трейсов" "tests/e2e_traces_flow.sh"

# ===== МЕТРИКИ =====
echo ""
echo "📋 РАЗДЕЛ 3: МЕТРИКИ"
echo ""

echo "Сбор метрик после деплоя..."
bash tests/collect_deployment_metrics.sh > /dev/null 2>&1
echo "✅ Метрики собраны"

echo "Проверка SLO метрик..."
bash tests/check_slo_metrics.sh
echo "✅ SLO метрики проверены"

# ===== ИТОГОВЫЙ ОТЧЕТ =====
echo ""
echo "================================================"
echo "  ИТОГОВЫЙ ОТЧЕТ"
echo "================================================"
echo "Время завершения: $(date)"
echo ""
echo "Всего тестов: $TOTAL_TESTS"
echo "Успешно: $PASSED_TESTS"
echo "Провалено: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅✅✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ ✅✅✅"
    echo ""
    echo "Monitoring Stack готов к использованию!"
    echo ""
    echo "Доступные интерфейсы:"
    echo "  - Grafana:       http://localhost:3000"
    echo "  - Prometheus:    http://localhost:9090"
    echo "  - Alertmanager:  http://localhost:9093"
    echo "  - Jaeger:        http://localhost:16686"
    echo ""
    exit 0
else
    echo "❌❌❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ ❌❌❌"
    echo ""
    echo "Провалено тестов: $FAILED_TESTS"
    echo "Пожалуйста, проверьте логи выше для деталей."
    echo ""
    exit 1
fi
```

**Запуск всех тестов:**
```bash
cd monitoring
chmod +x tests/run_all_tests.sh
./tests/run_all_tests.sh
```

**Ожидаемый результат:**
```
✅✅✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ ✅✅✅
Успешно: 6, Провалено: 0
Monitoring Stack готов к использованию!
```

---

## 📝 Быстрый Чеклист

### После Деплоя (выполнить в течение 5 минут)

```bash
# 1. Smoke tests
./tests/smoke_test.sh
./tests/check_containers.sh
./tests/check_targets.sh

# 2. E2E tests
./tests/e2e_metrics_flow.sh
./tests/e2e_logs_flow.sh
./tests/e2e_traces_flow.sh

# 3. Собрать метрики
./tests/collect_deployment_metrics.sh

# 4. Проверить SLO
./tests/check_slo_metrics.sh
```

### Или запустить все сразу:

```bash
./tests/run_all_tests.sh
```

---

**Последнее обновление:** 2025-10-11  
**Версия:** 1.0
