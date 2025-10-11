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
  
  backend "s3" {
    # Параметры задаются через backend-config при init
    # terraform init -backend-config=backend.hcl
  }
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
  
  recovery_window_in_days = var.secret_recovery_window_days
  
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
  
  recovery_window_in_days = var.secret_recovery_window_days
  
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
          Service = var.iam_trusted_services
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
# KMS Key
# ============================================

resource "aws_kms_key" "secrets" {
  count = var.enable_kms_encryption ? 1 : 0
  
  description             = "KMS key for ${var.project_name} secrets"
  deletion_window_in_days = var.kms_deletion_window_days
  enable_key_rotation     = var.enable_kms_key_rotation
  
  tags = {
    Name        = "${var.project_name}-secrets-key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "secrets" {
  count = var.enable_kms_encryption ? 1 : 0
  
  name          = "alias/${var.project_name}-${var.environment}-secrets"
  target_key_id = aws_kms_key.secrets[0].key_id
}

# ============================================
# CloudWatch Log Group
# ============================================

resource "aws_cloudwatch_log_group" "secrets_audit" {
  count = var.enable_audit_logging ? 1 : 0
  
  name              = "/aws/secretsmanager/${var.project_name}/${var.environment}"
  retention_in_days = var.log_retention_days
  
  tags = {
    Name        = "${var.project_name}-secrets-audit"
    Environment = var.environment
  }
}
