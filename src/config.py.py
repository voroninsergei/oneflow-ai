"""
Безопасная конфигурация для OneFlow.AI
Поддерживает несколько способов хранения секретов:
1. Переменные окружения (.env файл)
2. AWS Secrets Manager
3. HashiCorp Vault
4. Google Cloud Secret Manager
5. Azure Key Vault
6. Kubernetes Secrets
"""

import os
import json
import logging
from typing import Dict, Optional
from enum import Enum

# Опциональные импорты для различных secret managers
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    import hvac
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

try:
    from google.cloud import secretmanager
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


logger = logging.getLogger(__name__)


class SecretSource(Enum):
    """Источники для загрузки секретов"""
    ENV = "env"
    AWS = "aws"
    VAULT = "vault"
    GCP = "gcp"
    AZURE = "azure"
    K8S = "k8s"


class ConfigError(Exception):
    """Ошибка конфигурации"""
    pass


class SecretManager:
    """Менеджер для работы с различными источниками секретов"""
    
    def __init__(self, source: SecretSource = SecretSource.ENV):
        self.source = source
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Проверка доступности необходимых библиотек"""
        if self.source == SecretSource.ENV and not DOTENV_AVAILABLE:
            logger.warning("python-dotenv не установлен. Используются только системные переменные окружения.")
        elif self.source == SecretSource.AWS and not AWS_AVAILABLE:
            raise ConfigError("boto3 не установлен. Установите: pip install boto3")
        elif self.source == SecretSource.VAULT and not VAULT_AVAILABLE:
            raise ConfigError("hvac не установлен. Установите: pip install hvac")
        elif self.source == SecretSource.GCP and not GCP_AVAILABLE:
            raise ConfigError("google-cloud-secret-manager не установлен. Установите: pip install google-cloud-secret-manager")
        elif self.source == SecretSource.AZURE and not AZURE_AVAILABLE:
            raise ConfigError("azure-keyvault-secrets не установлен. Установите: pip install azure-keyvault-secrets azure-identity")
    
    def load_secrets(self) -> Dict[str, str]:
        """Загрузка секретов из выбранного источника"""
        if self.source == SecretSource.ENV:
            return self._load_from_env()
        elif self.source == SecretSource.AWS:
            return self._load_from_aws()
        elif self.source == SecretSource.VAULT:
            return self._load_from_vault()
        elif self.source == SecretSource.GCP:
            return self._load_from_gcp()
        elif self.source == SecretSource.AZURE:
            return self._load_from_azure()
        elif self.source == SecretSource.K8S:
            return self._load_from_k8s()
        else:
            raise ConfigError(f"Неподдерживаемый источник секретов: {self.source}")
    
    def _load_from_env(self) -> Dict[str, str]:
        """Загрузка из переменных окружения"""
        if DOTENV_AVAILABLE:
            load_dotenv()
            logger.info("Загружен .env файл")
        
        return {
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', ''),
            'stability_api_key': os.getenv('STABILITY_API_KEY', ''),
            'elevenlabs_api_key': os.getenv('ELEVENLABS_API_KEY', ''),
        }
    
    def _load_from_aws(self) -> Dict[str, str]:
        """Загрузка из AWS Secrets Manager"""
        secret_name = os.getenv('AWS_SECRET_NAME', 'oneflow-ai/api-keys')
        region_name = os.getenv('AWS_REGION', 'us-east-1')
        
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        try:
            response = client.get_secret_value(SecretId=secret_name)
            secrets = json.loads(response['SecretString'])
            logger.info(f"Секреты загружены из AWS Secrets Manager: {secret_name}")
            return secrets
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise ConfigError(f"Секрет не найден: {secret_name}")
            elif error_code == 'InvalidRequestException':
                raise ConfigError(f"Неверный запрос к AWS Secrets Manager")
            elif error_code == 'InvalidParameterException':
                raise ConfigError(f"Неверный параметр запроса")
            else:
                raise ConfigError(f"Ошибка AWS Secrets Manager: {e}")
    
    def _load_from_vault(self) -> Dict[str, str]:
        """Загрузка из HashiCorp Vault"""
        vault_addr = os.getenv('VAULT_ADDR')
        vault_token = os.getenv('VAULT_TOKEN')
        vault_path = os.getenv('VAULT_SECRET_PATH', 'secret/oneflow-ai/api-keys')
        
        if not vault_addr or not vault_token:
            raise ConfigError("VAULT_ADDR и VAULT_TOKEN должны быть установлены")
        
        client = hvac.Client(url=vault_addr, token=vault_token)
        
        if not client.is_authenticated():
            raise ConfigError("Не удалось аутентифицироваться в Vault")
        
        try:
            # Для KV v2
            secret = client.secrets.kv.v2.read_secret_version(path=vault_path)
            secrets = secret['data']['data']
            logger.info(f"Секреты загружены из Vault: {vault_path}")
            return secrets
        except Exception as e:
            raise ConfigError(f"Ошибка загрузки из Vault: {e}")
    
    def _load_from_gcp(self) -> Dict[str, str]:
        """Загрузка из Google Cloud Secret Manager"""
        project_id = os.getenv('GCP_PROJECT_ID')
        
        if not project_id:
            raise ConfigError("GCP_PROJECT_ID должен быть установлен")
        
        client = secretmanager.SecretManagerServiceClient()
        secrets = {}
        
        secret_ids = {
            'openai_api_key': os.getenv('GCP_OPENAI_SECRET_ID', 'openai-api-key'),
            'anthropic_api_key': os.getenv('GCP_ANTHROPIC_SECRET_ID', 'anthropic-api-key'),
            'stability_api_key': os.getenv('GCP_STABILITY_SECRET_ID', 'stability-api-key'),
            'elevenlabs_api_key': os.getenv('GCP_ELEVENLABS_SECRET_ID', 'elevenlabs-api-key'),
        }
        
        for key, secret_id in secret_ids.items():
            try:
                name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                secrets[key] = response.payload.data.decode('UTF-8')
            except Exception as e:
                logger.warning(f"Не удалось загрузить {secret_id}: {e}")
                secrets[key] = ''
        
        logger.info(f"Секреты загружены из GCP Secret Manager")
        return secrets
    
    def _load_from_azure(self) -> Dict[str, str]:
        """Загрузка из Azure Key Vault"""
        vault_url = os.getenv('AZURE_VAULT_URL')
        
        if not vault_url:
            raise ConfigError("AZURE_VAULT_URL должен быть установлен")
        
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        
        secrets = {}
        secret_names = {
            'openai_api_key': 'openai-api-key',
            'anthropic_api_key': 'anthropic-api-key',
            'stability_api_key': 'stability-api-key',
            'elevenlabs_api_key': 'elevenlabs-api-key',
        }
        
        for key, secret_name in secret_names.items():
            try:
                secret = client.get_secret(secret_name)
                secrets[key] = secret.value
            except Exception as e:
                logger.warning(f"Не удалось загрузить {secret_name}: {e}")
                secrets[key] = ''
        
        logger.info(f"Секреты загружены из Azure Key Vault")
        return secrets
    
    def _load_from_k8s(self) -> Dict[str, str]:
        """Загрузка из Kubernetes Secrets (монтированных как файлы)"""
        secret_path = os.getenv('K8S_SECRET_PATH', '/run/secrets')
        
        secrets = {}
        secret_files = {
            'openai_api_key': 'openai-key',
            'anthropic_api_key': 'anthropic-key',
            'stability_api_key': 'stability-key',
            'elevenlabs_api_key': 'elevenlabs-key',
        }
        
        for key, filename in secret_files.items():
            filepath = os.path.join(secret_path, filename)
            try:
                with open(filepath, 'r') as f:
                    secrets[key] = f.read().strip()
            except FileNotFoundError:
                logger.warning(f"Секрет не найден: {filepath}")
                secrets[key] = ''
        
        logger.info(f"Секреты загружены из Kubernetes Secrets")
        return secrets


class Config:
    """Главный класс конфигурации OneFlow.AI"""
    
    def __init__(self, secret_source: Optional[SecretSource] = None):
        """
        Инициализация конфигурации
        
        Args:
            secret_source: Источник секретов. Если None, определяется автоматически
        """
        if secret_source is None:
            secret_source = self._detect_source()
        
        self.secret_manager = SecretManager(secret_source)
        self._secrets = self.secret_manager.load_secrets()
        
        # API ключи
        self.OPENAI_API_KEY = self._secrets.get('openai_api_key', '')
        self.ANTHROPIC_API_KEY = self._secrets.get('anthropic_api_key', '')
        self.STABILITY_API_KEY = self._secrets.get('stability_api_key', '')
        self.ELEVENLABS_API_KEY = self._secrets.get('elevenlabs_api_key', '')
        
        # Другие настройки из переменных окружения
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///oneflow.db')
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        self.PORT = int(os.getenv('PORT', '8000'))
        self.HOST = os.getenv('HOST', '0.0.0.0')
        
        # Настройки безопасности
        self.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', self._generate_secret_key())
        self.JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    def _detect_source(self) -> SecretSource:
        """Автоматическое определение источника секретов"""
        if os.getenv('AWS_SECRET_NAME'):
            return SecretSource.AWS
        elif os.getenv('VAULT_ADDR'):
            return SecretSource.VAULT
        elif os.getenv('GCP_PROJECT_ID'):
            return SecretSource.GCP
        elif os.getenv('AZURE_VAULT_URL'):
            return SecretSource.AZURE
        elif os.path.exists('/run/secrets'):
            return SecretSource.K8S
        else:
            return SecretSource.ENV
    
    def _generate_secret_key(self) -> str:
        """Генерация случайного секретного ключа"""
        import secrets
        logger.warning("JWT_SECRET_KEY не установлен! Генерируется временный ключ.")
        return secrets.token_urlsafe(32)
    
    def validate(self, strict: bool = False):
        """
        Валидация конфигурации
        
        Args:
            strict: Если True, выбрасывает исключение при отсутствии любого ключа
                   Если False, только предупреждает
        """
        required_keys = {
            'OPENAI_API_KEY': self.OPENAI_API_KEY,
            'ANTHROPIC_API_KEY': self.ANTHROPIC_API_KEY,
        }
        
        optional_keys = {
            'STABILITY_API_KEY': self.STABILITY_API_KEY,
            'ELEVENLABS_API_KEY': self.ELEVENLABS_API_KEY,
        }
        
        missing_required = [k for k, v in required_keys.items() if not v]
        missing_optional = [k for k, v in optional_keys.items() if not v]
        
        if missing_required:
            error_msg = f"Отсутствуют обязательные API ключи: {', '.join(missing_required)}"
            if strict:
                raise ConfigError(error_msg)
            else:
                logger.warning(error_msg)
        
        if missing_optional:
            logger.info(f"Отсутствуют опциональные API ключи: {', '.join(missing_optional)}")
        
        logger.info("Конфигурация успешно загружена и проверена")
    
    def get_provider_key(self, provider: str) -> str:
        """Получение ключа для конкретного провайдера"""
        provider_map = {
            'openai': self.OPENAI_API_KEY,
            'gpt': self.OPENAI_API_KEY,
            'anthropic': self.ANTHROPIC_API_KEY,
            'claude': self.ANTHROPIC_API_KEY,
            'stability': self.STABILITY_API_KEY,
            'elevenlabs': self.ELEVENLABS_API_KEY,
        }
        
        key = provider_map.get(provider.lower(), '')
        if not key:
            raise ConfigError(f"API ключ для провайдера '{provider}' не найден")
        return key
    
    def mask_secrets(self) -> Dict[str, str]:
        """Возвращает конфигурацию с замаскированными секретами для логирования"""
        def mask(value: str) -> str:
            if not value or len(value) < 8:
                return '***'
            return f"{value[:4]}...{value[-4:]}"
        
        return {
            'OPENAI_API_KEY': mask(self.OPENAI_API_KEY),
            'ANTHROPIC_API_KEY': mask(self.ANTHROPIC_API_KEY),
            'STABILITY_API_KEY': mask(self.STABILITY_API_KEY),
            'ELEVENLABS_API_KEY': mask(self.ELEVENLABS_API_KEY),
            'DATABASE_URL': self.DATABASE_URL,
            'LOG_LEVEL': self.LOG_LEVEL,
            'DEBUG': self.DEBUG,
            'SECRET_SOURCE': self.secret_manager.source.value,
        }


# Глобальный экземпляр конфигурации
_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """
    Получение глобального экземпляра конфигурации (singleton)
    
    Args:
        reload: Если True, перезагружает конфигурацию
    """
    global _config
    if _config is None or reload:
        _config = Config()
    return _config


# Для обратной совместимости со старым кодом
def load_api_keys() -> Dict[str, str]:
    """
    DEPRECATED: Используйте get_config() вместо этого
    Загрузка API ключей (для обратной совместимости)
    """
    logger.warning("load_api_keys() устарела. Используйте get_config()")
    config = get_config()
    return {
        'openai': config.OPENAI_API_KEY,
        'anthropic': config.ANTHROPIC_API_KEY,
        'stability': config.STABILITY_API_KEY,
        'elevenlabs': config.ELEVENLABS_API_KEY,
    }


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO)
    
    # Автоматическое определение источника
    config = Config()
    config.validate()
    
    print("\n=== Конфигурация OneFlow.AI ===")
    print(json.dumps(config.mask_secrets(), indent=2))
    print("\n=== Тест получения ключа провайдера ===")
    try:
        print(f"OpenAI key: {config.get_provider_key('openai')[:10]}...")
    except ConfigError as e:
        print(f"Ошибка: {e}")
