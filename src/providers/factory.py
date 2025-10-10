"""
Feature flags для контроля функциональности
"""
from typing import Dict
import os
import json

class FeatureFlags:
    """Управление feature flags"""
    
    DEFAULT_FLAGS = {
        "openai_enabled": True,
        "anthropic_enabled": True,
        "stability_enabled": True,
        "elevenlabs_enabled": True,
        "rate_limiting_enabled": True,
        "cost_estimation_enabled": True,
        "fallback_enabled": True,
        "detailed_logging": False,
    }
    
    def __init__(self, config_path: str = ".feature_flags.json"):
        self.config_path = config_path
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, bool]:
        """Загрузка флагов из файла или переменных окружения"""
        flags = self.DEFAULT_FLAGS.copy()
        
        # Попытка загрузки из файла
        try:
            with open(self.config_path, 'r') as f:
                file_flags = json.load(f)
                flags.update(file_flags)
        except FileNotFoundError:
            pass
        
        # Переопределение из environment variables
        for key in flags:
            env_key = f"FF_{key.upper()}"
            if env_key in os.environ:
                flags[key] = os.environ[env_key].lower() == "true"
        
        return flags
    
    def is_enabled(self, flag_name: str) -> bool:
        """Проверка, включен ли флаг"""
        return self.flags.get(flag_name, False)
    
    def get_all(self) -> Dict[str, bool]:
        """Получение всех флагов"""
        return self.flags.copy()
