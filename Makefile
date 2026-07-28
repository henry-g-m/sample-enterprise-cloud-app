.PHONY: help install dev test lint format type-check clean run docker-build docker-up docker-down

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements-dev.txt

dev: ## Start development server
	uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linting checks
	ruff check src/ tests/

format: ## Format code with black
	black src/ tests/
	isort src/ tests/

format-check: ## Check code formatting without changes
	black --check src/ tests/
	isort --check-only src/ tests/

type-check: ## Run type checking with mypy
	mypy src/ --strict

clean: ## Remove build and test artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .mypy_cache/ htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build: ## Build Docker image
	docker build -t demo-app:latest .

docker-up: ## Start services with docker-compose
	docker-compose up -d

docker-down: ## Stop services with docker-compose
	docker-compose down

docker-logs: ## View docker logs
	docker-compose logs -f app

docker-test: ## Run tests in Docker container
	docker-compose exec app pytest tests/ -v

all: clean install lint type-check test ## Run all checks and tests
