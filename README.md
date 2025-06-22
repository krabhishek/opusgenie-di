# OpusGenie Dependency Injection

[![PyPI version](https://img.shields.io/pypi/v/opusgenie-di.svg)](https://pypi.org/project/opusgenie-di/)
[![Python 3.12+](https://img.shields.io/pypi/pyversions/opusgenie-di.svg)](https://pypi.org/project/opusgenie-di/)
[![PyPI downloads](https://img.shields.io/pypi/dm/opusgenie-di.svg)](https://pypi.org/project/opusgenie-di/)
[![Apache License 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A powerful, multi-context dependency injection framework for Python that provides Angular-style dependency injection with support for multiple isolated contexts, cross-context imports, declarative module definitions, comprehensive async lifecycle management, and event-driven monitoring.

## Features

- **Automatic Dependency Injection**: Robust auto-wiring of dependencies based on type hints
- **Multi-Context Architecture**: Create isolated dependency contexts with clear boundaries
- **Cross-Context Dependencies**: Automatically inject dependencies from imported contexts
- **Declarative Configuration**: Use `@og_component` and `@og_context` decorators for clean setup
- **Component Scopes**: Singleton, Transient, and Scoped lifecycles
- **Async Lifecycle Management**: Comprehensive async/await support with event loop management
- **Event-Driven Monitoring**: Lifecycle callbacks for component creation and disposal
- **Type Safety**: Full type safety with Python type hints and runtime validation
- **Event System**: Built-in event hooks for monitoring and extension
- **Framework Agnostic**: No dependencies on specific frameworks
- **Testing Support**: Comprehensive testing utilities and mocks

## Installation

```bash
pip install opusgenie-di
```

## Quick Start

### Basic Usage with Automatic Dependency Injection

```python
from opusgenie_di import og_component, BaseComponent, ComponentScope, get_global_context

# Define a simple component
@og_component(scope=ComponentScope.SINGLETON)
class DatabaseService(BaseComponent):
    def get_data(self) -> str:
        return "Data from database"

# Define a component with automatic dependency injection
@og_component(scope=ComponentScope.SINGLETON)
class UserService(BaseComponent):
    def __init__(self, db_service: DatabaseService) -> None:  # No | None = None needed!
        super().__init__()
        # Natural assignment - clean and intuitive!
        self.db_service = db_service

    def get_user(self, user_id: str) -> dict[str, str]:
        data = self.db_service.get_data()
        return {"id": user_id, "name": f"User_{user_id}", "source": data}

# Use the global context with auto-wiring enabled
context = get_global_context()
context.enable_auto_wiring()  # Enable automatic dependency injection

user_service = context.resolve(UserService)  # DatabaseService automatically injected!
user_data = user_service.get_user("123")
print(user_data)  # {'id': '123', 'name': 'User_123', 'source': 'Data from database'}
```

### Multi-Context Architecture with Cross-Context Auto-Wiring

```python
from opusgenie_di import (
    og_component, og_context, BaseComponent, ComponentScope,
    ContextModuleBuilder, ModuleContextImport
)

# Infrastructure layer components
@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class DatabaseRepository(BaseComponent):
    def get_data(self) -> str:
        return "Data from database"

@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class CacheRepository(BaseComponent):
    def get_cached_data(self) -> str:
        return "Cached data"

# Business layer components with cross-context dependencies
@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class BusinessService(BaseComponent):
    def __init__(self, db_repo: DatabaseRepository, cache_repo: CacheRepository) -> None:
        super().__init__()
        # Dependencies automatically injected from infrastructure context!
        self.db_repo = db_repo
        self.cache_repo = cache_repo

    def process_data(self) -> dict[str, str]:
        return {
            "status": "processed",
            "db_data": self.db_repo.get_data(),
            "cache_data": self.cache_repo.get_cached_data(),
        }

# Define module contexts
@og_context(
    name="infrastructure_context",
    imports=[],  # Base layer - no imports
    exports=[DatabaseRepository, CacheRepository],
    providers=[DatabaseRepository, CacheRepository],
)
class InfrastructureModule:
    pass

@og_context(
    name="business_context",
    imports=[
        ModuleContextImport(component_type=DatabaseRepository, from_context="infrastructure_context"),
        ModuleContextImport(component_type=CacheRepository, from_context="infrastructure_context"),
    ],
    exports=[BusinessService],
    providers=[BusinessService],
)
class BusinessModule:
    pass

# Build and use contexts (auto-wiring happens automatically!)
async def main():
    builder = ContextModuleBuilder()
    contexts = await builder.build_contexts(InfrastructureModule, BusinessModule)
    
    business_context = contexts["business_context"]
    business_service = business_context.resolve(BusinessService)  # All dependencies auto-injected!
    result = business_service.process_data()
    print(result)  # {'status': 'processed', 'db_data': 'Data from database', 'cache_data': 'Cached data'}
```

## Automatic Dependency Injection

OpusGenie DI provides robust automatic dependency injection based on constructor type hints. The framework automatically analyzes constructor parameters and injects the appropriate dependencies.

### How It Works

1. **Type Analysis**: The framework analyzes constructor type hints to determine dependencies
2. **Automatic Resolution**: Dependencies are automatically resolved from the context or imported contexts  
3. **Lazy Evaluation**: Dependencies are resolved at component creation time, not registration time
4. **Cross-Context Support**: Dependencies can be automatically injected from imported contexts

### Key Features

- **No Manual Configuration**: Just declare dependencies in constructor parameters
- **Type-Safe**: Uses Python type hints for dependency resolution
- **Cross-Context**: Automatically resolves dependencies from imported contexts
- **Error Handling**: Clear error messages for missing or circular dependencies
- **Circular Dependency Detection**: Runtime detection of circular dependencies with detailed error reporting
- **Optional Dependencies**: Support for optional dependencies with type unions

### Example: Simple Auto-Wiring

```python
@og_component()
class EmailService(BaseComponent):
    def send_email(self, message: str) -> bool:
        print(f"Sending email: {message}")
        return True

@og_component()
class NotificationService(BaseComponent):
    # EmailService automatically injected!
    def __init__(self, email_service: EmailService) -> None:
        super().__init__()
        self.email_service = email_service
    
    def notify(self, message: str) -> None:
        self.email_service.send_email(message)

# Enable auto-wiring and use
context = get_global_context()
context.enable_auto_wiring()
notification_service = context.resolve(NotificationService)  # EmailService auto-injected!
```

### Example: Cross-Context Auto-Wiring

```python
# Dependencies from infrastructure context automatically injected into business context
@og_context(
    name="business_context",
    imports=[
        ModuleContextImport(component_type=DatabaseService, from_context="infrastructure"),
        ModuleContextImport(component_type=CacheService, from_context="infrastructure"),
    ],
    providers=[UserService],
)
class BusinessModule:
    pass

@og_component(auto_register=False)
class UserService(BaseComponent):
    def __init__(self, db: DatabaseService, cache: CacheService) -> None:
        super().__init__()
        # Both dependencies automatically resolved from infrastructure context!
        self.db = db
        self.cache = cache
```

### Optional Dependencies

```python
@og_component()
class ServiceWithOptionalDependency(BaseComponent):
    def __init__(self, required_service: RequiredService, 
                 optional_service: OptionalService | None = None) -> None:
        super().__init__()
        self.required_service = required_service
        self.optional_service = optional_service  # Will be None if not available
```

### Circular Dependency Detection

OpusGenie DI provides runtime circular dependency detection to prevent infinite loops during component resolution. When a circular dependency is detected, a `CircularDependencyError` is raised with detailed information about the dependency chain.

#### How It Works

The framework tracks the component resolution chain using thread-local storage. When a component is being resolved, it checks if that component is already in the current resolution chain, indicating a circular dependency.

#### Example: Detecting Circular Dependencies

```python
from opusgenie_di import og_component, BaseComponent, ComponentScope, Context, CircularDependencyError

@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class ServiceA(BaseComponent):
    def __init__(self, service_b: "ServiceB") -> None:  # Forward reference
        super().__init__()
        self.service_b = service_b

@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class ServiceB(BaseComponent):
    def __init__(self, service_a: ServiceA) -> None:
        super().__init__()
        self.service_a = service_a

# Register components
context = Context("example_context")
context.register_component(ServiceA, scope=ComponentScope.SINGLETON)
context.register_component(ServiceB, scope=ComponentScope.SINGLETON)
context.enable_auto_wiring()

# This will detect the circular dependency
try:
    service_a = context.resolve(ServiceA)
except CircularDependencyError as e:
    print(f"Circular dependency detected: {e.message}")
    print(f"Dependency chain: {' -> '.join(e.dependency_chain)}")
    # Output: Dependency chain: ServiceA -> ServiceB -> ServiceA
```

#### Key Benefits

- **Runtime Detection**: Circular dependencies are detected when components are actually resolved, not at registration time
- **Clear Error Messages**: The error includes the complete dependency chain showing exactly where the cycle occurs
- **Forward Reference Support**: Works with forward references in type hints (e.g., `"ServiceB"`)
- **Thread-Safe**: Uses thread-local storage to track resolution chains, making it safe for concurrent use
- **Zero Performance Impact**: No overhead when no circular dependencies exist

#### Best Practices

While the framework detects circular dependencies, it's better to design your architecture to avoid them:

```python
# Instead of circular dependencies, use a shared dependency
@og_component()
class SharedConfig(BaseComponent):
    def __init__(self) -> None:
        super().__init__()
        self.setting = "shared_value"

@og_component()
class ServiceA(BaseComponent):
    def __init__(self, config: SharedConfig) -> None:
        super().__init__()
        self.config = config

@og_component()
class ServiceB(BaseComponent):
    def __init__(self, config: SharedConfig) -> None:
        super().__init__()
        self.config = config
```

## Component Scopes

- **Singleton**: One instance per context (default)
- **Transient**: New instance every time
- **Scoped**: One instance per scope (useful for request-scoped dependencies)

```python
from opusgenie_di import og_component, ComponentScope

@og_component(scope=ComponentScope.SINGLETON)
class SingletonService(BaseComponent):
    pass

@og_component(scope=ComponentScope.TRANSIENT)
class TransientService(BaseComponent):
    pass

@og_component(scope=ComponentScope.SCOPED)
class ScopedService(BaseComponent):
    pass
```

## Event Hooks and Extension

```python
from opusgenie_di import register_hook, register_lifecycle_hook, LifecycleStage

# Register event hooks
@register_hook("component.resolved")
def on_component_resolved(event_data):
    print(f"Component resolved: {event_data['component_type']}")

# Register lifecycle hooks
@register_lifecycle_hook(LifecycleStage.POST_INIT)
def on_component_initialized(component):
    print(f"Component initialized: {type(component).__name__}")
```

## Testing Support

```python
from opusgenie_di import create_test_context, MockComponent, reset_global_state

def test_my_service():
    # Create isolated test context
    context = create_test_context()
    
    # Use mock components
    mock_db = MockComponent(return_value="test data")
    context.register_instance(DatabaseService, mock_db)
    
    # Test your service
    user_service = context.resolve(UserService)
    result = user_service.get_user("123")
    assert result["source"] == "test data"
    
    # Clean up
    reset_global_state()
```

## Advanced Features

### Cross-Context Communication

```python
# Import specific components from other contexts
@og_context(
    name="api_context",
    imports=[
        ModuleContextImport(DatabaseService, from_context="infrastructure"),
        ModuleContextImport(BusinessService, from_context="business", alias="BizService"),
    ],
    providers=[ApiController],
)
class ApiModule:
    pass
```

### Component Metadata and Tags

```python
@og_component(
    scope=ComponentScope.SINGLETON,
    tags=["database", "infrastructure"],
    metadata={"connection_pool_size": 10}
)
class DatabaseService(BaseComponent):
    pass
```

### Async Lifecycle Management

OpusGenie DI v0.1.4 introduces comprehensive async lifecycle management for robust async/await support:

#### Event Loop Management

```python
from opusgenie_di import get_event_loop_manager, run_async_safely

# Automatic event loop management
event_manager = get_event_loop_manager()

# Safe async execution in any context
async def cleanup_resources():
    # Your async cleanup code
    pass

# This works whether or not an event loop is running
run_async_safely(cleanup_resources())
```

#### Async Component Lifecycle

```python
@og_component()
class AsyncService(BaseComponent):
    async def initialize(self) -> None:
        """Async initialization - called automatically"""
        await super().initialize()
        # Your async setup code
        
    async def cleanup(self) -> None:
        """Async cleanup - called on disposal"""
        await super().cleanup()
        # Your async cleanup code
        
    def cleanup_sync(self) -> None:
        """Sync cleanup fallback"""
        super().cleanup_sync()
        # Sync cleanup code
```

#### Lifecycle Callbacks and Monitoring

```python
from opusgenie_di import ScopeManager

def lifecycle_callback(event: str, **kwargs):
    print(f"Component {event}: {kwargs.get('component_type')}")

# Create scope manager with lifecycle monitoring
scope_manager = ScopeManager(lifecycle_callback=lifecycle_callback)

# Events are triggered for:
# - instance_created: When a component is instantiated
# - instance_disposed: When a component is cleaned up
```

#### Mixed Sync/Async Support

```python
@og_component()
class FlexibleService(BaseComponent):
    def dispose(self) -> None:
        """Sync disposal method"""
        self.cleanup_resources()
        
    async def cleanup(self) -> None:
        """Async cleanup method (preferred)"""
        await self.async_cleanup_resources()
        
    # The framework automatically chooses the appropriate method
    # based on event loop availability
```

#### Key Benefits

- **Guaranteed Async Execution**: Components with async lifecycle methods are properly awaited
- **Graceful Fallbacks**: Automatic fallback to sync methods when no event loop is available  
- **Event-Driven Monitoring**: Lifecycle callbacks for observability and debugging
- **Zero Configuration**: Works out of the box with existing sync components
- **Thread Safe**: Event loop management is thread-safe for concurrent applications

### Async Resolution

```python
from opusgenie_di import resolve_global_component_async

async def main():
    service = await resolve_global_component_async(AsyncService)
    result = await service.process_async()
```

## Type Safety

OpusGenie DI is fully typed and supports:

- Type hints for all public APIs
- Runtime type validation with Pydantic
- Generic type support
- Protocol-based interfaces

```python
from typing import Protocol
from opusgenie_di import og_component, BaseComponent

class DataProvider(Protocol):
    def get_data(self) -> str: ...

@og_component()
class DatabaseProvider(BaseComponent):
    def get_data(self) -> str:
        return "database data"

@og_component()
class ServiceWithProtocol(BaseComponent):
    def __init__(self, provider: DataProvider) -> None:
        super().__init__()
        self.provider = provider
```

## Performance Considerations

- **Lazy Loading**: Components are created only when needed
- **Smart Auto-Wiring**: Dependencies are analyzed once and cached for fast resolution
- **Efficient Resolution**: Auto-wiring uses optimized factory functions for dependency injection
- **Caching**: Singleton instances are cached for performance
- **Minimal Overhead**: Built on top of proven `dependency-injector` library
- **Memory Efficient**: Contexts can be disposed when no longer needed
- **Cross-Context Optimization**: Imported dependencies are resolved efficiently without duplication

## Development and Contributing

### Quick Setup

```bash
git clone <repository-url>
cd opusgenie-di
./scripts/setup-dev.sh
```

### Development Workflow

```bash
# Quick development checks
make dev

# Full CI checks (emulates GitHub Actions locally)
make ci-check

# Individual commands
make format      # Format code with ruff
make lint        # Lint code with ruff  
make typecheck   # Type check with mypy
make examples    # Run example scripts
make build       # Build package
```

### Pre-Push Validation

**Always run before pushing:**
```bash
make ci-check
```

This emulates the exact GitHub Actions workflow locally and catches issues before they reach CI.

### Running Tests

```bash
pytest tests/ -v
```

### Running Examples

```bash
# Basic usage
python examples/basic_usage.py

# Multi-context example
python examples/multi_context.py
```

## API Reference

### Core Classes

- `BaseComponent`: Base class for all DI components
- `Context`: Dependency injection context
- `Container`: Internal container implementation
- `GlobalContext`: Singleton global context

### Decorators

- `@og_component`: Register a class as a DI component
- `@og_context`: Define a context module

### Enums

- `ComponentScope`: Singleton, Transient, Scoped
- `LifecycleStage`: Component lifecycle stages

### Utilities

- `get_global_context()`: Access the global context
- `reset_global_context()`: Reset global state
- `create_test_context()`: Create isolated test context
- `context.enable_auto_wiring()`: Enable automatic dependency injection for a context
- `ContextModuleBuilder()`: Build contexts with automatic cross-context wiring

## Migration Guide

### Upgrading to Auto-Wiring

**Before (manual dependency handling):**
```python
def __init__(self, db_service: DatabaseService | None = None) -> None:
    super().__init__()
    self.__dict__["db_service"] = db_service

def get_data(self):
    db_service = self.__dict__.get("db_service")
    if db_service:
        return db_service.get_data()
    return "no data"
```

**After (automatic dependency injection):**
```python
def __init__(self, db_service: DatabaseService) -> None:
    super().__init__()
    self.db_service = db_service

def get_data(self):
    return self.db_service.get_data()  # Always available!

# Don't forget to enable auto-wiring:
context.enable_auto_wiring()
```

### Multi-Context Changes

- `ModuleContextImport` now requires keyword arguments: `ModuleContextImport(component_type=Type, from_context="name")`
- Auto-wiring is automatically enabled for contexts built with `ContextModuleBuilder`
- Dependencies are resolved at creation time, improving error detection

## License

Apache License 2.0 - see LICENSE file for details.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- 🐛 Reporting bugs
- ✨ Suggesting features  
- 💻 Contributing code
- 📖 Improving documentation
- 🧪 Writing tests

## Support

For issues and questions, please visit our [GitHub repository](https://github.com/krabhishek/opusgenie-di).