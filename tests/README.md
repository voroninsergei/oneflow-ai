# OneFlow.AI Testing Guide

## Структура тестов / Test Structure

```
tests/
├── unit/                      # Unit tests (fast, isolated)
│   ├── conftest.py           # Unit test fixtures
│   ├── test_routing.py       # Router unit tests
│   ├── test_budget_pricing.py # Budget & pricing tests
│   ├── test_providers_mock.py # Provider tests with mocks
│   ├── test_analytics.py     # Analytics tests
│   ├── test_auth.py          # Authentication tests
│   ├── test_config.py        # Configuration tests
│   ├── test_database.py      # Database tests
│   └── test_wallet.py        # Wallet tests
│
├── e2e/                       # End-to-end tests (integrated)
│   ├── conftest.py           # E2E test fixtures
│   ├── test_complete_flow.py # Complete workflow tests
│   └── test_api_integration.py # API integration tests
│
├── integration/              # Integration tests
│   └── (future integration tests)
│
├── conftest.py              # Global fixtures
└── README.md                # This file
```

## Запуск тестов / Running Tests

### Основные команды / Basic Commands

```bash
# Run all tests with default settings
make test

# Run only unit tests (fast)
make test-unit

# Run only E2E tests
make test-e2e

# Run with coverage
make test-coverage
```

### Тесты по категориям / Tests by Category

```bash
# Provider tests
make test-providers
pytest -m providers

# Budget and pricing tests
make test-budget
pytest -m budget

# Routing tests
make test-routing
pytest -m routing

# Authentication tests
make test-auth
pytest -m auth

# Database tests
make test-db
pytest -m db
```

### Расширенные опции / Advanced Options

```bash
# Run fast tests only
make test-fast
pytest -m "not slow"

# Run slow tests only
make test-slow
pytest -m slow

# Parallel execution
make test-parallel
pytest -n auto

# Verbose output
make test-verbose
pytest -vv

# Stop on first failure
pytest -x

# Run specific test file
make test-file FILE=tests/unit/test_routing.py

# Run specific test function
pytest tests/unit/test_routing.py::TestRouterUnit::test_router_initialization -v
```

## Маркеры тестов / Test Markers

Тесты помечены следующими маркерами:

- `@pytest.mark.unit` - Unit tests (isolated, fast)
- `@pytest.mark.e2e` - End-to-end tests (integrated)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.providers` - Provider-specific tests
- `@pytest.mark.routing` - Router tests
- `@pytest.mark.budget` - Budget/pricing tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.db` - Database tests
- `@pytest.mark.api` - API endpoint tests

## Фикстуры / Fixtures

### Unit Test Fixtures

- `mock_gpt_provider` - Mocked GPT provider
- `mock_image_provider` - Mocked Image provider
- `mock_audio_provider` - Mocked Audio provider
- `mock_video_provider` - Mocked Video provider
- `mock_all_providers` - Dictionary of all mocked providers
- `mock_wallet` - Mocked wallet
- `mock_analytics` - Mocked analytics
- `mock_budget` - Mocked budget
- `temp_config_file` - Temporary config file
- `temp_db_file` - Temporary database file

### E2E Test Fixtures

- `full_system_setup` - Complete system with all components
- `system_with_db` - System with database integration
- `realistic_config` - Realistic production-like configuration
- `request_factory` - Factory for creating test requests
- `batch_requests` - Batch of test requests
- `stress_test_requests` - Large batch for stress testing

## HTTP Моки / HTTP Mocking

Тесты используют библиотеки для мокирования HTTP запросов:

### Responses (для requests)

```python
@responses.activate
def test_api_call():
    responses.add(
        responses.POST,
        "https://api.example.com/endpoint",
        json={"result": "success"},
        status=200
    )
    # Your test code
```

### RESPX (для httpx/async)

```python
@pytest.mark.asyncio
async def test_async_api():
    import respx
    with respx.mock:
        respx.post("https://api.example.com").mock(
            return_value=httpx.Response(200, json={"result": "success"})
        )
        # Your async test code
```

