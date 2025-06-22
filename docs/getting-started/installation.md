# Installation Guide

*Complete installation and setup instructions for OpusGenie DI*

---

## Requirements

OpusGenie DI requires **Python 3.12** or later and supports the following platforms:

- **Operating Systems**: Linux, macOS, Windows
- **Python Versions**: 3.12, 3.13+
- **Architecture**: x86_64, ARM64

!!! info "Why Python 3.12+?"
    OpusGenie DI leverages modern Python features like enhanced type hints, performance improvements, and better async handling that are only available in Python 3.12+.

## Installation Methods

### Method 1: pip (Standard)

```bash
pip install opusgenie-di
```

### Method 2: uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that OgPgy Bank uses for their development workflow:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add OpusGenie DI to your project
uv add opusgenie-di
```

### Method 3: poetry

```bash
poetry add opusgenie-di
```

### Method 4: Development Installation

For contributing to OpusGenie DI or running the latest features:

```bash
git clone https://github.com/krabhishek/opusgenie-di.git
cd opusgenie-di
uv sync --dev
```

## Verification

Verify your installation by running:

```python
import opusgenie_di
print(f"OpusGenie DI version: {opusgenie_di.__version__}")
```

## Dependencies

OpusGenie DI has minimal dependencies to keep your project lightweight:

```python
dependencies = [
    "dependency-injector>=4.46.0",  # Core DI functionality
    "pydantic>=2.11.5",           # Data validation
    "structlog>=25.3.0",          # Structured logging
    "typing-extensions>=4.0.0",    # Enhanced type hints
]
```

## Development Dependencies

For development, testing, and documentation:

=== "Development Tools"

    ```python
    dev_dependencies = [
        "build>=1.2.2.post1",        # Build system
        "coverage>=7.8.2",           # Code coverage
        "mypy>=1.15.0",              # Type checking
        "pytest>=8.3.5",             # Testing framework
        "pytest-asyncio>=0.24.0",    # Async testing
        "pytest-cov>=6.1.1",         # Coverage integration
        "ruff>=0.11.11",             # Linting and formatting
        "twine>=6.1.0",              # Package publishing
    ]
    ```

=== "Documentation Tools"

    ```python
    docs_dependencies = [
        "mkdocs>=1.6.1",                                 # Documentation
        "mkdocs-awesome-pages-plugin>=2.10.1",          # Page organization
        "mkdocs-git-revision-date-localized-plugin>=1.2.0",  # Git dates
        "mkdocs-macros-plugin>=1.0.0",                  # Macros
        "mkdocs-material[imaging]>=9.6.14",             # Material theme
        "mkdocs-mermaid2-plugin>=1.1.0",                # Diagrams
        "mkdocs-minify-plugin>=0.8.0",                  # Minification
        "mkdocstrings[python]>=0.29.1",                 # API docs
        "pymdown-extensions>=10.15",                     # Markdown extensions
    ]
    ```

## Project Setup

### Basic Project Structure

Here's how Elena Korvas structures a new OpusGenie DI project at OgPgy Bank:

```
ogpgy-banking/
├── src/
│   ├── __init__.py
│   ├── account/
│   │   ├── __init__.py
│   │   ├── services.py
│   │   └── repositories.py
│   ├── payment/
│   │   ├── __init__.py
│   │   ├── services.py
│   │   └── processors.py
│   └── main.py
├── tests/
│   ├── test_account.py
│   └── test_payment.py
├── pyproject.toml
└── README.md
```

### pyproject.toml Configuration

=== "Basic Setup"

    ```toml title="pyproject.toml"
    [project]
    name = "ogpgy-banking"
    version = "1.0.0"
    description = "OgPgy Bank's digital banking platform"
    requires-python = ">=3.12"
    dependencies = [
        "opusgenie-di>=0.1.4",
    ]
    
    [build-system]
    requires = ["setuptools", "wheel"]
    build-backend = "setuptools.build_meta"
    ```

=== "With Development Tools"

    ```toml title="pyproject.toml"
    [project]
    name = "ogpgy-banking"
    version = "1.0.0"
    description = "OgPgy Bank's digital banking platform"
    requires-python = ">=3.12"
    dependencies = [
        "opusgenie-di>=0.1.4",
        "fastapi>=0.104.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.5.0",
    ]
    
    [dependency-groups]
    dev = [
        "pytest>=8.0.0",
        "pytest-asyncio>=0.23.0",
        "mypy>=1.15.0",
        "ruff>=0.11.0",
    ]
    
    [tool.pytest.ini_options]
    asyncio_mode = "auto"
    testpaths = ["tests"]
    
    [tool.mypy]
    python_version = "3.12"
    strict = true
    
    [tool.ruff]
    target-version = "py312"
    line-length = 88
    
    [tool.ruff.lint]
    select = ["E", "W", "F", "I", "N", "UP", "B"]
    ```

## IDE Setup

### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "ruff",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "files.associations": {
        "*.py": "python"
    }
}
```

