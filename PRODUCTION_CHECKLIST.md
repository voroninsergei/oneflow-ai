# ✅ Production Readiness Checklist

Используйте этот чеклист перед развёртыванием OneFlow.AI в production.

---

## 🔐 Безопасность

### API Security
- [ ] CORS настроен с конкретными доменами (не `*`)
- [ ] Security headers добавлены (X-Frame-Options, CSP, HSTS)
- [ ] Request size limits установлены (по умолчанию 10MB)
- [ ] Rate limiting включен (60/min, 1000/hour)
- [ ] JWT secret изменён с дефолтного значения
- [ ] Все секреты вынесены из кода в переменные окружения
- [ ] API ключи провайдеров хранятся в Secret Manager
- [ ] Санитизация секретов в логах работает

### Authentication
- [ ] Password минимальная длина 12 символов
- [ ] Bcrypt hashing для паролей
- [ ] JWT токены с коротким временем жизни (30 мин)
- [ ] Refresh токены реализованы
- [ ] API ключи имеют ротацию
- [ ] Grace period для старых ключей настроен (7 дней)

### Network
- [ ] HTTPS включен (TLS 1.2+)
- [ ] Network policies настроены в K8s
- [ ] Firewall rules ограничивают доступ
- [ ] VPN/Private network для внутренних сервисов
- [ ] DDoS защита на уровне CDN/Load Balancer

---

## 📊 Observability

### Metrics
- [ ] Prometheus `/metrics` endpoint работает
- [ ] Grafana dashboards настроены
- [ ] Alerting rules созданы
- [ ] SLO/SLI определены
- [ ] Custom business metrics добавлены

### Logging
- [ ] Structured logging (JSON) включен
- [ ] Log level установлен в INFO для production
- [ ] Sensitive data не попадает в логи
- [ ] Centralized logging настроен (ELK/Loki/CloudWatch)
- [ ] Log rotation настроен
- [ ] Retention policy определён

### Tracing
- [ ] OpenTelemetry middleware включен (опционально)
- [ ] Jaeger/Tempo настроен для distributed tracing
- [ ] Sampling rate установлен разумно (10-20%)
- [ ] Trace context передаётся между сервисами

---

## 🏗️ Infrastructure

### Container
- [ ] Multi-stage Dockerfile для оптимизации размера
- [ ] Non-root user в контейнере
- [ ] HEALTHCHECK добавлен в Dockerfile
- [ ] Image регулярно обновляется (security patches)
- [ ] Vulnerability scanning включен (Trivy/Snyk)
- [ ] Base image minimal (alpine/distroless)

### Kubernetes
- [ ] Resources requests/limits установлены
- [ ] Liveness probe настроен
- [ ] Readiness probe настроен
- [ ] Startup probe настроен (для медленного старта)
- [ ] HPA (HorizontalPodAutoscaler) настроен
- [ ] PDB (PodDisruptionBudget) создан
- [ ] Multiple replicas для HA (минимум 3)
- [ ] Topology spread constraints настроены
- [ ] Node affinity/anti-affinity правила
- [ ] ConfigMap и Secret используются вместо hardcode

### Database
- [ ] PostgreSQL в HA режиме (или managed service)
- [ ] Connection pooling настроен
- [ ] Backup автоматизирован
- [ ] Backup тестируется регулярно
- [ ] Retention policy для backups
- [ ] Database migrations автоматизированы
- [ ] Read replicas для масштабирования чтения

### Redis
- [ ] Redis Sentinel/Cluster для HA
- [ ] Persistence включена (AOF)
- [ ] Memory limit установлен
- [ ] Eviction policy настроена
- [ ] Password защита включена

---

## 🔄 Reliability

### Circuit Breaker
- [ ] Circuit breaker реализован для всех провайдеров
- [ ] Failure threshold настроен (5 ошибок)
- [ ] Recovery timeout настроен (60 секунд)
- [ ] Half-open state тестируется

### Retry Logic
- [ ] Exponential backoff реализован
- [ ] Max retries установлен (3)
- [ ] Jitter добавлен для избежания thundering herd
- [ ] Idempotency keys используются
- [ ] Timeout для каждого retry

### Timeouts
- [ ] HTTP connection timeout: 10s
- [ ] HTTP read timeout: 30s
- [ ] Database query timeout: 30s
- [ ] Redis operation timeout: 5s

### Quotas & Rate Limiting
- [ ] Per-user quotas реализованы
- [ ] Per-provider quotas настроены
- [ ] Graceful degradation при превышении квот
- [ ] Quota tracking в Redis
- [ ] Rate limit headers в ответах API

---

## 💰 Pricing & Routing

### Token-based Billing
- [ ] Input/output токены отслеживаются раздельно
- [ ] Pricing catalog актуален
- [ ] Credits normalization работает
- [ ] Property tests для расчётов проходят
- [ ] Округление корректное (2 decimal places)

