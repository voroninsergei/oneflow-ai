# 🚀 Быстрая миграция OneFlow.AI на безопасное хранение секретов

## ⚡ 5-минутная миграция для разработки

### Шаг 1: Установка зависимостей
```bash
pip install python-dotenv
```

### Шаг 2: Автоматическая миграция
```bash
# Запустить скрипт миграции
python migrate_to_env.py

# Скрипт автоматически:
# ✓ Прочитает .api_keys.json
# ✓ Создаст .env файл
# ✓ Сгенерирует JWT secret
# ✓ Создаст резервную копию
```

### Шаг 3: Обновить .gitignore
```bash
# Добавить файлы с секретами в .gitignore
cat >> .gitignore << EOF
.env
.api_keys.json*
secrets.env
EOF
```

### Шаг 4: Тестирование
```bash
# Проверить конфигурацию
python -c "from src.config import get_config; c = get_config(); c.validate(); print('✓ Config OK')"

# Запустить демо
python -m src.main --demo
```

### Шаг 5: Очистка
```bash
# Удалить старый файл (после проверки!)
rm .api_keys.json
```

---

## 🏢 Миграция для Production

### Вариант A: AWS Secrets Manager

#### 1. Создать секрет
```bash
# Используя AWS CLI
aws secretsmanager create-secret \
  --name oneflow-ai/api-keys \
  --secret-string '{
    "openai_api_key":"sk-proj-...",
    "anthropic_api_key":"sk-ant-...",
    "stability_api_key":"sk-...",
    "elevenlabs_api_key":"..."
  }'
```

#### 2. Настроить переменные
```bash
export AWS_SECRET_NAME=oneflow-ai/api-keys
export AWS_REGION=us-east-1
```

#### 3. Запуск
```bash
python -m src.main
```

**Автоматически определится AWS как источник секретов!**

---

### Вариант B: Kubernetes

#### 1. Создать Secret
```bash
kubectl create secret generic oneflow-api-keys \
  --from-literal=openai-key='sk-proj-...' \
  --from-literal=anthropic-key='sk-ant-...' \
  --from-literal=stability-key='sk-...' \
  --from-literal=elevenlabs-key='...' \
  --namespace=oneflow
```

#### 2. Применить deployment
```bash
kubectl apply -f kubernetes-deployment.yaml
```

#### 3. Проверка
```bash
kubectl get pods -n oneflow
kubectl logs -f deployment/oneflow-ai -n oneflow
```

---

### Вариант C: Docker Compose

#### 1. Создать secrets.env
```bash
# Автоматическая генерация
python migrate_to_env.py --docker
```

#### 2. Обновить docker-compose.yml
```yaml
services:
  oneflow-ai:
    env_file:
      - secrets.env
```

#### 3. Запуск
```bash
docker-compose up -d
```

---

### Вариант D: HashiCorp Vault

#### 1. Записать секреты
```bash
vault kv put secret/oneflow-ai/api-keys \
  openai_api_key="sk-proj-..." \
  anthropic_api_key="sk-ant-..." \
  stability_api_key="sk-..." \
  elevenlabs_api_key="..."
```

#### 2. Настроить переменные
```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_TOKEN="s.your-token"
export VAULT_SECRET_PATH="secret/oneflow-ai/api-keys"
```

#### 3. Запуск
```bash
python -m src.main
```

---

## 📋 Чек-лист миграции

### Перед миграцией
- [ ] Сделать резервную копию `.api_keys.json`
- [ ] Убедиться, что `.gitignore` настроен
- [ ] Установить `python-dotenv`
- [ ] Прочитать SECURITY_GUIDE.md

### Во время миграции
- [ ] Запустить `migrate_to_env.py`
- [ ] Проверить созданный `.env` файл
- [ ] Убедиться, что все ключи на месте
- [ ] Установить права 600 на `.env`

### После миграции
- [ ] Протестировать приложение
- [ ] Убедиться, что API работают
- [ ] Удалить `.api_keys.json`
- [ ] Проверить, что файлы не в git: `git status`
- [ ] Настроить pre-commit hooks

