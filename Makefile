.PHONY: install fmt lint typecheck test cov run docker-build docker-up release help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
FLAKE8 := $(PYTHON) -m flake8
DOCKER_IMAGE := oneflow-ai
DOCKER_TAG := 2.0.0

help: ## Show available commands
	@echo "OneFlow.AI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

fmt: ## Format code with black and isort
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

lint: ## Run linters
	$(FLAKE8) src/ tests/ --max-line-length=100

typecheck: ## Run type checker
	mypy src/ --ignore-missing-imports

test: ## Run tests
	$(PYTEST) tests/ -v

cov: ## Run tests with coverage
	$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term

run: ## Run development server
	uvicorn web_server:app --reload --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest

docker-up: ## Start services with docker-compose
	docker-compose up -d

release: lint typecheck test docker-build ## Build release (lint + typecheck + test + docker-build)
	@echo "✅ Release build complete: $(DOCKER_IMAGE):$(DOCKER_TAG)"