### Smart Routing
- [ ] Routing strategies реализованы (cost/latency/quality)
- [ ] Fallback chain настроен (минимум 2 fallback)
- [ ] Provider health tracking работает
- [ ] Load balancing между провайдерами
- [ ] A/B testing capability

---

## 🧪 Testing

### Unit Tests
- [ ] Coverage > 80%
- [ ] All critical paths covered
- [ ] Edge cases тестируются
- [ ] Mock external APIs

### Integration Tests
- [ ] API endpoints тестируются
- [ ] Database interactions тестируются
- [ ] Redis operations тестируются
- [ ] Authentication flow тестируется

### Property Tests
- [ ] Pricing calculations property tests
- [ ] Routing logic property tests
- [ ] Hypothesis tests проходят

### Load Testing
- [ ] Load testing выполнен (k6/Locust)
- [ ] Sustained load 1000 req/s
- [ ] Spike testing выполнен
- [ ] Latency p95 < 500ms, p99 < 1s
- [ ] Error rate < 0.1%

### Chaos Testing
- [ ] Pod failures тестируются
- [ ] Network partitions симулируются
- [ ] Database failures тестируются
- [ ] Provider API failures тестируются

---

## 📝 Documentation

- [ ] API documentation актуальна (Swagger/ReDoc)
- [ ] README.md обновлён
- [ ] DEPLOYMENT.md создан
- [ ] Architecture diagrams созданы
- [ ] Runbooks для incident response
- [ ] Postmortem template
- [ ] Changelog ведётся

---

## 🚀 Deployment

### CI/CD
- [ ] Automated tests в CI pipeline
- [ ] Docker image build автоматизирован
- [ ] Security scanning в CI
- [ ] Automated deployment to staging
- [ ] Manual approval для production
- [ ] Rollback plan документирован

### Blue-Green/Canary
- [ ] Canary deployment strategy настроена
- [ ] Traffic splitting возможен
- [ ] Automated rollback при ошибках
- [ ] Monitoring during deployment

### Disaster Recovery
- [ ] Backup strategy документирован
- [ ] Restore procedure тестирован
- [ ] RTO определён (Recovery Time Objective)
- [ ] RPO определён (Recovery Point Objective)
- [ ] DR runbook создан

---

## 📈 Performance

- [ ] Database indexes оптимизированы
- [ ] N+1 queries избегаются
- [ ] Caching strategy реализован
- [ ] CDN для статических ресурсов
- [ ] Compression включен (gzip/brotli)
- [ ] Connection pooling оптимизирован
- [ ] Lazy loading где возможно

---

## 🔔 Alerting

### Critical Alerts
- [ ] Service down alert
- [ ] High error rate (>1%)
- [ ] High latency (p99 > 2s)
- [ ] Database connection failures
- [ ] Redis connection failures
- [ ] Disk space low (<10%)
- [ ] Memory usage high (>90%)

### Warning Alerts
- [ ] Error rate elevated (>0.5%)
- [ ] Latency degraded (p95 > 1s)
- [ ] Circuit breaker opened
- [ ] Rate limit approaching
- [ ] Certificate expiring (<30 days)

### On-Call
- [ ] On-call rotation настроен
- [ ] PagerDuty/Opsgenie интеграция
- [ ] Escalation policy определена
- [ ] Runbooks доступны on-call

---

## 🎯 Business Metrics

- [ ] Request count tracking
- [ ] Revenue tracking (credits consumed)
- [ ] User activity tracking
- [ ] Provider usage distribution
- [ ] Cost per request analytics
- [ ] Conversion funnel tracking

---

## ✅ Final Checks

### Pre-deployment
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance benchmarks met
- [ ] Documentation reviewed
- [ ] Stakeholders informed

### Post-deployment
- [ ] Health checks green
- [ ] Metrics flowing correctly
- [ ] Logs visible in aggregator
- [ ] Alerts configured and firing tests
- [ ] Smoke tests passed
- [ ] Rollback procedure verified

### Week 1
- [ ] Monitor error rates daily
- [ ] Check latency trends
- [ ] Review user feedback
- [ ] Optimize based on real traffic
- [ ] Update documentation based on learnings

---

## 📊 Success Metrics

### SLIs (Service Level Indicators)
- **Availability**: 99.9% uptime
- **Latency**: p95 < 500ms, p99 < 1s
- **Error Rate**: < 0.1%
- **Throughput**: 1000 req/s sustained

### SLOs (Service Level Objectives)
- **Monthly uptime**: 99.9% (43 minutes downtime/month)
- **API response time**: 95% under 500ms
- **Successful requests**: 99.9%

---

## 🎓 Training & Knowledge Transfer

- [ ] Team trained on new features
- [ ] Incident response practiced
- [ ] Monitoring dashboards reviewed
- [ ] Common issues documented
- [ ] Escalation paths clear

---

**Sign-off:**

- [ ] Tech Lead approved
- [ ] Security team approved
- [ ] DevOps team approved
- [ ] Product owner approved

**Deployment Date:** ___________

**Deployed By:** ___________

**Rollback Owner:** ___________
