#!/bin/bash
set -e

echo "🚀 Setting up OpusGenie DI Development Environment"
echo "=================================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is available"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --dev

# Make scripts executable
echo "🔧 Setting up scripts..."
chmod +x scripts/ci-check.sh
chmod +x scripts/setup-dev.sh

# Run initial checks
echo "🧪 Running initial checks..."
make dev

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  make help       - Show all available commands"
echo "  make dev        - Run quick development checks"
echo "  make ci-check   - Run full CI checks (emulates GitHub Actions)"
echo "  make examples   - Run example scripts"
echo ""
echo "Before pushing code, always run:"
echo "  make ci-check"
echo ""