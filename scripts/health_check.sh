#!/bin/bash

###############################################################################
# OneFlow.AI Health Check Script
# Проверяет состояние всех компонентов системы
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-oneflow}"
POSTGRES_DB="${POSTGRES_DB:-oneflow}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

TIMEOUT=10
FAILURES=0

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_failure() {
    echo -e "${RED}✗${NC} $1"
    FAILURES=$((FAILURES + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_failure "Command '$1' not found. Please install it."
        return 1
    fi
    return 0
}

###############################################################################
# Health Checks
###############################################################################

check_api_health() {
    print_header "API Health Check"
    
    if ! check_command curl; then
        return 1
    fi
    
    # Health endpoint
    echo -n "Checking /health endpoint... "
    if curl -sf --max-time $TIMEOUT "${API_URL}/health" > /dev/null 2>&1; then
        print_success "Health endpoint responding"
    else
        print_failure "Health endpoint not responding"
        return 1
    fi
    
    # Readiness endpoint
    echo -n "Checking /ready endpoint... "
    if curl -sf --max-time $TIMEOUT "${API_URL}/ready" > /dev/null 2>&1; then
        print_success "Readiness endpoint responding"
    else
        print_failure "Readiness endpoint not responding"
        return 1
    fi
    
    # Metrics endpoint
    echo -n "Checking /metrics endpoint... "
    if curl -sf --max-time $TIMEOUT "${API_URL}/metrics" > /dev/null 2>&1; then
        print_success "Metrics endpoint responding"
    else
        print_warning "Metrics endpoint not responding (may be disabled)"
    fi
    
    # API docs
    echo -n "Checking /docs endpoint... "
    if curl -sf --max-time $TIMEOUT "${API_URL}/docs" > /dev/null 2>&1; then
        print_success "API documentation available"
    else
        print_warning "API documentation not available"
    fi
    
    return 0
}

check_api_latency() {
    print_header "API Latency Check"
    
    echo -n "Measuring /health response time... "
    LATENCY=$(curl -o /dev/null -s -w '%{time_total}' --max-time $TIMEOUT "${API_URL}/health")
    
    # Convert to milliseconds
    LATENCY_MS=$(echo "$LATENCY * 1000" | bc)
    
    if (( $(echo "$LATENCY_MS < 100" | bc -l) )); then
        print_success "Excellent latency: ${LATENCY_MS}ms"
    elif (( $(echo "$LATENCY_MS < 500" | bc -l) )); then
        print_success "Good latency: ${LATENCY_MS}ms"
    elif (( $(echo "$LATENCY_MS < 1000" | bc -l) )); then
        print_warning "Acceptable latency: ${LATENCY_MS}ms"
    else
        print_failure "High latency: ${LATENCY_MS}ms"
    fi
}

check_postgres() {
    print_header "PostgreSQL Check"
    
    if ! check_command pg_isready; then
        print_warning "pg_isready not found, skipping PostgreSQL check"
        return 0
    fi
    
    echo -n "Checking PostgreSQL connection... "
    if pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; then
        print_success "PostgreSQL is accepting connections"
    else
        print_failure "PostgreSQL is not responding"
        return 1
    fi
    
    # Check connection count (requires psql and password)
    if check_command psql && [ -n "${PGPASSWORD:-}" ]; then
        echo -n "Checking active connections... "
        CONN_COUNT=$(PGPASSWORD="$PGPASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | xargs || echo "0")
        
        if [ "$CONN_COUNT" -gt 0 ]; then
            print_success "Active connections: $CONN_COUNT"
        else
            print_warning "Unable to check connection count"
        fi
    fi
    
    return 0
}

check_redis() {
    print_header "Redis Check"
    
    if ! check_command redis-cli; then
        print_warning "redis-cli not found, skipping Redis check"
        return 0
    fi
    
    echo -n "Checking Redis connection... "
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
        print_success "Redis is responding"
    else
        print_failure "Redis is not responding"
        return 1
    fi
    
    echo -n "Checking Redis memory... "
    REDIS_MEMORY=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2 | tr -d '\r' || echo "unknown")
    
    if [ "$REDIS_MEMORY" != "unknown" ]; then
        print_success "Memory usage: $REDIS_MEMORY"
    else
        print_warning "Unable to check memory usage"
    fi
    
    return 0
}

check_disk_space() {
    print_header "Disk Space Check"
    
    echo -n "Checking disk usage... "
    DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -lt 70 ]; then
        print_success "Disk usage: ${DISK_USAGE}%"
    elif [ "$DISK_USAGE" -lt 85 ]; then
        print_warning "Disk usage: ${DISK_USAGE}%"
    else
        print_failure "Critical disk usage: ${DISK_USAGE}%"
    fi
}

check_memory() {
    print_header "Memory Check"
    
    if command -v free &> /dev/null; then
        echo -n "Checking memory usage... "
        MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
        
        if [ "$MEMORY_USAGE" -lt 70 ]; then
            print_success "Memory usage: ${MEMORY_USAGE}%"
        elif [ "$MEMORY_USAGE" -lt 85 ]; then
            print_warning "Memory usage: ${MEMORY_USAGE}%"
        else
            print_failure "Critical memory usage: ${MEMORY_USAGE}%"
        fi
    else
        print_warning "Cannot check memory (free command not found)"
    fi
}

check_security() {
    print_header "Security Headers Check"
    
    if ! check_command curl; then
        return 1
    fi
    
    echo -n "Checking security headers... "
    HEADERS=$(curl -sI --max-time $TIMEOUT "${API_URL}/health" 2>/dev/null || echo "")
    
    # Check for important security headers
    declare -a REQUIRED_HEADERS=(
        "X-Content-Type-Options"
        "X-Frame-Options"
        "Strict-Transport-Security"
    )
    
    MISSING_HEADERS=()
    for header in "${REQUIRED_HEADERS[@]}"; do
        if ! echo "$HEADERS" | grep -qi "$header"; then
            MISSING_HEADERS+=("$header")
        fi
    done
    
    if [ ${#MISSING_HEADERS[@]} -eq 0 ]; then
        print_success "All security headers present"
    else
        print_warning "Missing headers: ${MISSING_HEADERS[*]}"
    fi
}

check_ssl_certificate() {
    print_header "SSL Certificate Check"
    
    # Skip if not HTTPS
    if [[ ! "$API_URL" =~ ^https:// ]]; then
        print_warning "Not using HTTPS, skipping SSL check"
        return 0
    fi
    
    if ! check_command openssl; then
        print_warning "openssl not found, skipping SSL check"
        return 0
    fi
    
    DOMAIN=$(echo "$API_URL" | sed -e 's|^https://||' -e 's|/.*||' -e 's|:.*||')
    
    echo -n "Checking SSL certificate for $DOMAIN... "
    EXPIRY=$(echo | openssl s_client -servername "$DOMAIN" -connect "${DOMAIN}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    
    if [ -n "$EXPIRY" ]; then
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$EXPIRY" +%s 2>/dev/null)
        NOW_EPOCH=$(date +%s)
        DAYS_UNTIL_EXPIRY=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
        
        if [ "$DAYS_UNTIL_EXPIRY" -gt 30 ]; then
            print_success "Certificate valid for $DAYS_UNTIL_EXPIRY days"
        elif [ "$DAYS_UNTIL_EXPIRY" -gt 7 ]; then
            print_warning "Certificate expires in $DAYS_UNTIL_EXPIRY days"
        else
            print_failure "Certificate expires in $DAYS_UNTIL_EXPIRY days!"
        fi
    else
        print_warning "Unable to check certificate"
    fi
}

###############################################################################
# Main Execution
###############################################################################

main() {
    echo "╔════════════════════════════════════════╗"
    echo "║   OneFlow.AI Health Check Script      ║"
    echo "║   $(date +'%Y-%m-%d %H:%M:%S')                   ║"
    echo "╚════════════════════════════════════════╝"
    
    # Run all checks
    check_api_health
    check_api_latency
    check_postgres
    check_redis
    check_disk_space
    check_memory
    check_security
    check_ssl_certificate
    
    # Summary
    print_header "Summary"
    
    if [ $FAILURES -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ $FAILURES check(s) failed${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
