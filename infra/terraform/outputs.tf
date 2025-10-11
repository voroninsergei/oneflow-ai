# ============================================
# Outputs
# ============================================

output "api_keys_secret_arn" {
  description = "ARN of API keys secret"
  value       = aws_secretsmanager_secret.api_keys.arn
}

output "api_keys_secret_name" {
  description = "Name of API keys secret"
  value       = aws_secretsmanager_secret.api_keys.name
}

output "jwt_secret_arn" {
  description = "ARN of JWT secret"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}

output "jwt_secret_name" {
  description = "Name of JWT secret"
  value       = aws_secretsmanager_secret.jwt_secret.name
}

output "app_role_arn" {
  description = "ARN of IAM role for application"
  value       = aws_iam_role.oneflow_app.arn
}

output "app_role_name" {
  description = "Name of IAM role for application"
  value       = aws_iam_role.oneflow_app.name
}

output "instance_profile_name" {
  description = "Name of instance profile for EC2"
  value       = aws_iam_instance_profile.oneflow_app.name
}

output "instance_profile_arn" {
  description = "ARN of instance profile for EC2"
  value       = aws_iam_instance_profile.oneflow_app.arn
}

output "kms_key_id" {
  description = "KMS key ID for secrets encryption"
  value       = var.enable_kms_encryption ? aws_kms_key.secrets[0].id : null
}

output "kms_key_arn" {
  description = "KMS key ARN for secrets encryption"
  value       = var.enable_kms_encryption ? aws_kms_key.secrets[0].arn : null
}

output "secrets_policy_arn" {
  description = "ARN of IAM policy for reading secrets"
  value       = aws_iam_policy.read_secrets.arn
}

output "audit_log_group_name" {
  description = "Name of CloudWatch log group for audit"
  value       = var.enable_audit_logging ? aws_cloudwatch_log_group.secrets_audit[0].name : null
}
