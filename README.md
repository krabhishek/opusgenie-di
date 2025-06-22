# OpusGenie Dependency Injection

A powerful, multi-context dependency injection framework for Python that provides Angular-style dependency injection with support for multiple isolated contexts, cross-context imports, declarative module definitions, and comprehensive lifecycle management.

## Features

- **Multi-Context Architecture**: Create isolated dependency contexts with clear boundaries
- **Declarative Configuration**: Use `@og_component` and `@og_context` decorators for clean setup
- **Cross-Context Imports**: Import dependencies between contexts safely
- **Component Scopes**: Singleton, Transient, and Scoped lifecycles
- **Type Safety**: Full type safety with Python type hints and runtime validation
- **Event System**: Built-in event hooks for monitoring and extension
- **Framework Agnostic**: No dependencies on specific frameworks
- **Testing Support**: Comprehensive testing utilities and mocks

## Installation

```bash
pip install opusgenie-di
```

## Quick Start

### Basic Usage

```python
from opusgenie_di import og_component, BaseComponent, ComponentScope, get_global_context

# Define a simple component
@og_component(scope=ComponentScope.SINGLETON)
class DatabaseService(BaseComponent):
    def get_data(self) -> str:
        return "Data from database"

# Define a component with dependencies
@og_component(scope=ComponentScope.SINGLETON)
class UserService(BaseComponent):
    def __init__(self, db_service: DatabaseService | None = None) -> None:
        super().__init__()
        self.__dict__["db_service"] = db_service

    def get_user(self, user_id: str) -> dict[str, str]:
        db_service = self.__dict__.get("db_service")
        if db_service:
            data = db_service.get_data()
            return {"id": user_id, "name": f"User_{user_id}", "source": data}
        return {"id": user_id, "name": f"User_{user_id}", "source": "unknown"}

# Use the global context
context = get_global_context()
user_service = context.resolve(UserService)
user_data = user_service.get_user("123")
```

### Multi-Context Architecture

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

# Business layer components
@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class BusinessService(BaseComponent):
    def __init__(self, db_repo: DatabaseRepository | None = None) -> None:
        super().__init__()
        self.__dict__["db_repo"] = db_repo

    def process_data(self) -> dict[str, str]:
        db_repo = self.__dict__.get("db_repo")
        return {"status": "processed", "data": db_repo.get_data() if db_repo else ""}

# Define module contexts
@og_context(
    name="infrastructure_context",
    imports=[],
    exports=[DatabaseRepository],
    providers=[DatabaseRepository],
)
class InfrastructureModule:
    pass

@og_context(
    name="business_context",
    imports=[
        ModuleContextImport(DatabaseRepository, from_context="infrastructure_context"),
    ],
    exports=[BusinessService],
    providers=[BusinessService],
)
class BusinessModule:
    pass

# Build and use contexts
async def main():
    builder = ContextModuleBuilder()
    contexts = await builder.build_contexts(InfrastructureModule, BusinessModule)
    
    business_context = contexts["business_context"]
    business_service = business_context.resolve(BusinessService)
    result = business_service.process_data()
    print(result)
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

### Async Support

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
        self.__dict__["provider"] = provider
```

## Performance Considerations

- **Lazy Loading**: Components are created only when needed
- **Caching**: Singleton instances are cached for performance
- **Minimal Overhead**: Built on top of proven `dependency-injector` library
- **Memory Efficient**: Contexts can be disposed when no longer needed

## Development and Contributing

### Setup Development Environment

```bash
git clone <repository-url>
cd opusgenie-di
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy opusgenie_di/
```

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

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please visit our [GitHub repository](https://github.com/your-org/opusgenie-di).