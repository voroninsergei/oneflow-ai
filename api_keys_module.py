"""
API Keys management module for OneFlow.AI.
Модуль управления API ключами для OneFlow.AI.

This module handles secure storage and retrieval of API keys for different AI providers.
Этот модуль обеспечивает безопасное хранение и получение API ключей для различных AI провайдеров.
"""

import os
import json
from typing import Optional, Dict
from pathlib import Path


class APIKeyManager:
    """
    Manage API keys for AI providers.
    Управление API ключами для AI провайдеров.
    """
    
    def __init__(self, config_file: str = '.api_keys.json'):
        """
        Initialize API key manager.
        Инициализировать менеджер API ключей.
        
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
                    self.keys = json.load(f)
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
            provider: Provider name (openai, anthropic, stability, etc.).
        
        Returns:
            str or None: API key if found, None otherwise.
        """
        return self.keys.get(provider.lower())
    
    def set_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a provider.
        Установить API ключ для провайдера.
        
        Args:
            provider: Provider name.
            api_key: API key value.
        """
        self.keys[provider.lower()] = api_key
    
    def save_keys(self) -> None:
        """
        Save API keys to configuration file.
        Сохранить API ключи в файл конфигурации.
        
        Note: This file should be added to .gitignore!
        Примечание: Этот файл должен быть добавлен в .gitignore!
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.keys, f, indent=2)
            
            # Set file permissions to read/write for owner only
            os.chmod(self.config_file, 0o600)
            print(f"✓ API keys saved to {self.config_file}")
            print(f"⚠ Make sure {self.config_file} is in your .gitignore!")
        except Exception as e:
            print(f"✗ Error saving API keys: {e}")
    
    def has_key(self, provider: str) -> bool:
        """
        Check if API key exists for provider.
        Проверить наличие API ключа для провайдера.
        
        Args:
            provider: Provider name.
        
        Returns:
            bool: True if key exists, False otherwise.
        """
        return provider.lower() in self.keys and bool(self.keys[provider.lower()])
    
    def list_providers(self) -> list:
        """
        List all providers with configured API keys.
        Список всех провайдеров с настроенными API ключами.
        
        Returns:
            list: List of provider names.
        """
        return [provider for provider, key in self.keys.items() if key]
    
    def remove_key(self, provider: str) -> None:
        """
        Remove API key for a provider.
        Удалить API ключ провайдера.
        
        Args:
            provider: Provider name.
        """
        if provider.lower() in self.keys:
            del self.keys[provider.lower()]
    
    def get_masked_key(self, provider: str) -> str:
        """
        Get masked version of API key for display.
        Получить замаскированную версию API ключа для отображения.
        
        Args:
            provider: Provider name.
        
        Returns:
            str: Masked API key (e.g., "sk-...abc123").
        """
        key = self.get_key(provider)
        if not key:
            return "Not configured"
        
        if len(key) <= 8:
            return "***"
        
        return f"{key[:3]}...{key[-4:]}"


# Global instance
_key_manager = None


def get_key_manager(config_file: str = '.api_keys.json') -> APIKeyManager:
    """
    Get global API key manager instance.
    Получить глобальный экземпляр менеджера API ключей.
    
    Args:
        config_file: Path to configuration file.
    
    Returns:
        APIKeyManager: Global key manager instance.
    """
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager(config_file)
    return _key_manager
