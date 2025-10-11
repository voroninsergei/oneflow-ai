# ============================================
# Staging Environment Configuration
# ============================================

environment = "staging"
aws_region  = "us-east-1"

# Secrets Manager
secret_recovery_window_days = 7

# KMS
enable_kms_encryption    = true
kms_deletion_window_days = 7
enable_kms_key_rotation  = true

# CloudWatch
enable_audit_logging = true
log_retention_days   = 14

# IAM
iam_trusted_services = [
  "ec2.amazonaws.com",
  "ecs-tasks.amazonaws.com"
]

# Tags
additional_tags = {
  Environment = "staging"
  Owner       = "QA Team"
}
