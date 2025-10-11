# Makefile for OneFlow.AI Testing
# Makefile для тестирования OneFlow.AI

.PHONY: help test test-unit test-e2e test-integration test-all test-coverage test-fast test-slow test-providers test-budget test-routing clean install-dev

help:
	@echo "OneFlow.AI Commands:"
	@echo ""
	@echo "Dependencies:"
	@echo "  make install           - Install production dependencies"
	@echo "  make install-dev       - Install development dependencies"
	@echo "  make compile-deps      - Compile .in files to .txt"
	@echo "  make update-deps       - Update dependencies to latest versions"
	@echo "  make sync-deps         - Sync production environment"
	@echo "  make sync-dev          - Sync development environment"
	@echo "  make clean-deps        - Clean compiled dependency files"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests with default settings"
	@echo "  make test-unit         - Run only unit tests (fast)"
	@echo "  make test-e2e          - Run only end-to-end tests"
	@echo "  make test-integration  - Run integration tests"
	@echo "  make test-fast         - Run fast tests only"
	@echo "  make test-slow         - Run slow tests only"
	@echo "  make test-providers    - Run provider tests"
	@echo "  make test-budget       - Run budget/pricing tests"
	@echo "  make test-routing      - Run routing tests"
	@echo "  make test-coverage     - Run tests with coverage report"
	@echo "  make test-all          - Run all tests with verbose output"
	@echo "  make test-watch        - Run tests in watch mode"
	@echo "  make clean             - Clean test artifacts"

# ============================================
# Dependency Management (pip-tools)
# ============================================

# Install pip-tools
install-pip-tools:
	pip install pip-tools

# Compile dependencies (create lock files)
compile-deps: install-pip-tools
	pip-compile requirements.in -o requirements.txt --resolver=backtracking
	pip-compile requirements-dev.in -o requirements-dev.txt --resolver=backtracking

# Update dependencies to latest versions
update-deps: install-pip-tools
	pip-compile --upgrade requirements.in -o requirements.txt --resolver=backtracking
	pip-compile --upgrade requirements-dev.in -o requirements-dev.txt --resolver=backtracking

# Sync environment with production dependencies
sync-deps: install-pip-tools
	pip-sync requirements.txt

# Sync environment with dev dependencies
sync-dev: install-pip-tools
	pip-sync requirements-dev.txt

# Install production dependencies
install: compile-deps
	pip install -r requirements.txt

# Install development dependencies
install-dev: compile-deps
	pip install -r requirements-dev.txt

# Clean compiled dependency files
clean-deps:
	rm -f requirements.txt requirements-dev.txt

# ============================================
# Testing Commands
# ============================================

# Default test command (matches pytest.ini settings)
test:
	pytest -q --maxfail=1 --disable-warnings

# Unit tests only (fast, isolated)
test-unit:
	pytest tests/unit/ -q --maxfail=1 --disable-warnings -m unit

# End-to-end tests only
test-e2e:
	pytest tests/e2e/ -q --maxfail=1 --disable-warnings -m e2e

# Integration tests
test-integration:
	pytest -q --maxfail=1 --disable-warnings -m integration

# Fast tests (excludes slow tests)
test-fast:
	pytest -q --maxfail=1 --disable-warnings -m "not slow"

# Slow tests only
test-slow:
	pytest -q --maxfail=1 --disable-warnings -m slow

# Provider-specific tests
test-providers:
	pytest -q --maxfail=1 --disable-warnings -m providers

# Budget and pricing tests
test-budget:
	pytest -q --maxfail=1 --disable-warnings -m budget

# Routing tests
test-routing:
	pytest -q --maxfail=1 --disable-warnings -m routing

# Authentication tests
test-auth:
	pytest tests/unit/test_auth.py -q --maxfail=1 --disable-warnings -m auth

# Database tests
test-db:
	pytest tests/unit/test_database.py -q --maxfail=1 --disable-warnings -m db

# Coverage report
test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing --cov-branch
	@echo "Coverage report generated in htmlcov/index.html"

# All tests with verbose output
test-all:
	pytest -v --tb=short

# Verbose test with full output
test-verbose:
	pytest -vv --tb=long --disable-warnings

# Run specific test file
test-file:
	pytest $(FILE) -q --maxfail=1 --disable-warnings

# Run specific test function
test-func:
	pytest $(FILE)::$(FUNC) -v

# Watch mode (requires pytest-watch)
test-watch:
	ptw -- -q --maxfail=1 --disable-warnings

# Parallel execution (requires pytest-xdist)
test-parallel:
	pytest -n auto -q --maxfail=1 --disable-warnings

# Test with profiling
test-profile:
	pytest --profile --profile-svg

# Clean test artifacts
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.db
	rm -rf *.log
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Install test dependencies (legacy, use install-dev instead)
install-test:
	pip install pytest pytest-cov pytest-mock pytest-asyncio
	pip install responses respx httpx
	pip install pytest-xdist pytest-watch

# Run tests in CI mode (strict, no warnings, fail fast)
test-ci:
	pytest -q --maxfail=1 --strict-markers --disable-warnings --tb=short

# Generate test report
test-report:
	pytest --html=report.html --self-contained-html

# Check test quality (lint tests)
test-lint:
	pylint tests/
	flake8 tests/
	mypy tests/

# Run mutation testing (requires mutmut)
test-mutation:
	mutmut run

# Benchmark tests
test-benchmark:
	pytest tests/ --benchmark-only

# Security testing
test-security:
	bandit -r src/
	safety check

# Full quality check (tests + linting + security)
test-quality: test-lint test test-security
	@echo "All quality checks passed!"

# Quick smoke test (fastest critical tests)
test-smoke:
	pytest tests/unit/test_router.py tests/unit/test_wallet.py -q --maxfail=1 --disable-warnings
