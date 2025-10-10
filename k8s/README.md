# OneFlow AI Kubernetes Deployment

## Структура файлов

```
k8s/
├── namespace.yaml              # Namespace для изоляции
├── configmap.yaml             # Конфигурация приложения
├── secret.yaml                # Секреты (API keys, passwords)
├── deployment.yaml            # Основной Deployment с probes и security
├── service.yaml               # Service для внутреннего доступа
├── ingress.yaml               # Ingress для внешнего доступа
├── hpa.yaml                   # HorizontalPodAutoscaler
├── additional-resources.yaml  # ServiceAccount, PDB, NetworkPolicy, Quotas
├── kustomization.yaml         # Kustomize для управления
└── README.md                  # Эта инструкция
```

## Быстрый старт

### 1. Подготовка

**Обязательно заполните секреты:**

```bash
# Создайте файл с секретами (НЕ коммитить в git!)
cat > k8s/secret.yaml << EOF
# ... скопируйте из шаблона и заполните реальными значениями
EOF
```

**Замените в файлах:**
- `yourdomain.com` → ваш домен
- `your-registry.io/oneflow-ai:2.0.0` → ваш Docker registry

### 2. Применение манифестов

**Вариант A: Напрямую через kubectl**

```bash
# Применить все манифесты
kubectl apply -f k8s/

# Или в определённом порядке
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/additional-resources.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

**Вариант B: Через Kustomize (рекомендуется)**

```bash
# Просмотр результата
kubectl kustomize k8s/

# Применение
kubectl apply -k k8s/
```

**Вариант C: Через Helm (если создадите chart)**

```bash
helm install oneflow-ai ./helm-chart/ \
  --namespace oneflow-ai \
  --create-namespace \
  --values values.production.yaml
```

### 3. Проверка развёртывания

```bash
# Статус подов
kubectl get pods -n oneflow-ai -w

# Логи
kubectl logs -n oneflow-ai -l app=oneflow-ai -f

# Описание пода (для отладки)
kubectl describe pod -n oneflow-ai <pod-name>

# Проверка endpoints
kubectl get endpoints -n oneflow-ai

# Проверка HPA
kubectl get hpa -n oneflow-ai

# События namespace
kubectl get events -n oneflow-ai --sort-by='.lastTimestamp'
```

### 4. Доступ к приложению

```bash
# Port-forward для локального доступа
kubectl port-forward -n oneflow-ai svc/oneflow-ai 8000:8000

# Или через Ingress (после настройки DNS)
curl https://api.yourdomain.com/health
```

## Основные компоненты

### ✅ Deployment
- **Replicas**: 3 (минимум для HA)
- **Strategy**: RollingUpdate с maxUnavailable: 0
- **Probes**:
  - `startupProbe`: 60 секунд на старт
  - `livenessProbe`: проверка каждые 10 сек
  - `readinessProbe`: проверка каждые 5 сек
- **Security**:
  - runAsNonRoot: true
  - readOnlyRootFilesystem: true
  - seccompProfile: RuntimeDefault
- **Resources**:
  - requests: 256Mi RAM / 200m CPU
  - limits: 512Mi RAM / 1000m CPU

### ✅ Service
- **Type**: ClusterIP
- **Session Affinity**: ClientIP (для WebSocket)
- **Port**: 8000

### ✅ Ingress
- **TLS**: автоматический через cert-manager
- **Rate Limiting**: 100 req/min, 10 req/sec
- **Security Headers**: X-Frame-Options, CSP, etc.
- **WebSocket**: поддержка включена
- **CORS**: настроен для указанных origins

### ✅ HPA
- **Min**: 3 replicas
- **Max**: 10 replicas
- **Triggers**: CPU 70%, Memory 80%
- **Scale Up**: быстро (0 sec stabilization)
- **Scale Down**: медленно (300 sec stabilization)

### ✅ Additional Resources
- **ServiceAccount**: для RBAC
- **PodDisruptionBudget**: минимум 2 пода доступны
- **NetworkPolicy**: ограничение сетевого доступа
- **ResourceQuota**: лимиты на namespace
- **LimitRange**: дефолтные лимиты для подов

## Обновление приложения

### Rolling Update (zero-downtime)

```bash
# Обновить образ
kubectl set image deployment/oneflow-ai \
  oneflow-ai=your-registry.io/oneflow-ai:2.1.0 \
  -n oneflow-ai