### PyCharm

1. Open **Settings** → **Project** → **Python Interpreter**
2. Add your virtual environment interpreter
3. Enable **Type Checking** in **Editor** → **Inspections** → **Python**
4. Install the **Pydantic** plugin for enhanced validation support

## Environment Setup

### Virtual Environment (Recommended)

=== "uv"

    ```bash
    # Create new project with uv
    uv init ogpgy-banking
    cd ogpgy-banking
    
    # Add OpusGenie DI
    uv add opusgenie-di
    
    # Activate environment
    source .venv/bin/activate  # Linux/macOS
    # or
    .venv\Scripts\activate     # Windows
    ```

=== "venv"

    ```bash
    # Create virtual environment
    python -m venv venv
    
    # Activate environment
    source venv/bin/activate   # Linux/macOS
    # or
    venv\Scripts\activate      # Windows
    
    # Install OpusGenie DI
    pip install opusgenie-di
    ```

=== "conda"

    ```bash
    # Create conda environment
    conda create -n ogpgy-banking python=3.12
    conda activate ogpgy-banking
    
    # Install OpusGenie DI
    pip install opusgenie-di
    ```

## Docker Setup

For containerized deployments (like OgPgy Bank's production environment):

```dockerfile title="Dockerfile"
FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Run application
CMD ["uv", "run", "python", "-m", "src.main"]
```

## Configuration

### Logging Setup

OpusGenie DI uses structured logging. Here's OgPgy Bank's logging configuration:

```python title="src/logging_config.py"
import structlog
import logging

def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging for OgPgy Bank systems"""
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### Environment Variables

```bash title=".env"
# OgPgy Bank Environment Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@localhost/ogpgy_bank
REDIS_URL=redis://localhost:6379
OPUSGENIE_DI_ENABLE_HOOKS=true
OPUSGENIE_DI_LOG_LEVEL=INFO
```

## Testing Installation

Create a simple test to verify everything works:

```python title="test_installation.py"
import asyncio
from opusgenie_di import (
    og_component, 
    BaseComponent, 
    ComponentScope,
    get_global_context
)

@og_component(scope=ComponentScope.SINGLETON)
class TestService(BaseComponent):
    def greet(self) -> str:
        return "Hello from OgPgy Bank!"

async def test_basic_functionality():
    context = get_global_context()
    context.enable_auto_wiring()
    
    service = context.resolve(TestService)
    message = service.greet()
    
    assert message == "Hello from OgPgy Bank!"
    print("✅ OpusGenie DI installation successful!")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
```

Run the test:

```bash
python test_installation.py
```

## Troubleshooting

### Common Issues

!!! bug "ImportError: No module named 'opusgenie_di'"
    
    **Solution**: Ensure you're in the correct virtual environment and OpusGenie DI is installed:
    ```bash
    pip list | grep opusgenie-di
    ```

!!! bug "TypeError: BaseComponent.__init__() missing 1 required positional argument"
    
    **Solution**: Always call `super().__init__()` in your component constructors:
    ```python
    def __init__(self):
        super().__init__()  # Required!
    ```

!!! bug "ModuleNotFoundError: No module named 'typing_extensions'"
    
    **Solution**: Ensure you're using Python 3.12+ or install typing-extensions:
    ```bash
    pip install typing-extensions
    ```

### Getting Help

- **Documentation**: [OpusGenie DI Docs](https://github.com/krabhishek/opusgenie-di#readme)
- **Issues**: [GitHub Issues](https://github.com/krabhishek/opusgenie-di/issues)
- **Examples**: Check the `examples/` directory in the repository

## Performance Considerations

### Memory Usage

OpusGenie DI is designed to be memory-efficient:

- **Singleton components**: Shared instances reduce memory footprint
- **Lazy initialization**: Components are created only when needed
- **Automatic cleanup**: Resources are properly released during shutdown

### Startup Time

For applications with many components (like OgPgy Bank's 200+ services):

```python
# Enable parallel initialization for faster startup
context.enable_parallel_initialization()

# Use component pre-registration for known dependencies
context.pre_register_components([
    AccountService,
    PaymentProcessor,
    ComplianceChecker
])
```

---

!!! success "Installation Complete!"
    You're now ready to build amazing applications with OpusGenie DI. Head over to the [Quick Start Guide](quickstart.md) to see it in action!