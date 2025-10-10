# OneFlow.AI - Production Security Guide
## Руководство по безопасности для Production

---

## 🚨 CRITICAL: API Keys Security

### ❌ NEVER DO THIS (Current README approach)

```bash
# DON'T store API keys in .api_keys.json in production
{
  "openai": "sk-proj-...",
  "anthropic": "sk-ant-..."
}
```

**Why this is dangerous:**
- File can be accidentally committed to git
- Accessible to anyone with filesystem access
- No audit trail for key access
- No rotation mechanism
- Hard to revoke in case of breach

---

## ✅ Production-Grade Solutions

### Option 1: Environment Variables (Minimum)

**Setup:**
```bash
# .env file (add to .gitignore!)
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
STABILITY_API_KEY=sk-your-key-here
ELEVENLABS_API_KEY=your-key-here

# Load in application
export $(cat .env | xargs)
```

**In code:**
```python
import os

api_keys = {
    'openai': os.getenv('OPENAI_API_KEY'),
    'anthropic': os.getenv('ANTHROPIC_API_KEY'),
    'stability': os.getenv('STABILITY_API_KEY'),
    'elevenlabs': os.getenv('ELEVENLABS_API_KEY')
}

# Validate
for provider, key in api_keys.items():
    if not key:
        raise ValueError(f"Missing API key for {provider}")
```

**Deployment:**
```bash
# Kubernetes
kubectl create secret generic oneflow-api-keys \
  --from-literal=openai-key="sk-proj-..." \
  --from-literal=anthropic-key="sk-ant-..."

# Docker
docker run -e OPENAI_API_KEY="sk-proj-..." oneflow-ai:latest

# Systemd service
echo "Environment=OPENAI_API_KEY=sk-proj-..." >> /etc/systemd/system/oneflow.service
```

---

### Option 2: HashiCorp Vault (Recommended)

**Why Vault:**
- ✅ Centralized secret management
- ✅ Automatic rotation
- ✅ Audit logging
- ✅ Fine-grained access control
- ✅ Encryption at rest and in transit

**Setup:**

```bash
# 1. Install Vault
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
unzip vault_*_linux_amd64.zip
sudo mv vault /usr/local/bin/

# 2. Start Vault server (dev mode for testing)
vault server -dev

# 3. Set environment
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# 4. Store secrets
vault kv put secret/oneflow/api-keys \
  openai="sk-proj-..." \
  anthropic="sk-ant-..." \
  stability="sk-..." \
  elevenlabs="..."
```

**Python Integration:**

```python
import hvac
import os

class VaultAPIKeyManager:
    """API key manager using HashiCorp Vault."""
    
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
            token=os.getenv('VAULT_TOKEN')
        )
        
        if not self.client.is_authenticated():
            raise ValueError("Failed to authenticate with Vault")
    
    def get_api_keys(self) -> dict:
        """Retrieve all API keys from Vault."""
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(
                path='oneflow/api-keys',
                mount_point='secret'
            )
            return secret['data']['data']
        except Exception as e:
            raise ValueError(f"Failed to retrieve API keys from Vault: {e}")
    
    def rotate_key(self, provider: str, new_key: str):
        """Rotate API key for a provider."""
        current_keys = self.get_api_keys()
        current_keys[provider] = new_key
        
        self.client.secrets.kv.v2.create_or_update_secret(
            path='oneflow/api-keys',
            secret=current_keys,
            mount_point='secret'
        )

# Usage
vault_manager = VaultAPIKeyManager()
api_keys = vault_manager.get_api_keys()
```

**Dependencies:**
```bash
pip install hvac  # HashiCorp Vault client
```

---

### Option 3: AWS Secrets Manager

**Why AWS Secrets Manager:**
- ✅ Native AWS integration
- ✅ Automatic rotation
- ✅ IAM-based access control
- ✅ Encryption with KMS
- ✅ CloudWatch logging

**Setup:**