## Покрытие кода / Code Coverage

```bash
# Generate coverage report
make test-coverage

# View HTML report
open htmlcov/index.html

# View terminal report
pytest --cov=src --cov-report=term-missing
```

Цель покрытия: **>80%** для критичных модулей

## Стратегии тестирования / Testing Strategies

### Unit Tests
- Тестируют отдельные компоненты изолированно
- Используют моки для внешних зависимостей
- Быстрые (< 1s каждый)
- Не требуют внешних сервисов

### E2E Tests
- Тестируют полные рабочие процессы
- Интегрируют несколько компонентов
- Могут быть медленнее
- Проверяют реальные сценарии использования

### Integration Tests
- Тестируют взаимодействие между компонентами
- Могут использовать реальные базы данных (временные)
- Проверяют интеграцию с внешними API

## Best Practices

### Именование тестов

```python
def test_<component>_<scenario>_<expected_result>():
    """
    Test that <component> <does something> when <scenario>
    """
```

### Структура теста (AAA Pattern)

```python
def test_example():
    # Arrange - подготовка данных
    wallet = Wallet(initial_balance=100.0)
    
    # Act - выполнение действия
    wallet.deduct(30.0)
    
    # Assert - проверка результата
    assert wallet.get_balance() == 70.0
```

### Использование фикстур

```python
@pytest.fixture
def setup_system():
    # Setup
    system = create_system()
    yield system
    # Teardown
    cleanup(system)

def test_with_fixture(setup_system):
    # Use setup_system
    assert setup_system.is_ready()
```

## CI/CD Integration

Для CI/CD используйте:

```bash
# Strict mode for CI
make test-ci

# Or directly
pytest -q --maxfail=1 --strict-markers --disable-warnings --tb=short
```

## Отладка тестов / Debugging Tests

```bash
# Run with pdb debugger
pytest --pdb

# Drop into debugger on failure
pytest --pdb -x

# Show local variables on failure
pytest -l

# Verbose traceback
pytest --tb=long

# Show print statements
pytest -s
```

## Профилирование / Profiling

```bash
# Profile test execution
pytest --profile

# Profile with visualization
pytest --profile --profile-svg

# Show slowest tests
pytest --durations=10
```

## Проблемы и решения / Troubleshooting

### Tests running slowly
- Используйте `pytest -n auto` для параллельного выполнения
- Проверьте медленные тесты с `pytest --durations=10`
- Рассмотрите use of test doubles/mocks

### Import errors
- Проверьте `sys.path.insert(0, ...)` в conftest.py
- Убедитесь что `__init__.py` файлы существуют
- Запускайте из корня проекта

### Fixture not found
- Проверьте что conftest.py в правильной директории
- Используйте `pytest --fixtures` для просмотра доступных фикстур

### Mock not working
- Убедитесь что mock создан до вызова тестируемого кода
- Проверьте правильность path в `patch()`
- Используйте `return_value` для простых моков

## Установка зависимостей / Installing Dependencies

```bash
# Install all dev dependencies
make install-dev

# Or manually
pip install -r requirements-dev.txt

# Install test dependencies only
make install-test
```

## Качество тестов / Test Quality

```bash
# Check test code quality
make test-lint

# Run mutation testing
make test-mutation

# Full quality check
make test-quality
```

## Дополнительные ресурсы / Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [responses documentation](https://github.com/getsentry/responses)
- [respx documentation](https://lundberg.github.io/respx/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Вклад в тесты / Contributing Tests

При добавлении нового функционала:

1. Добавьте unit тесты для новых компонентов
2. Добавьте E2E тесты для новых workflows
3. Обновите документацию
4. Убедитесь что покрытие не снизилось
5. Запустите `make test-all` перед коммитом

## Контакты / Contacts

Вопросы по тестированию? Создайте issue в репозитории.
