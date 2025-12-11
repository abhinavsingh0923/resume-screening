.PHONY: help install run test clean format lint type-check dev setup

# Default target
help:
	@echo "Resume Screener - Available Commands:"
	@echo ""
	@echo "  make setup        - Complete project setup (first time)"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the Streamlit application"
	@echo "  make dev          - Run in development mode with auto-reload"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with ruff"
	@echo "  make type-check   - Run type checking with mypy"
	@echo "  make clean        - Remove cache and temporary files"
	@echo "  make all          - Format, lint, test"
	@echo ""

# First-time setup
setup:
	@echo "🚀 Setting up Resume Screener..."
	@if ! command -v uv &> /dev/null; then \
		echo "❌ uv not found. Installing..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "✅ uv already installed"; \
	fi
	@echo "📦 Creating virtual environment..."
	uv venv
	@echo "📥 Installing dependencies..."
	uv sync
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp .env.template .env; \
		echo "⚠️  Please edit .env and add your GOOGLE_API_KEY"; \
	fi
	@echo "✅ Setup complete! Run 'make run' to start the application"

# Install dependencies
install:
	@echo "📥 Installing dependencies..."
	uv sync

# Run the application
run:
	@echo "🚀 Starting Resume Screener..."
	@if [ ! -f .env ]; then \
		echo "⚠️  Warning: .env file not found. Create from .env.template"; \
	fi
	uv run streamlit run app/app.py

# Run in development mode
dev:
	@echo "🔧 Starting in development mode..."
	uv run streamlit run app/app.py --server.runOnSave=true

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	uv run pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report generated in htmlcov/index.html"

# Format code
format:
	@echo "🎨 Formatting code..."
	uv run black .
	@echo "✅ Code formatted"

# Lint code
lint:
	@echo "🔍 Linting code..."
	uv run ruff check .
	@echo "✅ Linting complete"

# Type checking
type-check:
	@echo "🔍 Running type checks..."
	uv run mypy .
	@echo "✅ Type checking complete"

# Run all quality checks
all: format lint type-check test
	@echo "✅ All checks passed!"

# Clean cache and temporary files
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Development setup with all tools
dev-setup: setup
	@echo "🔧 Installing development dependencies..."
	uv add --dev pytest pytest-asyncio pytest-cov black ruff mypy
	@echo "✅ Development setup complete"

# Quick test (no coverage)
quick-test:
	@echo "⚡ Running quick tests..."
	uv run pytest tests/ -v -x

# Watch mode for tests
test-watch:
	@echo "👀 Running tests in watch mode..."
	uv run pytest-watch tests/ -v

# Generate requirements.txt (for compatibility)
requirements:
	@echo "📝 Generating requirements.txt..."
	uv pip compile pyproject.toml -o requirements.txt
	@echo "✅ requirements.txt generated"

# Update dependencies
update:
	@echo "⬆️  Updating dependencies..."
	uv sync --upgrade
	@echo "✅ Dependencies updated"

# Check for outdated packages
outdated:
	@echo "🔍 Checking for outdated packages..."
	uv pip list --outdated

# Build for distribution
build:
	@echo "📦 Building distribution..."
	uv build
	@echo "✅ Build complete"

# Docker build
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t resume-screener .

# Docker run
docker-run:
	@echo "🚀 Running Docker container..."
	docker run -p 8501:8501 --env-file .env resume-screener

# Deploy to Streamlit Cloud (requires git)
deploy:
	@echo "🚀 Preparing for deployment..."
	@if [ -z "$$(git status --porcelain)" ]; then \
		echo "✅ Working directory clean"; \
		echo "📤 Push to GitHub to deploy to Streamlit Cloud"; \
		echo "Visit: https://share.streamlit.io"; \
	else \
		echo "⚠️  Uncommitted changes found. Commit first:"; \
		git status --short; \
	fi

# Show project info
info:
	@echo "📊 Project Information:"
	@echo ""
	@echo "Python version: $$(python --version)"
	@echo "uv version: $$(uv --version)"
	@echo "Virtual env: $$(if [ -d .venv ]; then echo '✅ Active'; else echo '❌ Not found'; fi)"
	@echo ""
	@if [ -f pyproject.toml ]; then \
		echo "Dependencies:"; \
		uv pip list; \
	fi

# Create sample data directory
sample-data:
	@echo "📁 Creating sample data directory..."
	mkdir -p sample_data
	@echo "✅ sample_data/ directory created"
	@echo "Add sample resumes and JD here for testing"