```bash
# Install AWS CLI
pip install awscli boto3

# Create secret
aws secretsmanager create-secret \
  --name oneflow/api-keys \
  --secret-string '{
    "openai": "sk-proj-...",
    "anthropic": "sk-ant-...",
    "stability": "sk-...",
    "elevenlabs": "..."
  }'

# Grant access via IAM policy
aws iam put-role-policy \
  --role-name oneflow-app-role \
  --policy-name SecretsAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:*:*:secret:oneflow/*"
    }]
  }'
```

**Python Integration:**

```python
import boto3
import json
from botocore.exceptions import ClientError

class AWSSecretsManager:
    """API key manager using AWS Secrets Manager."""
    
    def __init__(self, region_name: str = 'us-east-1'):
        self.client = boto3.client(
            'secretsmanager',
            region_name=region_name
        )
        self.secret_name = 'oneflow/api-keys'
    
    def get_api_keys(self) -> dict:
        """Retrieve API keys from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(
                SecretId=self.secret_name
            )
            
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            else:
                raise ValueError("Secret is binary, expected JSON string")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise ValueError("Failed to decrypt secret")
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise ValueError("Secret not found")
            else:
                raise
    
    def update_key(self, provider: str, new_key: str):
        """Update a specific API key."""
        current_keys = self.get_api_keys()
        current_keys[provider] = new_key
        
        self.client.put_secret_value(
            SecretId=self.secret_name,
            SecretString=json.dumps(current_keys)
        )

# Usage
aws_manager = AWSSecretsManager(region_name='us-east-1')
api_keys = aws_manager.get_api_keys()
```

---

### Option 4: Google Cloud Secret Manager

**Setup:**

```bash
# Install gcloud SDK
curl https://sdk.cloud.google.com | bash

# Create secrets
echo -n "sk-proj-..." | gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy="automatic"

echo -n "sk-ant-..." | gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Grant access
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:oneflow@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Python Integration:**

```python
from google.cloud import secretmanager

class GCPSecretsManager:
    """API key manager using GCP Secret Manager."""
    
    def __init__(self, project_id: str):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id
    
    def get_secret(self, secret_id: str) -> str:
        """Get secret value from GCP."""
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
        
        try:
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode('UTF-8')
        except Exception as e:
            raise ValueError(f"Failed to retrieve secret {secret_id}: {e}")
    
    def get_api_keys(self) -> dict:
        """Get all API keys."""
        return {
            'openai': self.get_secret('openai-api-key'),
            'anthropic': self.get_secret('anthropic-api-key'),
            'stability': self.get_secret('stability-api-key'),
            'elevenlabs': self.get_secret('elevenlabs-api-key')
        }

# Usage
gcp_manager = GCPSecretsManager(project_id='your-project-id')
api_keys = gcp_manager.get_api_keys()
```

---

## 🔄 Automatic Key Rotation

### Vault Rotation Policy

```hcl
# rotation-policy.hcl
path "secret/data/oneflow/api-keys" {
  capabilities = ["create", "update"]
  
  # Rotate every 90 days
  allowed_parameters = {
    "rotation_period" = ["90d"]
  }
}
```

### AWS Rotation Lambda

```python
import boto3
import json

def lambda_handler(event, context):
    """Rotate API keys automatically."""
    
    secrets_client = boto3.client('secretsmanager')
    
    # Get current secret
    response = secrets_client.get_secret_value(
        SecretId='oneflow/api-keys'
    )
    current_keys = json.loads(response['SecretString'])
    
    # Rotate each key (implement provider-specific rotation)
    new_keys = rotate_all_keys(current_keys)
    
    # Update secret
    secrets_client.put_secret_value(
        SecretId='oneflow/api-keys',
        SecretString=json.dumps(new_keys)
    )
    
    return {
        'statusCode': 200,
        'body': 'Keys rotated successfully'
    }

def rotate_all_keys(current_keys: dict) -> dict:
    """Rotate all API keys with providers."""
    new_keys = {}
    
    for provider, old_key in current_keys.items():
        # Call provider API to generate new key
        new_keys[provider] = rotate_provider_key(provider, old_key)
    
    return new_keys
