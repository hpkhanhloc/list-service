.PHONY: help install test deploy destroy clean lint format

# Load environment variables from .env file if it exists
-include .env
export

# Default target
help:
	@echo "ListService - Makefile Commands"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run unit tests"
	@echo "  make test-cov   - Run tests with coverage"
	@echo "  make test-int   - Run integration tests (requires deployed API)"
	@echo "  make format     - Format code with black"
	@echo "  make destroy    - Destroy AWS resources"
	@echo "  make clean      - Clean temporary files"
	@echo ""

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run unit tests
test:
	pytest tests/unit/ -v

# Run tests with coverage
test-cov:
	pytest tests/unit/ --cov=src --cov-report=term --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# Run integration tests
test-int:
	@if [ -z "$(API_ENDPOINT)" ]; then \
		echo "Error: API_ENDPOINT not set. Please run: source .env"; \
		exit 1; \
	fi
	pytest tests/integration/ -v

# Run all tests
test-all: test test-int

# Format code
format:
	black src tests
	@echo "Code formatted!"

# Clean temporary files
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf venv
	rm -rf lambda_deployment_package.zip
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned temporary files!"
