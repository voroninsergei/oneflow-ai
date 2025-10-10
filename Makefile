# Makefile for OneFlow.AI
# Автоматизация команд для OneFlow.AI

.PHONY: help install test test-verbose test-coverage clean lint format run demo docs

# Default target
help:
	@echo "OneFlow.AI - Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make test           - Run tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code with black"
	@echo "  make run            - Run interactive mode"
	@echo "  make demo           - Run demo mode"
	@echo "  make clean          - Clean temporary files"
	@echo "  make docs           - Generate documentation"
	@echo ""
	@echo "Русский:"
	@echo "  make install        - Установить зависимости"
	@echo "  make test           - Запустить тесты"
	@echo "  make test-verbose   - Запустить тесты с подробным выводом"
	@echo "  make test-coverage  - Запустить тесты с отчётом о покрытии"
	@echo "  make lint           - Проверить код"
	@echo "  make format         - Форматировать код"
	@echo "  make run            - Запустить интерактивный режим"
	@echo "  make demo           - Запустить демо-режим"
	@echo "  make clean          - Очистить временные файлы"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Run all tests
test:
	@echo "Running tests..."
	pytest -q
	@echo "✓ Tests completed"

# Run tests with verbose output
test-verbose:
	@echo "Running tests (verbose)..."
	pytest -v
	@echo "✓ Tests completed"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	pytest --cov=src --cov-report=html --cov-report=term tests/
	@echo "✓ Coverage report generated in htmlcov/"

# Run specific test file
test-pricing:
	pytest tests/test_pricing.py -v

test-providers:
	pytest tests/test_providers.py -v

test-router:
	pytest tests/test_router.py -v

test-wallet:
	pytest tests/test_wallet.py -v

test-analytics:
	pytest tests/test_analytics.py -v

test-budget:
	pytest tests/test_budget.py -v

test-config:
	pytest tests/test_config.py -v

# Code quality
lint:
	@echo "Running linter..."
	flake8 src/ tests/ --max-line-length=120 --ignore=E501,W503
	@echo "✓ Linting completed"

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/ --line-length=120
	@echo "✓ Code formatted"

# Type checking
typecheck:
	@echo "Running type checker..."
	mypy src/ --ignore-missing-imports
	@echo "✓ Type checking completed"

# Run interactive mode
run:
	@echo "Starting OneFlow.AI interactive mode..."
	python -m src.main

# Run demo mode
demo:
	@echo "Starting OneFlow.AI demo mode..."
	python -m src.main --demo

# CLI commands
cli-status:
	python -m src.cli status

cli-analytics:
	python -m src.cli analytics

cli-budget:
	python -m src.cli budget

cli-config:
	python -m src.cli config

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	pip install pytest-cov black flake8 mypy
	@echo "✓ Development environment ready"

# Build package
build:
	@echo "Building package..."
	python setup.py sdist bdist_wheel
	@echo "✓ Package built in dist/"

# Install package in development mode
dev-install:
	@echo "Installing package in development mode..."
	pip install -e .
	@echo "✓ Package installed in development mode"

# Run all quality checks
quality: lint typecheck test
	@echo "✓ All quality checks passed"

# Quick test (no coverage)
quicktest:
	pytest -q --tb=short

# Generate test report
test-report:
	pytest --html=test-report.html --self-contained-html
	@echo "✓ Test report generated: test-report.html"

# Help in Russian
help-ru:
	@echo "OneFlow.AI - Доступные команды:"
	@echo "  make install        - Установить зависимости"
	@echo "  make test           - Запустить тесты"
	@echo "  make run            - Запустить интерактивный режим"
	@echo "  make demo           - Запустить демо-режим"
	@echo "  make clean          - Очистить временные файлы"