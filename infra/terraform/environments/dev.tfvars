# ============================================
# Development Environment Configuration
# ============================================

environment = "dev"
aws_region  = "us-east-1"

# Secrets Manager
secret_recovery_window_days = 7

# KMS
enable_kms_encryption    = false  # Disable KMS in dev to save costs
kms_deletion_window_days = 7
enable_kms_key_rotation  = false

# CloudWatch
enable_audit_logging = false  # Disable audit logging in dev
log_retention_days   = 7

# IAM
iam_trusted_services = [
  "ec2.amazonaws.com"
]

# Tags
additional_tags = {
  Environment = "development"
  AutoShutdown = "true"
}
