# ============================================
# OneFlow.AI - AWS Secrets Manager Setup
# Terraform Configuration
# ============================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  
  # Опционально: remote state
  # backend "s3" {
  #   bucket = "oneflow-terraform-state"
  #   key    = "secrets/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# ============================================
# Variables
# ============================================

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "oneflow-ai"
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API Key"
  type        = string
  sensitive   = true
}

variable "stability_api_key" {
  description = "Stability AI API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "elevenlabs_api_key" {
  description = "ElevenLabs API Key"
  type        = string
  sensitive   = true
  default     = ""
}

# ============================================
# Provider Configuration
# ============================================

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ============================================
# Random JWT Secret
# ============================================

resource "random_password" "jwt_secret" {
  length  = 32
  special = true
}

# ============================================
# Secrets Manager - API Keys
# ============================================

resource "aws_secretsmanager_secret" "api_keys" {
  name        = "${var.project_name}/${var.environment}/api-keys"
  description = "API Keys for OneFlow.AI AI providers"
  
  recovery_window_in_days = 7
  
  tags = {
    Name        = "${var.project_name}-api-keys"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  
  secret_string = jsonencode({
    openai_api_key     = var.openai_api_key
    anthropic_api_key  = var.anthropic_api_key
    stability_api_key  = var.stability_api_key
    elevenlabs_api_key = var.elevenlabs_api_key
  })
}

# ============================================
# Secrets Manager - JWT Secret
# ============================================

resource "aws_secretsmanager_secret" "jwt_secret" {
  name        = "${var.project_name}/${var.environment}/jwt-secret"
  description = "JWT Secret Key for OneFlow.AI"
  
  recovery_window_in_days = 7
  
  tags = {
    Name        = "${var.project_name}-jwt-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id = aws_secretsmanager_secret.jwt_secret.id
  
  secret_string = jsonencode({
    jwt_secret_key = random_password.jwt_secret.result
  })
}

# ============================================
# IAM Policy - Read Secrets
# ============================================

resource "aws_iam_policy" "read_secrets" {
  name        = "${var.project_name}-${var.environment}-read-secrets"
  description = "Allow reading OneFlow.AI secrets"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.api_keys.arn,
          aws_secretsmanager_secret.jwt_secret.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "secretsmanager.${var.aws_region}.amazonaws.com"
          }
        }
      }
    ]
  })
}

# ============================================
# IAM Role - EC2/ECS
# ============================================

resource "aws_iam_role" "oneflow_app" {
  name = "${var.project_name}-${var.environment}-app-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "ec2.amazonaws.com",
            "ecs-tasks.amazonaws.com"
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = {
    Name        = "${var.project_name}-app-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "oneflow_app_secrets" {
  role       = aws_iam_role.oneflow_app.name
  policy_arn = aws_iam_policy.read_secrets.arn
}

# ============================================
# Instance Profile (для EC2)
# ============================================

resource "aws_iam_instance_profile" "oneflow_app" {
  name = "${var.project_name}-${var.environment}-instance-profile"
  role = aws_iam_role.oneflow_app.name
}

# ============================================
# KMS Key (опционально, для дополнительного шифрования)
# ============================================

resource "aws_kms_key" "secrets" {
  description             = "KMS key for ${var.project_name} secrets"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  tags = {
    Name        = "${var.project_name}-secrets-key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.project_name}-${var.environment}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# ============================================
# CloudWatch Log Group (для аудита)
# ============================================

resource "aws_cloudwatch_log_group" "secrets_audit" {
  name              = "/aws/secretsmanager/${var.project_name}/${var.environment}"
  retention_in_days = 30
  
  tags = {
    Name        = "${var.project_name}-secrets-audit"
    Environment = var.environment
  }
}

# ============================================
# Secrets Rotation Lambda (опционально)
# ============================================

# Раскомментируйте для автоматической ротации секретов

# resource "aws_lambda_function" "rotate_secrets" {
#   filename      = "lambda_rotation.zip"
#   function_name = "${var.project_name}-${var.environment}-rotate-secrets"
#   role          = aws_iam_role.lambda_rotation.arn
#   handler       = "index.handler"
#   runtime       = "python3.11"
#   timeout       = 60
#   
#   environment {
#     variables = {
#       SECRET_ARN = aws_secretsmanager_secret.api_keys.arn
#     }
#   }
# }

# resource "aws_secretsmanager_secret_rotation" "api_keys" {
#   secret_id           = aws_secretsmanager_secret.api_keys.id
#   rotation_lambda_arn = aws_lambda_function.rotate_secrets.arn
#   
#   rotation_rules {
#     automatically_after_days = 90
#   }
# }

# ============================================
# Outputs
# ============================================

output "api_keys_secret_arn" {
  description = "ARN of API keys secret"
  value       = aws_secretsmanager_secret.api_keys.arn
}

output "jwt_secret_arn" {
  description = "ARN of JWT secret"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}

output "app_role_arn" {
  description = "ARN of IAM role for application"
  value       = aws_iam_role.oneflow_app.arn
}

output "instance_profile_name" {
  description = "Name of instance profile for EC2"
  value       = aws_iam_instance_profile.oneflow_app.name
}

output "kms_key_id" {
  description = "KMS key ID for secrets encryption"
  value       = aws_kms_key.secrets.id
}

# ============================================
# Использование:
# ============================================
#
# 1. Инициализация:
#    terraform init
#
# 2. Создание файла с переменными (terraform.tfvars):
#    echo 'openai_api_key = "sk-proj-..."' > terraform.tfvars
#    echo 'anthropic_api_key = "sk-ant-..."' >> terraform.tfvars
#    echo 'environment = "prod"' >> terraform.tfvars
#
# 3. План:
#    terraform plan
#
# 4. Применение:
#    terraform apply
#
# 5. Получение outputs:
#    terraform output api_keys_secret_arn
#
# 6. Использование в приложении:
#    export AWS_SECRET_NAME=$(terraform output -raw api_keys_secret_arn)
#    python -m src.main
#
# 7. Удаление (осторожно!):
#    terraform destroy
#
