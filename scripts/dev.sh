#!/bin/bash
# Development setup script for Azure Storage MCP
set -e

echo "🚀 Setting up Azure Storage MCP development environment..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Installing it now..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --all-extras

# Setup pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🔧 Setting up pre-commit hooks..."
    uv run pre-commit install
else
    echo "⚠️  pre-commit not found, skipping hooks setup"
fi

# Run initial code quality checks
echo "🔍 Running initial code quality checks..."
uv run ruff check src tests
uv run black --check src tests

# Run type checking
echo "🔍 Running type checking..."
uv run mypy src

# Run tests
echo "🧪 Running tests..."
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

echo "✅ Development environment setup complete!"
echo "📄 Coverage report available at: htmlcov/index.html"
echo ""
echo "🌟 Next steps:"
echo "  1. Configure Azure authentication: az login"
echo "  2. Test the MCP server: uv run azure-storage-mcp"
echo "  3. Run development server: uv run python -m azure_storage_mcp.server"