```

---

## 🔐 Updated OneFlow.AI Integration

### Modified KeyManager Class

```python
"""
Enhanced API Key Manager with production security.
"""

import os
from typing import Optional, Dict
from enum import Enum

class SecretBackend(Enum):
    """Secret management backend types."""
    FILE = "file"  # Development only
    ENV = "env"
    VAULT = "vault"
    AWS = "aws"
    GCP = "gcp"

class ProductionKeyManager:
    """Production-grade API key manager."""
    
    def __init__(self, backend: SecretBackend = SecretBackend.ENV):
        """
        Initialize key manager with specified backend.
        
        Args:
            backend: Secret management backend to use.
        """
        self.backend = backend
        self.keys = {}
        self._load_keys()
    
    def _load_keys(self):
        """Load keys from configured backend."""
        if self.backend == SecretBackend.ENV:
            self._load_from_env()
        elif self.backend == SecretBackend.VAULT:
            self._load_from_vault()
        elif self.backend == SecretBackend.AWS:
            self._load_from_aws()
        elif self.backend == SecretBackend.GCP:
            self._load_from_gcp()
        elif self.backend == SecretBackend.FILE:
            # Only for development!
            if os.getenv('ENVIRONMENT') == 'production':
                raise ValueError("FILE backend not allowed in production!")
            self._load_from_file()
    
    def _load_from_env(self):
        """Load from environment variables."""
        env_keys = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'stability': 'STABILITY_API_KEY',
            'elevenlabs': 'ELEVENLABS_API_KEY'
        }
        
        for provider, env_var in env_keys.items():
            key = os.getenv(env_var)
            if key:
                self.keys[provider] = key
    
    def _load_from_vault(self):
        """Load from HashiCorp Vault."""
        try:
            import hvac
            
            client = hvac.Client(
                url=os.getenv('VAULT_ADDR'),
                token=os.getenv('VAULT_TOKEN')
            )
            
            secret = client.secrets.kv.v2.read_secret_version(
                path='oneflow/api-keys',
                mount_point='secret'
            )
            
            self.keys = secret['data']['data']
            
        except ImportError:
            raise ValueError("hvac package required for Vault backend")
        except Exception as e:
            raise ValueError(f"Failed to load keys from Vault: {e}")
    
    def _load_from_aws(self):
        """Load from AWS Secrets Manager."""
        try:
            import boto3
            import json
            
            client = boto3.client('secretsmanager')
            response = client.get_secret_value(SecretId='oneflow/api-keys')
            
            self.keys = json.loads(response['SecretString'])
            
        except ImportError:
            raise ValueError("boto3 package required for AWS backend")
        except Exception as e:
            raise ValueError(f"Failed to load keys from AWS: {e}")
    
    def _load_from_gcp(self):
        """Load from GCP Secret Manager."""
        try:
            from google.cloud import secretmanager
            
            client = secretmanager.SecretManagerServiceClient()
            project_id = os.getenv('GCP_PROJECT_ID')
            
            for provider in ['openai', 'anthropic', 'stability', 'elevenlabs']:
                name = f"projects/{project_id}/secrets/{provider}-api-key/versions/latest"
                response = client.access_secret_version(request={"name": name})
                self.keys[provider] = response.payload.data.decode('UTF-8')
                
        except ImportError:
            raise ValueError("google-cloud-secret-manager package required")
        except Exception as e:
            raise ValueError(f"Failed to load keys from GCP: {e}")
    
    def _load_from_file(self):
        """Load from file (DEVELOPMENT ONLY)."""
        import json
        
        if not os.path.exists('.api_keys.json'):
            return
        
        with open('.api_keys.json', 'r') as f:
            self.keys = json.load(f)
    
    def get_key(self, provider: str) -> Optional[str]:
        """Get API key for provider."""
        return self.keys.get(provider.lower())
    
    def has_key(self, provider: str) -> bool:
        """Check if API key exists."""
        return provider.lower() in self.keys
```

### Usage in Application

```python
"""
Application startup with production security.
"""

import os
from production_key_manager import ProductionKeyManager, SecretBackend

