# OneFlow.AI Terraform Configuration

Terraform конфигурация для управления AWS Secrets Manager и IAM ролями.

## Структура проекта

```
infra/terraform/
├── main.tf                      # Основная конфигурация
├── variables.tf                 # Определение переменных
├── outputs.tf                   # Выходные значения
├── backend.hcl                  # Конфигурация удалённого backend
├── terraform.tfvars.example     # Пример файла с переменными
├── .gitignore                   # Git ignore для чувствительных файлов
├── environments/
│   ├── dev.tfvars              # Переменные для dev
│   ├── staging.tfvars          # Переменные для staging
│   └── prod.tfvars             # Переменные для prod
└── README.md                    # Эта документация
```

## Предварительные требования

1. **Terraform** >= 1.0
2. **AWS CLI** настроенный с credentials
3. **S3 bucket** для хранения state
4. **DynamoDB table** для lock management

### Создание S3 backend

```bash
# Создать S3 bucket
aws s3api create-bucket \
  --bucket oneflow-terraform-state \
  --region us-east-1

# Включить versioning
aws s3api put-bucket-versioning \
  --bucket oneflow-terraform-state \
  --versioning-configuration Status=Enabled

# Включить encryption
aws s3api put-bucket-encryption \
  --bucket oneflow-terraform-state \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Создать DynamoDB table для locks
aws dynamodb create-table \
  --table-name oneflow-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

## Использование

### 1. Инициализация

```bash
cd infra/terraform

# Инициализация с backend
terraform init -backend-config=backend.hcl
```

### 2. Подготовка переменных

```bash
# Создать файл с секретами (НЕ коммитить!)
cp terraform.tfvars.example terraform.tfvars

# Отредактировать terraform.tfvars
nano terraform.tfvars
```

**terraform.tfvars** должен содержать:
```hcl
openai_api_key    = "sk-proj-..."
anthropic_api_key = "sk-ant-..."
# ... другие API ключи
```

### 3. Применение для разных окружений

#### Development

```bash
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

#### Staging

```bash
terraform plan -var-file="environments/staging.tfvars"
terraform apply -var-file="environments/staging.tfvars"
```

#### Production

```bash
terraform plan -var-file="environments/prod.tfvars"
terraform apply -var-file="environments/prod.tfvars"
```

### 4. Получение outputs

```bash
# Получить ARN секрета с API ключами
terraform output api_keys_secret_arn

# Получить имя instance profile
terraform output instance_profile_name

# Получить все outputs в JSON
terraform output -json > outputs.json
```

## Использование секретов в приложении

### Python

```python
import boto3
import json

def get_api_keys():
    session = boto3.session.Session()
    client = session.client('secretsmanager', region_name='us-east-1')
    
    secret_arn = "arn:aws:secretsmanager:us-east-1:..."
    response = client.get_secret_value(SecretId=secret_arn)
    
    return json.loads(response['SecretString'])

keys = get_api_keys()
openai_key = keys['openai_api_key']
```

### AWS CLI

```bash
# Получить секрет
aws secretsmanager get-secret-value \
  --secret-id oneflow-ai/prod/api-keys \
  --query SecretString \
  --output text | jq -r '.openai_api_key'
```

### Docker / Environment Variables

```bash
# Экспорт в переменные окружения
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id oneflow-ai/prod/api-keys \
  --query SecretString --output text | jq -r '.openai_api_key')
```

## Безопасность

### ⚠️ ВАЖНО

1. **НЕ коммитить** файлы `*.tfvars` с реальными API ключами
2. **Использовать** AWS IAM roles вместо hardcoded credentials
3. **Включить** MFA для Terraform operations в production
4. **Ротировать** секреты регулярно (каждые 90 дней)
5. **Мониторить** доступ к секретам через CloudWatch

### IAM Permissions

Для работы Terraform нужны следующие permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:*",
        "iam:*",
        "kms:*",
        "logs:*",
        "s3:*",
        "dynamodb:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Управление State

### Просмотр state

```bash
terraform state list
terraform state show aws_secretsmanager_secret.api_keys
```

### Импорт существующих ресурсов

```bash
terraform import aws_secretsmanager_secret.api_keys arn:aws:secretsmanager:...
```

### Backup state

```bash
# State автоматически версионируется в S3
# Просмотр версий
aws s3api list-object-versions \
  --bucket oneflow-terraform-state \
  --prefix secrets/terraform.tfstate
```

## Troubleshooting

### Ошибка: "Backend initialization required"

```bash
terraform init -reconfigure -backend-config=backend.hcl
```

### Ошибка: "Resource already exists"

```bash
# Импортировать существующий ресурс
terraform import aws_secretsmanager_secret.api_keys <secret-arn>
```

### Ошибка: "Access denied to secret"

```bash
# Проверить IAM permissions
aws sts get-caller-identity
aws iam get-user
```

## Очистка ресурсов

```bash
# ⚠️ ОСТОРОЖНО! Удалит все ресурсы
terraform destroy -var-file="environments/dev.tfvars"
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Terraform Apply
  run: |
    cd infra/terraform
    terraform init -backend-config=backend.hcl
    terraform apply -var-file="environments/${{ env.ENVIRONMENT }}.tfvars" -auto-approve
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    TF_VAR_openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    TF_VAR_anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Дополнительная информация

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [Terraform Backend S3](https://www.terraform.io/docs/language/settings/backends/s3.html)
