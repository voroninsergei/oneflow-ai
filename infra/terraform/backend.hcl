# ============================================
# Terraform Backend Configuration
# ============================================

bucket         = "oneflow-terraform-state"
key            = "secrets/terraform.tfstate"
region         = "us-east-1"
encrypt        = true
dynamodb_table = "oneflow-terraform-locks"

# Рекомендуется создать S3 bucket и DynamoDB table заранее:
#
# aws s3api create-bucket \
#   --bucket oneflow-terraform-state \
#   --region us-east-1
#
# aws s3api put-bucket-versioning \
#   --bucket oneflow-terraform-state \
#   --versioning-configuration Status=Enabled
#
# aws s3api put-bucket-encryption \
#   --bucket oneflow-terraform-state \
#   --server-side-encryption-configuration \
#   '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
#
# aws dynamodb create-table \
#   --table-name oneflow-terraform-locks \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --billing-mode PAY_PER_REQUEST \
#   --region us-east-1
