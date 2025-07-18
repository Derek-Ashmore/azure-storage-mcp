#!/bin/bash
# Test runner script for Azure Storage MCP
set -e

echo "🧪 Running Azure Storage MCP tests..."

# Run linting
echo "🔍 Running linting..."
uv run ruff check src tests

# Run formatting check
echo "🎨 Checking code formatting..."
uv run black --check src tests

# Run type checking
echo "🔍 Running type checking..."
uv run mypy src

# Run tests with coverage
echo "🧪 Running tests with coverage..."
uv run pytest --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=75

echo "✅ All tests passed!"
echo "📄 Coverage report available at: htmlcov/index.html"