# Следить за процессом
kubectl rollout status deployment/oneflow-ai -n oneflow-ai

# Откатить в случае проблем
kubectl rollout undo deployment/oneflow-ai -n oneflow-ai

# История деплоев
kubectl rollout history deployment/oneflow-ai -n oneflow-ai
```

### Обновление конфигурации

```bash
# Изменить ConfigMap
kubectl edit configmap oneflow-config -n oneflow-ai

# Перезапустить поды для применения изменений
kubectl rollout restart deployment/oneflow-ai -n oneflow-ai
```

## Масштабирование

### Ручное масштабирование

```bash
# Увеличить до 5 реплик
kubectl scale deployment/oneflow-ai --replicas=5 -n oneflow-ai

# Или изменить в файле и применить
kubectl apply -f k8s/deployment.yaml
```

### Автоматическое (HPA)

HPA автоматически масштабирует от 3 до 10 реплик на основе CPU и Memory.

## Мониторинг

### Prometheus Metrics

```bash
# Проверить метрики
kubectl port-forward -n oneflow-ai svc/oneflow-ai 8000:8000
curl http://localhost:8000/metrics
```

### Логи

```bash
# Все поды
kubectl logs -n oneflow-ai -l app=oneflow-ai --tail=100 -f

# Конкретный под
kubectl logs -n oneflow-ai <pod-name> -f

# Предыдущий контейнер (после краша)
kubectl logs -n oneflow-ai <pod-name> --previous
```

## Troubleshooting

### Поды не стартуют

```bash
# Проверить описание
kubectl describe pod -n oneflow-ai <pod-name>

# Проверить события
kubectl get events -n oneflow-ai --sort-by='.lastTimestamp'

# Проверить лимиты
kubectl describe nodes | grep -A 5 "Allocated resources"
```

### Проблемы с Ingress

```bash
# Проверить Ingress
kubectl describe ingress oneflow-ai -n oneflow-ai

# Проверить endpoints
kubectl get endpoints -n oneflow-ai

# Логи ingress controller
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Health Checks не проходят

```bash
# Проверить health endpoint напрямую
kubectl port-forward -n oneflow-ai <pod-name> 8000:8000
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Проверить конфигурацию probes
kubectl get pod -n oneflow-ai <pod-name> -o yaml | grep -A 10 Probe
```

## Security Best Practices

✅ **Реализовано:**
- Non-root пользователь (uid: 1000)
- Read-only root filesystem
- Dropped ALL capabilities
- Seccomp profile: RuntimeDefault
- Network policies
- Resource quotas и limits

⚠️ **TODO для production:**
1. Использовать External Secrets Operator или Vault для секретов
2. Включить Pod Security Standards
3. Настроить RBAC для ServiceAccount
4. Включить audit logging
5. Настроить Falco для runtime security
6. Использовать OPA/Gatekeeper для policy enforcement

## Дополнительные инструменты

### Kustomize overlays для разных окружений

```bash
k8s/
├── base/                  # Базовые манифесты
├── overlays/
│   ├── development/      # Dev окружение
│   ├── staging/          # Staging окружение
│   └── production/       # Production окружение

# Применить для dev
kubectl apply -k k8s/overlays/development/
```

### ArgoCD для GitOps

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: oneflow-ai
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/oneflow-ai
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: oneflow-ai
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Полезные ссылки

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [HPA Walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)

## Поддержка

Для вопросов и проблем: support@oneflow-ai.com
