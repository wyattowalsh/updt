.PHONY: help install install-dev install-docs dev test test-cov test-html test-watch test-unit test-integration lint format check pre-commit docs docs-serve docs-clean clean build

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package
	pip install -e .

install-dev: ## Install with development dependencies
	pip install -e ".[dev]"

install-docs: ## Install documentation dependencies
	pip install -e ".[docs]"

dev: ## Install all dependencies (dev + docs)
	pip install -e ".[dev,docs]"

test: ## Run all tests
	pytest -v

test-cov: ## Run tests with coverage report
	pytest --cov=src/updt --cov-report=term-missing --cov-report=html -v

test-html: ## Generate HTML test report
	pytest --html=htmlcov/test-report.html --self-contained-html

test-watch: ## Run tests in watch mode
	pytest-watch

test-unit: ## Run unit tests only
	pytest tests/test_*.py -v -k "not integration"

test-integration: ## Run integration tests only
	pytest tests/test_integration.py -v

lint: ## Run linters (ruff + mypy)
	ruff check src tests
	mypy src

format: ## Format code with ruff
	ruff format src tests
	ruff check --fix src tests

check: lint test ## Run all checks (lint + test)

pre-commit: ## Install pre-commit hooks
	pre-commit install

docs: ## Build documentation
	cd docs && sphinx-build -b html source _build/html

docs-serve: docs ## Serve documentation locally
	@echo "Serving docs at http://localhost:8000"
	cd docs/_build/html && python -m http.server 8000

docs-clean: ## Clean documentation build
	rm -rf docs/_build

clean: ## Clean all build artifacts
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build package wheel
	python -m build
