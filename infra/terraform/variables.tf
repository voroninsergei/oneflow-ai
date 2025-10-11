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
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "oneflow-ai"
}

# ============================================
# API Keys (чувствительные данные)
# ============================================

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
# Secrets Manager Settings
# ============================================

variable "secret_recovery_window_days" {
  description = "Number of days to retain deleted secrets"
  type        = number
  default     = 7
  
  validation {
    condition     = var.secret_recovery_window_days >= 7 && var.secret_recovery_window_days <= 30
    error_message = "Recovery window must be between 7 and 30 days."
  }
}

# ============================================
# IAM Settings
# ============================================

variable "iam_trusted_services" {
  description = "List of AWS services that can assume the IAM role"
  type        = list(string)
  default     = ["ec2.amazonaws.com", "ecs-tasks.amazonaws.com"]
}

# ============================================
# KMS Settings
# ============================================

variable "enable_kms_encryption" {
  description = "Enable KMS encryption for secrets"
  type        = bool
  default     = true
}

variable "kms_deletion_window_days" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.kms_deletion_window_days >= 7 && var.kms_deletion_window_days <= 30
    error_message = "KMS deletion window must be between 7 and 30 days."
  }
}

variable "enable_kms_key_rotation" {
  description = "Enable automatic KMS key rotation"
  type        = bool
  default     = true
}

# ============================================
# CloudWatch Settings
# ============================================

variable "enable_audit_logging" {
  description = "Enable CloudWatch audit logging for secrets"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch logs retention in days"
  type        = number
  default     = 30
  
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period."
  }
}

# ============================================
# Tags
# ============================================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