### Для production
- [ ] Выбрать Secret Manager
- [ ] Настроить IAM/права доступа
- [ ] Перенести секреты в выбранный Manager
- [ ] Обновить переменные окружения
- [ ] Протестировать в staging
- [ ] Настроить мониторинг
- [ ] Настроить ротацию ключей

---

## 🔍 Проверка безопасности

### Убедитесь, что секреты не в git
```bash
# Проверка staged файлов
git diff --staged --name-only | grep -E '\.(env|api_keys\.json)'

# Поиск паттернов секретов в коммитах
git log --all --full-history -- .env .api_keys.json

# Проверка текущего состояния
git status | grep -E '\.(env|api_keys)'
```

### Удалить секреты из истории git (если были закоммичены)
```bash
# ОПАСНО: Перепишет всю историю!
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .api_keys.json' \
  --prune-empty --tag-name-filter cat -- --all

# Принудительный push
git push origin --force --all
```

---

## 🆘 Troubleshooting

### Проблема: "Missing API keys"
**Решение:**
```bash
# Проверить .env файл
cat .env | grep API_KEY

# Проверить загрузку
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"

# Проверить права
ls -la .env
# Должно быть: -rw------- (600)
```

### Проблема: "python-dotenv not found"
**Решение:**
```bash
pip install python-dotenv
# или
pip install -r requirements.txt
```

### Проблема: AWS "Access Denied"
**Решение:**
```bash
# Проверить credentials
aws sts get-caller-identity

# Проверить доступ к секрету
aws secretsmanager get-secret-value \
  --secret-id oneflow-ai/api-keys

# Добавить IAM политику
aws iam attach-user-policy \
  --user-name your-user \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

### Проблема: Kubernetes "Secret not found"
**Решение:**
```bash
# Проверить секреты
kubectl get secrets -n oneflow

# Описание секрета
kubectl describe secret oneflow-api-keys -n oneflow

# Пересоздать секрет
kubectl delete secret oneflow-api-keys -n oneflow
kubectl create secret generic oneflow-api-keys \
  --from-literal=openai-key='...' \
  --namespace=oneflow
```

---

## 📚 Дополнительная информация

### Документация
- [SECURITY_GUIDE.md](SECURITY_GUIDE.md) - Полное руководство
- [README.md](README.md) - Общая документация
- [.env.example](.env.example) - Шаблон переменных

### Примеры
```bash
# Миграция для всех окружений
python migrate_to_env.py --all

# Только Kubernetes
python migrate_to_env.py --kubernetes

# Только AWS
python migrate_to_env.py --aws

# С кастомным исходным файлом
python migrate_to_env.py --source custom_keys.json
```

### Автоматическое определение источника
```python
from src.config import Config

# OneFlow.AI автоматически определит источник в порядке приоритета:
# 1. AWS_SECRET_NAME → AWS Secrets Manager
# 2. VAULT_ADDR → HashiCorp Vault
# 3. GCP_PROJECT_ID → GCP Secret Manager
# 4. AZURE_VAULT_URL → Azure Key Vault
# 5. /run/secrets → Kubernetes Secrets
# 6. .env file → Environment Variables

config = Config()  # Автоматически определится!
```

---

## ⏱️ Временные затраты

| Окружение | Время миграции | Сложность |
|-----------|----------------|-----------|
| Development (.env) | 5 минут | ⭐ |
| Docker Compose | 10 минут | ⭐⭐ |
| Kubernetes | 15 минут | ⭐⭐ |
| AWS Secrets Manager | 20 минут | ⭐⭐⭐ |
| HashiCorp Vault | 30 минут | ⭐⭐⭐⭐ |
| GCP/Azure | 20 минут | ⭐⭐⭐ |

---

## ✅ Готово!

После миграции ваше приложение:
- ✓ Следует best practices безопасности
- ✓ Соответствует 12-factor app
- ✓ Готово к CI/CD
- ✓ Легко масштабируется
- ✓ Поддерживает ротацию ключей
- ✓ Не хранит секреты в коде

**Безопасность превыше всего! 🔒**