# 🔒 Руководство по безопасному хранению секретов в OneFlow.AI

## Содержание
1. [Почему это важно](#почему-это-важно)
2. [Методы хранения секретов](#методы-хранения-секретов)
3. [Быстрый старт](#быстрый-старт)
4. [Продакшен-конфигурации](#продакшен-конфигурации)
5. [Миграция со старого подхода](#миграция-со-старого-подхода)
6. [Лучшие практики](#лучшие-практики)
7. [Troubleshooting](#troubleshooting)

---

## Почему это важно

### ❌ Старый подход (НЕБЕЗОПАСНО)
```json
// .api_keys.json
{
  "openai": "sk-proj-...",
  "anthropic": "sk-ant-..."
}
```

**Проблемы:**
- ✗ Ключи в открытом виде
- ✗ Риск случайного коммита
- ✗ Нет шифрования
- ✗ Сложно ротировать ключи
- ✗ Не соответствует 12-factor app

### ✅ Новый подход (БЕЗОПАСНО)
```bash
# Переменные окружения
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Преимущества:**
- ✓ Следует принципам 12-factor app
- ✓ Не попадают в git
- ✓ Легко изменять без изменения кода
- ✓ Поддержка различных окружений (dev/staging/prod)
- ✓ Совместимость с CI/CD
- ✓ Поддержка enterprise secret managers

---

## Методы хранения секретов

OneFlow.AI поддерживает 6 методов хранения секретов:

| Метод | Сложность | Безопасность | Рекомендация |
|-------|-----------|--------------|--------------|
| **Environment Variables** | ⭐ | ⭐⭐ | Development |
| **Docker Secrets** | ⭐⭐ | ⭐⭐⭐ | Small Production |
| **Kubernetes Secrets** | ⭐⭐ | ⭐⭐⭐ | K8s Deployments |
| **AWS Secrets Manager** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | AWS Production |
| **HashiCorp Vault** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Enterprise |
| **GCP Secret Manager** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | GCP Production |
| **Azure Key Vault** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Azure Production |

---

## Быстрый старт

### 1. Установка зависимостей

```bash
# Базовые зависимости (всегда нужны)
pip install python-dotenv

# Для AWS
pip install boto3

# Для Vault
pip install hvac

# Для GCP
pip install google-cloud-secret-manager

# Для Azure
pip install azure-keyvault-secrets azure-identity

# Или установить все сразу
pip install -r requirements.txt
```

### 2. Создание .env файла

```bash
# Скопировать шаблон
cp .env.example .env

# Отредактировать .env
nano .env
```

### 3. Добавить .env в .gitignore

```bash
echo ".env" >> .gitignore
echo ".api_keys.json" >> .gitignore
```

### 4. Использование в коде

```python
from src.config import get_config

# Автоматическое определение источника секретов
config = get_config()
config.validate()

# Получение API ключа
openai_key = config.OPENAI_API_KEY
# или
openai_key = config.get_provider_key('openai')
```

---

## Продакшен-конфигурации

### 🔹 1. Environment Variables (.env)

**Когда использовать:** Локальная разработка, небольшие проекты

**Настройка:**
```bash
# .env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Использование:**
```python
# Автоматически определится
config = Config()
```

---

### 🔹 2. Docker Secrets

**Когда использовать:** Docker Swarm, небольшой production

**Настройка:**
```bash
# Создать secrets
echo "sk-proj-..." | docker secret create openai_key -
echo "sk-ant-..." | docker secret create anthropic_key -
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  oneflow-ai:
    image: oneflow-ai:latest
    secrets:
      - openai_key
      - anthropic_key
    environment:
      K8S_SECRET_PATH: /run/secrets

secrets:
  openai_key:
    external: true
  anthropic_key:
    external: true
```

---

### 🔹 3. Kubernetes Secrets

**Когда использовать:** Kubernetes deployments

**Создание секрета:**
```bash
# Из файла
kubectl create secret generic oneflow-api-keys \
  --from-literal=openai-key='sk-proj-...' \
  --from-literal=anthropic-key='sk-ant-...'

# Или из YAML
kubectl apply -f secrets.yaml
```

**secrets.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: oneflow-api-keys
type: Opaque
stringData:
  openai-key: sk-proj-...
  anthropic-key: sk-ant-...
```

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oneflow-ai
spec:
  template:
    spec:
      containers:
      - name: oneflow-ai
        image: oneflow-ai:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: oneflow-api-keys
              key: openai-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: oneflow-api-keys
              key: anthropic-key
```

---

### 🔹 4. AWS Secrets Manager

**Когда использовать:** Production на AWS

**Создание секрета:**
```bash
aws secretsmanager create-secret \
  --name oneflow-ai/api-keys \
  --secret-string '{
    "openai_api_key":"sk-proj-...",
    "anthropic_api_key":"sk-ant-..."
  }'
```

**Настройка:**
```bash
# .env или environment variables
AWS_SECRET_NAME=oneflow-ai/api-keys
AWS_REGION=us-east-1
```

**IAM Policy для EC2/ECS:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "secretsmanager:GetSecretValue"
    ],
    "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:oneflow-ai/*"
  }]
}
```

---

### 🔹 5. HashiCorp Vault

**Когда использовать:** Enterprise, мультиоблачные развертывания

**Настройка Vault:**
```bash
# Включить KV секреты v2
vault secrets enable -path=secret kv-v2

# Записать секреты
vault kv put secret/oneflow-ai/api-keys \
  openai_api_key="sk-proj-..." \
  anthropic_api_key="sk-ant-..."
```

**Конфигурация приложения:**
```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_TOKEN="s.your-token"
export VAULT_SECRET_PATH="secret/oneflow-ai/api-keys"
```

**AppRole authentication (рекомендуется):**
```bash
# Создать AppRole
vault auth enable approle

vault write auth/approle/role/oneflow-ai \
  token_policies="oneflow-policy" \
  token_ttl=1h \
  token_max_ttl=4h

# Получить credentials
vault read auth/approle/role/oneflow-ai/role-id
vault write -f auth/approle/role/oneflow-ai/secret-id
```

---

### 🔹 6. Google Cloud Secret Manager

**Когда использовать:** Production на GCP

**Создание секретов:**
```bash
# OpenAI ключ
echo -n "sk-proj-..." | gcloud secrets create openai-api-key \
  --data-file=-

# Anthropic ключ
echo -n "sk-ant-..." | gcloud secrets create anthropic-api-key \
  --data-file=-
```

**Конфигурация:**
```bash
export GCP_PROJECT_ID=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Service Account права:**
```bash
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:oneflow@your-project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

### 🔹 7. Azure Key Vault

**Когда использовать:** Production на Azure

**Создание Key Vault:**
```bash
# Создать Key Vault
az keyvault create \
  --name oneflow-vault \
  --resource-group oneflow-rg \
  --location eastus

# Добавить секреты
az keyvault secret set \
  --vault-name oneflow-vault \
  --name openai-api-key \
  --value "sk-proj-..."
```

**Конфигурация:**
```bash
export AZURE_VAULT_URL="https://oneflow-vault.vault.azure.net/"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

---

## Миграция со старого подхода

### Шаг 1: Экспорт ключей из .api_keys.json

```python
# migrate_secrets.py
import json
import os

# Прочитать старый файл
with open('.api_keys.json', 'r') as f:
    old_keys = json.load(f)

# Создать .env файл
with open('.env', 'w') as f:
    f.write('# API Keys\n')
    f.write(f'OPENAI_API_KEY={old_keys.get("openai", "")}\n')
    f.write(f'ANTHROPIC_API_KEY={old_keys.get("anthropic", "")}\n')
    f.write(f'STABILITY_API_KEY={old_keys.get("stability", "")}\n')
    f.write(f'ELEVENLABS_API_KEY={old_keys.get("elevenlabs", "")}\n')

print("✓ .env файл создан")
print("! Удалите .api_keys.json после проверки")
```

### Шаг 2: Обновление кода

```python
# Старый код
from src.config import load_api_keys
keys = load_api_keys()  # Читал .api_keys.json
openai_key = keys['openai']

# Новый код
from src.config import get_config
config = get_config()
openai_key = config.OPENAI_API_KEY
```

### Шаг 3: Очистка

```bash
# Удалить старый файл
rm .api_keys.json

# Удалить из истории git (если был закоммичен!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .api_keys.json' \
  --prune-empty --tag-name-filter cat -- --all
```

---

## Лучшие практики

### ✅ DO's

1. **Используйте разные ключи для разных окружений**
   ```bash
   # development.env
   OPENAI_API_KEY=sk-proj-dev-...
   
   # production.env
   OPENAI_API_KEY=sk-proj-prod-...
   ```

2. **Ротируйте ключи регулярно**
   - Рекомендуется: каждые 90 дней
   - Минимум: каждые 180 дней

3. **Используйте минимальные права доступа**
   - AWS: только GetSecretValue
   - GCP: только Secret Manager Secret Accessor
   - Vault: минимальные policies

4. **Логируйте только замаскированные ключи**
   ```python
   config = get_config()
   print(config.mask_secrets())  # Покажет: sk-pr...xyz
   ```

5. **Валидируйте конфигурацию при старте**
   ```python
   config = get_config()
   config.validate(strict=True)  # Выбросит ошибку если ключей нет
   ```

### ❌ DON'Ts

1. **Никогда не коммитьте секреты**
   ```bash
   # Проверка перед коммитом
   git diff --staged | grep -i "api_key\|secret\|password"
   ```

2. **Не используйте секреты в URL или query параметрах**
   ```python
   # ❌ Плохо
   f"https://api.example.com?key={api_key}"
   
   # ✅ Хорошо
   headers = {"Authorization": f"Bearer {api_key}"}
   ```

3. **Не логируйте секреты целиком**
   ```python
   # ❌ Плохо
   logger.info(f"API Key: {api_key}")
   
   # ✅ Хорошо
   logger.info(f"API Key: {api_key[:4]}...{api_key[-4:]}")
   ```

4. **Не храните секреты в коде**
   ```python
   # ❌ Плохо
   OPENAI_KEY = "sk-proj-hardcoded"
   
   # ✅ Хорошо
   OPENAI_KEY = os.getenv("OPENAI_API_KEY")
   ```

---

## Troubleshooting

### Проблема: "Missing API keys"

**Решение:**
```bash
# Проверьте, что .env файл существует
ls -la .env

# Проверьте, что python-dotenv установлен
pip list | grep dotenv

# Проверьте, что переменные загружаются
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Проблема: AWS "Access Denied"

**Решение:**
```bash
# Проверьте IAM роль/пользователя
aws sts get-caller-identity

# Проверьте политику
aws iam get-policy-version \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite \
  --version-id v1

# Тестовый доступ
aws secretsmanager get-secret-value \
  --secret-id oneflow-ai/api-keys
```

### Проблема: Vault "Permission Denied"

**Решение:**
```bash
# Проверьте токен
vault token lookup

# Проверьте политику
vault policy read oneflow-policy

# Проверьте путь
vault kv get secret/oneflow-ai/api-keys
```

### Проблема: GCP "PermissionDenied"

**Решение:**
```bash
# Проверьте service account
gcloud auth list

# Проверьте права
gcloud projects get-iam-policy your-project-id \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/secretmanager.secretAccessor"

# Тестовый доступ
gcloud secrets versions access latest --secret=openai-api-key
```

---

## Дополнительные ресурсы

- [12-Factor App Config](https://12factor.net/config)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [GCP Secret Manager Guide](https://cloud.google.com/secret-manager/docs)

---

## Поддержка

Если у вас возникли проблемы:
1. Проверьте [Troubleshooting](#troubleshooting) секцию
2. Создайте issue на GitHub
3. Напишите на voroninsergeiai@gmail.com

---

**Безопасность — это не опция, это необходимость!** 🔐
