# OpusGenie DI Development Makefile

.PHONY: help install format lint typecheck test examples build ci-check clean

# Default target
help:
	@echo "OpusGenie DI Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install     - Install dependencies with uv"
	@echo "  clean       - Clean build artifacts and cache"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  format      - Format code with ruff"
	@echo "  lint        - Lint code with ruff"
	@echo "  typecheck   - Type check with mypy"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test        - Run all tests (currently examples)"
	@echo "  examples    - Run example scripts"
	@echo "  verify-types - Verify registered types display correctly"
	@echo ""
	@echo "Build Commands:"
	@echo "  build       - Build package"
	@echo ""
	@echo "CI Commands:"
	@echo "  ci-check    - Run full CI checks locally (emulates GitHub Actions)"
	@echo ""

# Setup
install:
	@echo "📦 Installing dependencies..."
	uv sync --dev

# Code Quality
format:
	@echo "🎨 Formatting code..."
	uv run ruff format .

lint:
	@echo "🔍 Linting code..."
	uv run ruff check .

typecheck:
	@echo "🏷️  Type checking..."
	uv run mypy opusgenie_di/

# Testing
test: examples
	@echo "✅ All tests passed"

# Verify registered types display (matching GitHub Actions CI)
verify-types:
	@echo "🔍 Verifying registered types display..."
	@uv run python examples/basic_usage.py | grep -q "Registered types.*class.*DatabaseService"
	@uv run python examples/multi_context.py | grep -q "Types.*class.*DatabaseRepository"
	@echo "✅ Registered types verification passed"

examples: verify-types
	@echo "🧪 Running examples..."
	@echo "  → Basic usage example"
	@uv run python examples/basic_usage.py > /dev/null
	@echo "  → Multi-context example"  
	@uv run python examples/multi_context.py > /dev/null
	@echo "✅ Examples completed successfully"

# Build
build:
	@echo "🏗️  Building package..."
	uv build

# CI
ci-check:
	@echo "🚀 Running CI checks locally..."
	@./scripts/ci-check.sh

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Quick development workflow
dev: format lint typecheck examples
	@echo "🎉 Development checks completed!"

# Pre-push checks (same as CI)
pre-push: ci-check