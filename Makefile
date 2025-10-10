.PHONY: help install test lint format clean docker-build docker-up docker-down k8s-deploy

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
FLAKE8 := $(PYTHON) -m flake8
DOCKER_IMAGE := oneflow-ai
DOCKER_TAG := 2.0.0

help: ## Show this help message
	@echo "OneFlow.AI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===== Installation =====

install: ## Install all dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

install-dev: ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"
	pre-commit install

# ===== Testing =====

test: ## Run all tests
	$(PYTEST) tests/ -v

test-coverage: ## Run tests with coverage report
	$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term

test-property: ## Run property-based tests
	$(PYTEST) tests/test_pricing_properties.py -v --hypothesis-show-statistics

test-watch: ## Run tests in watch mode
	$(PYTEST) tests/ -v --looponfail

# ===== Code Quality =====

lint: ## Run linters (flake8)
	$(FLAKE8) src/ tests/ --max-line-length=100

format: ## Format code with black and isort
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

format-check: ## Check if code is formatted
	$(BLACK) src/ tests/ --check
	$(ISORT) src/ tests/ --check

type-check: ## Run mypy type checker
	mypy src/ --ignore-missing-imports

# ===== Docker =====

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest

docker-build-no-cache: ## Build Docker image without cache
	docker build --no-cache -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-up: ## Start all services with docker-compose
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## Show logs from all services
	docker-compose logs -f

docker-restart: ## Restart application service
	docker-compose restart app

docker-shell: ## Open shell in app container
	docker-compose exec app /bin/bash

docker-clean: ## Clean Docker volumes and images
	docker-compose down -v
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest || true

# ===== Database =====

db-migrate: ## Run database migrations
	alembic upgrade head

db-rollback: ## Rollback last migration
	alembic downgrade -1

db-reset: ## Reset database (WARNING: drops all data)
	alembic downgrade base
	alembic upgrade head

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U oneflow -d oneflow

# ===== Kubernetes =====

k8s-deploy: ## Deploy to Kubernetes
	kubectl apply -f k8s/

k8s-delete: ## Delete Kubernetes resources
	kubectl delete -f k8s/

k8s-status: ## Show Kubernetes deployment status
	kubectl get all -n oneflow-ai

k8s-logs: ## Show logs from Kubernetes pods
	kubectl logs -f -n oneflow-ai -l app=oneflow-ai

k8s-port-forward: ## Port forward to local machine
	kubectl port-forward -n oneflow-ai svc/oneflow-ai 8000:8000

# ===== Development =====

dev: ## Run development server with auto-reload
	uvicorn web_server:app --reload --host 0.0.0.0 --port 8000

dev-debug: ## Run development server with debug logs
	LOG_LEVEL=DEBUG uvicorn web_server:app --reload --host 0.0.0.0 --port 8000

shell: ## Open Python shell with app context
	$(PYTHON) -i -c "from src.main import *"

# ===== Monitoring =====

prometheus: ## Open Prometheus UI
	@echo "Opening Prometheus at http://localhost:9090"
	@open http://localhost:9090 || xdg-open http://localhost:9090 || echo "Open http://localhost:9090 in your browser"

grafana: ## Open Grafana UI
	@echo "Opening Grafana at http://localhost:3000"
	@echo "Default credentials: admin/admin"
	@open http://localhost:3000 || xdg-open http://localhost:3000 || echo "Open http://localhost:3000 in your browser"

jaeger: ## Open Jaeger UI
	@echo "Opening Jaeger at http://localhost:16686"
	@open http://localhost:16686 || xdg-open http://localhost:16686 || echo "Open http://localhost:16686 in your browser"

# ===== Cleanup =====

clean: ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/ dist/ build/

clean-all: clean docker-clean ## Clean everything including Docker

# ===== Security =====

security-check: ## Run security checks
	$(PYTHON) -m pip install safety bandit
	safety check
	bandit -r src/

audit: ## Audit dependencies for vulnerabilities
	$(PIP) install pip-audit
	pip-audit

# ===== Documentation =====

docs: ## Generate API documentation
	@echo "Documentation available at /docs endpoint when server is running"
	@echo "Run 'make dev' and visit http://localhost:8000/docs"

# ===== Quick Start =====

quickstart: install docker-up db-migrate ## Quick start for new developers
	@echo ""
	@echo "✅ OneFlow.AI setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and add your API keys"
	@echo "  2. Run 'make dev' to start development server"
	@echo "  3. Visit http://localhost:8000/docs for API documentation"
	@echo ""

# ===== Production =====

prod-check: lint type-check test security-check ## Run all pre-production checks
	@echo "✅ All checks passed! Ready for production."

prod-build: prod-check docker-build ## Build production-ready Docker image
	@echo "✅ Production image built: $(DOCKER_IMAGE):$(DOCKER_TAG)"
