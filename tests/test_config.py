"""
Test module for the Config class in OneFlow.AI.

English:
This module contains unit tests for the Config class, verifying configuration
management, file I/O, and validation.

Русская версия:
Этот модуль содержит юниттесты для класса Config: проверяет управление конфигурацией,
операции с файлами и валидацию.
"""

import os
import sys
import pytest
import json
import tempfile

# Add src path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config, get_config, reset_config


def test_config_initialization():
    """Test configuration initialization with defaults.
    Тест инициализации конфигурации со значениями по умолчанию.
    """
    config = Config()
    assert config.get_rate('gpt') == 1.0
    assert config.get_rate('image') == 10.0
    assert config.wallet_balance == 100.0
    assert config.region == 'US'


def test_set_and_get_rate():
    """Test setting and getting provider rates.
    Тест установки и получения тарифов провайдеров.
    """
    config = Config()
    config.set_rate('gpt', 2.5)
    assert config.get_rate('gpt') == 2.5


def test_set_negative_rate_raises_error():
    """Test that negative rates raise ValueError.
    Тест, что отрицательные тарифы вызывают ValueError.
    """
    config = Config()
    with pytest.raises(ValueError):
        config.set_rate('gpt', -1.0)


def test_set_wallet_balance():
    """Test setting wallet balance.
    Тест установки баланса кошелька.
    """
    config = Config()
    config.set_wallet_balance(200.0)
    assert config.wallet_balance == 200.0


def test_set_negative_balance_raises_error():
    """Test that negative balance raises ValueError.
    Тест, что отрицательный баланс вызывает ValueError.
    """
    config = Config()
    with pytest.raises(ValueError):
        config.set_wallet_balance(-50.0)


def test_set_budget_limit():
    """Test setting budget limits.
    Тест установки лимитов бюджета.
    """
    config = Config()
    config.set_budget_limit('daily', 50.0)
    assert config.budget_limits['daily'] == 50.0


def test_set_invalid_period_raises_error():
    """Test that invalid period raises ValueError.
    Тест, что неверный период вызывает ValueError.
    """
    config = Config()
    with pytest.raises(ValueError):
        config.set_budget_limit('invalid', 50.0)


def test_set_provider_budget():
    """Test setting provider budgets.
    Тест установки бюджетов провайдеров.
    """
    config = Config()
    config.set_provider_budget('gpt', 100.0)
    assert config.provider_budgets['gpt'] == 100.0


def test_set_region():
    """Test setting service region.
    Тест установки региона обслуживания.
    """
    config = Config()
    config.set_region('EU')
    assert config.region == 'EU'


def test_set_invalid_region_raises_error():
    """Test that invalid region raises ValueError.
    Тест, что неверный регион вызывает ValueError.
    """
    config = Config()
    with pytest.raises(ValueError):
        config.set_region('INVALID')


def test_get_all_rates():
    """Test getting all provider rates.
    Тест получения всех тарифов провайдеров.
    """
    config = Config()
    rates = config.get_all_rates()
    assert 'gpt' in rates
    assert 'image' in rates
    assert rates['gpt'] == 1.0


def test_save_and_load_config():
    """Test saving and loading configuration from file.
    Тест сохранения и загрузки конфигурации из файла.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Create and save config
        config1 = Config()
        config1.set_rate('gpt', 2.5)
        config1.set_wallet_balance(150.0)
        config1.set_region('EU')
        config1.save_to_file(temp_file)
        
        # Load config in new instance
        config2 = Config(temp_file)
        assert config2.get_rate('gpt') == 2.5
        assert config2.wallet_balance == 150.0
        assert config2.region == 'EU'
    
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_load_invalid_json_raises_error():
    """Test that invalid JSON raises ValueError.
    Тест, что неверный JSON вызывает ValueError.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write("invalid json {")
        temp_file = f.name
    
    try:
        config = Config()
        with pytest.raises(ValueError):
            config.load_from_file(temp_file)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_to_dict():
    """Test exporting configuration to dictionary.
    Тест экспорта конфигурации в словарь.
    """
    config = Config()
    config.set_rate('gpt', 2.0)
    config_dict = config.to_dict()
    
    assert 'rates' in config_dict
    assert 'wallet_balance' in config_dict
    assert 'region' in config_dict
    assert config_dict['rates']['gpt'] == 2.0


def test_global_config_singleton():
    """Test global configuration singleton pattern.
    Тест паттерна синглтон для глобальной конфигурации.
    """
    reset_config()
    
    config1 = get_config()
    config2 = get_config()
    
    assert config1 is config2
    
    config1.set_rate('gpt', 3.0)
    assert config2.get_rate('gpt') == 3.0
    
    reset_config()


def test_config_summary():
    """Test configuration summary generation.
    Тест генерации сводки конфигурации.
    """
    config = Config()
    summary = config.get_config_summary()
    
    assert 'OneFlow.AI Configuration' in summary
    assert 'gpt' in summary
    assert 'US' in summary


def test_load_partial_config():
    """Test loading partial configuration (not all fields present).
    Тест загрузки частичной конфигурации (не все поля присутствуют).
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({'rates': {'gpt': 5.0}, 'region': 'RU'}, f)
        temp_file = f.name
    
    try:
        config = Config(temp_file)
        assert config.get_rate('gpt') == 5.0
        assert config.region == 'RU'
        # Default values should still be present
        assert config.get_rate('image') == 10.0
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_none_budget_limit():
    """Test setting budget limit to None (no limit).
    Тест установки лимита бюджета в None (без лимита).
    """
    config = Config()
    config.set_budget_limit('daily', None)
    assert config.budget_limits['daily'] is None


def test_unknown_provider_rate():
    """Test getting rate for unknown provider.
    Тест получения тарифа для неизвестного провайдера.
    """
    config = Config()
    assert config.get_rate('unknown_provider') == 0.0
