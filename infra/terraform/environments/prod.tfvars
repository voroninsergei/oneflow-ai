# ============================================
# Production Environment Configuration
# ============================================

environment = "prod"
aws_region  = "us-east-1"

# Secrets Manager
secret_recovery_window_days = 30  # Maximum retention in production

# KMS
enable_kms_encryption    = true
kms_deletion_window_days = 30
enable_kms_key_rotation  = true

# CloudWatch
enable_audit_logging = true
log_retention_days   = 90

# IAM
iam_trusted_services = [
  "ec2.amazonaws.com",
  "ecs-tasks.amazonaws.com"
]

# Tags
additional_tags = {
  Environment    = "production"
  Owner          = "DevOps Team"
  CostCenter     = "Engineering"
  Compliance     = "SOC2"
  BackupRequired = "true"
}
