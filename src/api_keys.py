"""
API Keys Management Module for OneFlow.AI
Модуль управления API ключами для OneFlow.AI

This module provides secure management of API keys for various AI providers.
Этот модуль предоставляет безопасное управление API ключами для различных AI провайдеров.
"""

import os
import json
from typing import Optional, Dict, List


class KeyManager:
    """
    Manage API keys from file and environment variables.
    Управление API ключами из файла и переменных окружения.
    """
    
    def __init__(self, config_file: str = '.api_keys.json'):
        """
        Initialize key manager.
        Инициализация менеджера ключей.
        
        Args:
            config_file: Path to API keys configuration file.
        """
        self.config_file = config_file
        self.keys: Dict[str, str] = {}
        self._load_keys()
    
    def _load_keys(self) -> None:
        """
        Load API keys from file or environment variables.
        Загрузить API ключи из файла или переменных окружения.
        """
        # Try to load from file first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_data = json.load(f)
                    # Handle both flat and nested structures
                    for provider, value in file_data.items():
                        if isinstance(value, dict) and 'api_key' in value:
                            self.keys[provider] = value['api_key']
                        elif isinstance(value, str):
                            self.keys[provider] = value
            except Exception as e:
                print(f"Warning: Could not load API keys from file: {e}")
        
        # Override with environment variables if present
        env_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'stability': os.getenv('STABILITY_API_KEY'),
            'elevenlabs': os.getenv('ELEVENLABS_API_KEY'),
            'runway': os.getenv('RUNWAY_API_KEY'),
        }
        
        for provider, key in env_keys.items():
            if key:
                self.keys[provider] = key
    
    def get_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider.
        Получить API ключ для провайдера.
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic').
        
        Returns:
            str: API key or None if not found.
        """
        return self.keys.get(provider.lower())
    
    def has_key(self, provider: str) -> bool:
        """
        Check if API key exists for a provider.
        Проверить существует ли API ключ для провайдера.
        
        Args:
            provider: Provider name.
        
        Returns:
            bool: True if key exists and is not empty.
        """
        key = self.keys.get(provider.lower())
        return key is not None and len(key.strip()) > 0
    
    def set_key(self, provider: str, key: str) -> None:
        """
        Set API key for a provider.
        Установить API ключ для провайдера.
        
        Args:
            provider: Provider name.
            key: API key value.
        """
        self.keys[provider.lower()] = key
    
    def remove_key(self, provider: str) -> bool:
        """
        Remove API key for a provider.
        Удалить API ключ для провайдера.
        
        Args:
            provider: Provider name.
        
        Returns:
            bool: True if key was removed, False if not found.
        """
        provider_lower = provider.lower()
        if provider_lower in self.keys:
            del self.keys[provider_lower]
            return True
        return False
    
    def list_providers(self) -> List[str]:
        """
        Get list of providers with configured keys.
        Получить список провайдеров с настроенными ключами.
        
        Returns:
            list: List of provider names.
        """
        return list(self.keys.keys())
    
    def get_masked_key(self, provider: str) -> str:
        """
        Get masked API key for display purposes.
        Получить замаскированный API ключ для отображения.
        
        Args:
            provider: Provider name.
        
        Returns:
            str: Masked key (e.g., 'sk-...abc1') or 'Not configured'.
        """
        key = self.get_key(provider)
        if not key:
            return "Not configured"
        
        if len(key) <= 8:
            return key[:2] + "..." + key[-1:]
        else:
            return key[:3] + "..." + key[-4:]
    
    def save_to_file(self, filepath: Optional[str] = None) -> None:
        """
        Save API keys to JSON file.
        Сохранить API ключи в JSON файл.
        
        Args:
            filepath: Path to save file (uses default if None).
        """
        if filepath is None:
            filepath = self.config_file
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.keys, f, indent=2)
            
            # Set restrictive permissions (Unix-like systems)
            try:
                os.chmod(filepath, 0o600)
            except:
                pass
        except Exception as e:
            print(f"Error saving API keys: {e}")
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load API keys from a specific file.
        Загрузить API ключи из определённого файла.
        
        Args:
            filepath: Path to load file.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"API keys file not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                file_data = json.load(f)
                
            for provider, value in file_data.items():
                if isinstance(value, dict) and 'api_key' in value:
                    self.keys[provider.lower()] = value['api_key']
                elif isinstance(value, str):
                    self.keys[provider.lower()] = value
        except Exception as e:
            raise ValueError(f"Error loading API keys from file: {e}")
    
    def validate_key_format(self, provider: str, key: str) -> tuple[bool, Optional[str]]:
        """
        Validate API key format for a provider.
        Проверить формат API ключа для провайдера.
        
        Args:
            provider: Provider name.
            key: API key to validate.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not key or len(key.strip()) == 0:
            return False, "API key cannot be empty"
        
        provider_lower = provider.lower()
        
        # Provider-specific validation
        if provider_lower == 'openai':
            if not key.startswith('sk-'):
                return False, "OpenAI key must start with 'sk-'"
            if len(key) < 20:
                return False, "OpenAI key is too short"
        
        elif provider_lower == 'anthropic':
            if not key.startswith('sk-ant-'):
                return False, "Anthropic key must start with 'sk-ant-'"
            if len(key) < 20:
                return False, "Anthropic key is too short"
        
        elif provider_lower == 'stability':
            if not key.startswith('sk-'):
                return False, "Stability AI key must start with 'sk-'"
        
        elif provider_lower == 'elevenlabs':
            if len(key) != 32:
                return False, "ElevenLabs key should be 32 characters"
        
        return True, None
    
    def get_configuration_summary(self) -> str:
        """
        Get formatted summary of API key configuration.
        Получить форматированную сводку конфигурации API ключей.
        
        Returns:
            str: Formatted summary.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("API Keys Configuration | Конфигурация API ключей")
        lines.append("=" * 60)
        
        all_providers = ['openai', 'anthropic', 'stability', 'elevenlabs', 'runway']
        
        for provider in all_providers:
            status = "✓ Configured" if self.has_key(provider) else "✗ Not configured"
            masked = self.get_masked_key(provider)
            lines.append(f"\n{provider.capitalize()}:")
            lines.append(f"  Status: {status}")
            lines.append(f"  Key: {masked}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def get_available_providers_by_type(self, content_type: str) -> List[str]:
        """
        Get available providers for a specific content type.
        Получить доступных провайдеров для конкретного типа контента.
        
        Args:
            content_type: Type of content ('text', 'image', 'audio', 'video').
        
        Returns:
            list: List of available provider names.
        """
        type_providers = {
            'text': ['openai', 'anthropic'],
            'image': ['stability', 'openai'],
            'audio': ['elevenlabs'],
            'video': ['runway']
        }
        
        available = []
        for provider in type_providers.get(content_type, []):
            if self.has_key(provider):
                available.append(provider)
        
        return available


# Global instance
_key_manager: Optional[KeyManager] = None


def get_key_manager(config_file: str = '.api_keys.json') -> KeyManager:
    """
    Get global key manager instance (singleton).
    Получить глобальный экземпляр менеджера ключей (синглтон).
    
    Args:
        config_file: Path to API keys configuration file.
    
    Returns:
        KeyManager: Global key manager instance.
    """
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager(config_file)
    return _key_manager


def reset_key_manager():
    """
    Reset global key manager instance.
    Сбросить глобальный экземпляр менеджера ключей.
    """
    global _key_manager
    _key_manager = None


# Demo
if __name__ == '__main__':
    print("=" * 60)
    print("API Keys Manager - Demo")
    print("=" * 60)
    
    km = get_key_manager()
    
    print("\n" + km.get_configuration_summary())
    
    # Show available providers by type
    print("\nAvailable providers by content type:")
    for content_type in ['text', 'image', 'audio', 'video']:
        providers = km.get_available_providers_by_type(content_type)
        print(f"  {content_type}: {providers if providers else 'None'}")
    
    print("\n" + "=" * 60)
