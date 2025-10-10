# Changelog | История изменений

All notable changes to OneFlow.AI will be documented in this file.

Все значимые изменения OneFlow.AI будут документированы в этом файле.

---

## [2.0.0] - 2025-01-XX

### Added | Добавлено

#### New Modules | Новые модули

1. **Analytics Module** (`src/analytics.py`)
   - Comprehensive request tracking and logging
   - Provider usage statistics
   - Cost analysis and reporting
   - Recent request history
   - Summary report generation
   - Export to JSON functionality
   
   **Русский**: Модуль аналитики с отслеживанием запросов, статистикой провайдеров, анализом затрат и экспортом в JSON.

2. **Budget Management** (`src/budget.py`)
   - Period-based budget limits (daily, weekly, monthly, total)
   - Provider-specific budget controls
   - Automatic period reset functionality
   - Spending validation before requests
   - Budget summary reports
   
   **Русский**: Управление бюджетом с лимитами по периодам, контролем для каждого провайдера и автоматическим сбросом.

3. **Configuration System** (`src/config.py`)
   - Centralized configuration management
   - JSON file support for configuration
   - Default rate management
   - Budget and wallet configuration
   - Region settings (US/EU/RU)
   - Singleton pattern for global config
   
   **Русский**: Система конфигурации с поддержкой JSON, управлением тарифами и настройками регионов.

4. **Command Line Interface** (`src/cli.py`)
   - Full-featured CLI with argparse
   - Request, status, analytics, budget commands
   - Credit management commands
   - Configuration display
   - Export functionality
   - Verbose mode support
   
   **Русский**: Полнофункциональный CLI с командами для запросов, статуса, аналитики и экспорта.

#### Enhanced Features | Улучшенные функции

5. **Improved Main Application** (`src/main.py`)
   - `OneFlowAI` orchestrator class
   - Interactive mode with menu system
   - Demo mode with predefined scenarios
   - Integrated analytics and budget tracking
   - Better error handling and validation
   - Status reporting
   
   **Русский**: Улучшенное главное приложение с интерактивным режимом и демо-сценариями.

6. **Enhanced Pricing Calculator** (`src/pricing.py`)
   - Input validation (negative values)
   - Provider existence checking
   - Rate retrieval methods
   - Better error messages
   
   **Русский**: Улучшенный калькулятор с валидацией входных данных и проверкой провайдеров.

#### Testing | Тестирование

7. **Comprehensive Test Suite**
   - `tests/test_analytics.py` - 12 tests
   - `tests/test_budget.py` - 15 tests
   - `tests/test_config.py` - 16 tests
   - Updated existing tests with new scenarios
   - Edge case testing
   - Error condition testing
   
   **Русский**: Полный набор тестов с покрытием всех новых модулей.