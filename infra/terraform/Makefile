# ============================================
# OneFlow.AI Terraform Makefile
# ============================================

.PHONY: help init plan apply destroy fmt validate clean setup-backend

# Default environment
ENV ?= dev

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)OneFlow.AI Terraform Management$(NC)"
	@echo ""
	@echo "Usage:"
	@echo "  make [target] ENV=[dev|staging|prod]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup-backend: ## Create S3 bucket and DynamoDB table for backend
	@echo "$(YELLOW)Creating Terraform backend resources...$(NC)"
	@aws s3api create-bucket \
		--bucket oneflow-terraform-state \
		--region us-east-1 || true
	@aws s3api put-bucket-versioning \
		--bucket oneflow-terraform-state \
		--versioning-configuration Status=Enabled
	@aws s3api put-bucket-encryption \
		--bucket oneflow-terraform-state \
		--server-side-encryption-configuration \
		'{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
	@aws dynamodb create-table \
		--table-name oneflow-terraform-locks \
		--attribute-definitions AttributeName=LockID,AttributeType=S \
		--key-schema AttributeName=LockID,KeyType=HASH \
		--billing-mode PAY_PER_REQUEST \
		--region us-east-1 || true
	@echo "$(GREEN)Backend resources created successfully!$(NC)"

init: ## Initialize Terraform with backend
	@echo "$(YELLOW)Initializing Terraform for $(ENV) environment...$(NC)"
	@terraform init -backend-config=backend.hcl -reconfigure
	@echo "$(GREEN)Terraform initialized!$(NC)"

plan: ## Show Terraform plan for selected environment
	@echo "$(YELLOW)Planning changes for $(ENV) environment...$(NC)"
	@terraform plan \
		-var-file="environments/$(ENV).tfvars" \
		-var-file="terraform.tfvars" \
		-out=tfplan-$(ENV)
	@echo "$(GREEN)Plan saved to tfplan-$(ENV)$(NC)"

apply: ## Apply Terraform changes for selected environment
	@echo "$(RED)Applying changes for $(ENV) environment...$(NC)"
	@terraform apply tfplan-$(ENV)
	@rm -f tfplan-$(ENV)
	@echo "$(GREEN)Changes applied successfully!$(NC)"

apply-auto: ## Apply Terraform changes without confirmation
	@echo "$(RED)Auto-applying changes for $(ENV) environment...$(NC)"
	@terraform apply \
		-var-file="environments/$(ENV).tfvars" \
		-var-file="terraform.tfvars" \
		-auto-approve
	@echo "$(GREEN)Changes applied successfully!$(NC)"

destroy: ## Destroy Terraform resources for selected environment
	@echo "$(RED)WARNING: This will destroy all resources in $(ENV) environment!$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@terraform destroy \
		-var-file="environments/$(ENV).tfvars" \
		-var-file="terraform.tfvars"

fmt: ## Format Terraform files
	@echo "$(YELLOW)Formatting Terraform files...$(NC)"
	@terraform fmt -recursive
	@echo "$(GREEN)Files formatted!$(NC)"

validate: ## Validate Terraform configuration
	@echo "$(YELLOW)Validating Terraform configuration...$(NC)"
	@terraform validate
	@echo "$(GREEN)Configuration is valid!$(NC)"

output: ## Show Terraform outputs for selected environment
	@echo "$(YELLOW)Outputs for $(ENV) environment:$(NC)"
	@terraform output

output-json: ## Show Terraform outputs in JSON format
	@terraform output -json > outputs-$(ENV).json
	@echo "$(GREEN)Outputs saved to outputs-$(ENV).json$(NC)"

state-list: ## List all resources in state
	@terraform state list

state-show: ## Show specific resource (use RESOURCE=resource_name)
	@terraform state show $(RESOURCE)

clean: ## Clean temporary files
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	@rm -f tfplan-*
	@rm -f outputs-*.json
	@echo "$(GREEN)Cleanup complete!$(NC)"

lint: ## Run terraform fmt check
	@echo "$(YELLOW)Checking Terraform formatting...$(NC)"
	@terraform fmt -check -recursive

security-scan: ## Run security scan with tfsec (requires tfsec)
	@echo "$(YELLOW)Running security scan...$(NC)"
	@tfsec . || true

docs: ## Generate documentation (requires terraform-docs)
	@echo "$(YELLOW)Generating documentation...$(NC)"
	@terraform-docs markdown table . > TERRAFORM.md
	@echo "$(GREEN)Documentation generated in TERRAFORM.md$(NC)"

# Quick commands for specific environments
dev-plan: ENV=dev
dev-plan: plan ## Plan for dev environment

dev-apply: ENV=dev
dev-apply: apply ## Apply for dev environment

staging-plan: ENV=staging
staging-plan: plan ## Plan for staging environment

staging-apply: ENV=staging
staging-apply: apply ## Apply for staging environment

prod-plan: ENV=prod
prod-plan: plan ## Plan for prod environment

prod-apply: ENV=prod
prod-apply: apply ## Apply for prod environment

# Get secret values (use carefully!)
get-api-keys: ## Get API keys from Secrets Manager
	@aws secretsmanager get-secret-value \
		--secret-id oneflow-ai/$(ENV)/api-keys \
		--query SecretString \
		--output text | jq '.'

get-jwt-secret: ## Get JWT secret from Secrets Manager
	@aws secretsmanager get-secret-value \
		--secret-id oneflow-ai/$(ENV)/jwt-secret \
		--query SecretString \
		--output text | jq '.'