# Determine backend from environment
def get_secret_backend() -> SecretBackend:
    """Determine which secret backend to use."""
    env = os.getenv('ENVIRONMENT', 'development')
    backend = os.getenv('SECRET_BACKEND', 'env')
    
    if env == 'production' and backend == 'file':
        raise ValueError("FILE backend not allowed in production!")
    
    return SecretBackend[backend.upper()]

# Initialize key manager
key_manager = ProductionKeyManager(backend=get_secret_backend())

# Validate all required keys present
required_providers = ['openai', 'anthropic']
missing = [p for p in required_providers if not key_manager.has_key(p)]

if missing:
    raise ValueError(f"Missing required API keys: {missing}")

print("✓ All API keys loaded securely")
```

---

## 📋 Security Checklist

### Development
- [ ] Use `.env` file with `.gitignore`
- [ ] Never commit `.api_keys.json`
- [ ] Use different keys for dev/staging/prod
- [ ] Set `chmod 600` on any local key files

### Staging
- [ ] Use environment variables minimum
- [ ] Consider Vault/AWS Secrets for testing
- [ ] Enable audit logging
- [ ] Test key rotation procedures

### Production
- [ ] ✅ **MUST** use Vault/AWS/GCP Secret Manager
- [ ] ❌ **NEVER** use file-based keys
- [ ] ✅ Enable automatic rotation (90 days max)
- [ ] ✅ Implement audit logging
- [ ] ✅ Use IAM/RBAC for access control
- [ ] ✅ Encrypt secrets at rest
- [ ] ✅ Monitor for unauthorized access
- [ ] ✅ Have incident response plan

---

## 🚨 Incident Response

### If API Key Compromised

1. **Immediate Actions** (within 5 minutes):
   ```bash
   # Revoke compromised key immediately
   vault kv metadata delete secret/oneflow/api-keys
   
   # Or via AWS
   aws secretsmanager delete-secret \
     --secret-id oneflow/api-keys \
     --force-delete-without-recovery
   
   # Disable key at provider
   # - OpenAI: https://platform.openai.com/api-keys
   # - Anthropic: https://console.anthropic.com/settings/keys
   ```

2. **Generate new keys** (within 15 minutes):
   ```bash
   # Create new keys at each provider
   # Update secret manager
   vault kv put secret/oneflow/api-keys \
     openai="sk-proj-NEW-KEY" \
     anthropic="sk-ant-NEW-KEY"
   ```

3. **Restart services** (within 30 minutes):
   ```bash
   kubectl rollout restart deployment/oneflow-api
   ```

4. **Post-incident**:
   - Review access logs
   - Identify breach source
   - Update security policies
   - Notify stakeholders

---

## 📊 Comparison Matrix

| Solution | Security | Ease | Cost | Rotation | Audit |
|----------|----------|------|------|----------|-------|
| **File (.api_keys.json)** | ❌ Low | ✅ Easy | Free | ❌ Manual | ❌ None |
| **Environment Variables** | ⚠️ Medium | ✅ Easy | Free | ⚠️ Manual | ❌ Limited |
| **HashiCorp Vault** | ✅ High | ⚠️ Moderate | Free/Paid | ✅ Auto | ✅ Full |
| **AWS Secrets Manager** | ✅ High | ✅ Easy | ~$0.40/secret/month | ✅ Auto | ✅ Full |
| **GCP Secret Manager** | ✅ High | ✅ Easy | ~$0.06/secret/month | ✅ Auto | ✅ Full |

---

## 🎯 Recommendation

**For Production:**
1. **Small Projects**: AWS/GCP Secret Manager (easiest)
2. **Multi-Cloud**: HashiCorp Vault (most flexible)
3. **Enterprise**: Vault + HSM (most secure)

**Migration Path:**
```
Development → Environment Variables → Secret Manager → Vault (optional)
```

---

## 📚 Additional Resources

- [OWASP Secret Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [GCP Secret Manager Guide](https://cloud.google.com/secret-manager/docs/best-practices)

---

**Remember: Security is NOT optional in production! 🔒**