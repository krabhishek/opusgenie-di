#!/bin/bash
set -e

# Local CI Check Script
# Emulates the GitHub Actions CI workflow for local testing

echo "🚀 Running Local CI Checks"
echo "=========================="

# Function to print step headers
print_step() {
    echo ""
    echo "📋 $1"
    echo "----------------------------------------"
}

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ Error: $1 is not installed"
        exit 1
    fi
}

# Check required tools
print_step "Checking Required Tools"
check_command "uv"
echo "✅ uv is available"

# Activate virtual environment
print_step "Activating Virtual Environment"
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run 'uv sync' first."
    exit 1
fi
source .venv/bin/activate
echo "✅ Virtual environment activated"

# Check Python version
print_step "Checking Python Version"
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.12"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version+ required, found $python_version"
    exit 1
fi
echo "✅ Python version: $(python --version)"

# Install dependencies
print_step "Installing Dependencies"
uv sync --dev
echo "✅ Dependencies installed"

# Code formatting check
print_step "Code Formatting Check (ruff format)"
if uv run ruff format --check .; then
    echo "✅ Code formatting is correct"
else
    echo "❌ Code formatting issues found. Run 'uv run ruff format .' to fix."
    exit 1
fi

# Linting
print_step "Linting (ruff check)"
if uv run ruff check .; then
    echo "✅ No linting issues found"
else
    echo "❌ Linting issues found. Check output above."
    exit 1
fi

# Type checking
print_step "Type Checking (mypy)"
if uv run mypy opusgenie_di/; then
    echo "✅ Type checking passed"
else
    echo "❌ Type checking failed. Check output above."
    exit 1
fi

# Test basic usage example
print_step "Testing Basic Usage Example"
if uv run python examples/basic_usage.py > /dev/null 2>&1; then
    echo "✅ Basic usage example works"
else
    echo "❌ Basic usage example failed"
    uv run python examples/basic_usage.py
    exit 1
fi

# Test multi-context example
print_step "Testing Multi-Context Example"
if uv run python examples/multi_context.py > /dev/null 2>&1; then
    echo "✅ Multi-context example works"
else
    echo "❌ Multi-context example failed"
    uv run python examples/multi_context.py
    exit 1
fi

# Test registered types display (matching GitHub Actions)
print_step "Testing Registered Types Display"
if uv run python examples/basic_usage.py | grep -q "Registered types.*class.*DatabaseService"; then
    echo "✅ Basic usage registered types check passed"
else
    echo "❌ Basic usage registered types check failed"
    uv run python examples/basic_usage.py
    exit 1
fi

if uv run python examples/multi_context.py | grep -q "Types.*class.*DatabaseRepository"; then
    echo "✅ Multi-context registered types check passed"
else
    echo "❌ Multi-context registered types check failed"
    uv run python examples/multi_context.py
    exit 1
fi

# Test package import
print_step "Testing Package Import"
if uv run python -c "import opusgenie_di; print(f'Package version: {opusgenie_di.__version__}')"; then
    echo "✅ Package imports successfully"
else
    echo "❌ Package import failed"
    exit 1
fi

# Test package build
print_step "Testing Package Build"
if uv build; then
    echo "✅ Package builds successfully"
    # Clean up build artifacts
    rm -rf dist/ *.egg-info/
else
    echo "❌ Package build failed"
    exit 1
fi

# Summary
echo ""
echo "🎉 All CI Checks Passed!"
echo "========================"
echo "✅ Code formatting"
echo "✅ Linting" 
echo "✅ Type checking"
echo "✅ Basic usage example"
echo "✅ Multi-context example"
echo "✅ Registered types display"
echo "✅ Package import"
echo "✅ Package build"
echo ""
echo "🚀 Ready to push to GitHub!"