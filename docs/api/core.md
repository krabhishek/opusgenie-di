# Core API Reference

*Complete reference for OpusGenie DI core components*

---

## Container API

### ContainerInterface

The core dependency injection container interface that manages component instances and their lifecycle.

```python title="Container Interface"
from typing import TypeVar, Type, Optional, Dict, Any
from opusgenie_di._core.container_interface import ContainerInterface

T = TypeVar('T')

class ContainerInterface:
    """Core DI container interface"""
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance by type"""
        
    def resolve_by_name(self, name: str) -> Any:
        """Resolve a service instance by name"""
        
    def register(
        self, 
        service_type: Type[T], 
        implementation: Type[T] = None,
        scope: ComponentScope = ComponentScope.SINGLETON,
        name: str = None
    ) -> None:
        """Register a service with the container"""
        
    def is_registered(self, service_type: Type[T]) -> bool:
        """Check if a service type is registered"""
        
    def get_registered_types(self) -> List[Type]:
        """Get all registered service types"""
```

**Usage Example:**
```python
# Resolve a service
customer_service = container.resolve(CustomerService)

# Register a service
container.register(DatabaseService, PostgreSQLService, scope=ComponentScope.SINGLETON)
```

### ContextInterface

Multi-context DI container that supports imports and exports between contexts.

```python title="Context Interface"
from opusgenie_di._core.context_interface import ContextInterface

class ContextInterface(ContainerInterface):
    """Multi-context DI container interface"""
    
    @property
    def name(self) -> str:
        """Context name"""
        
    @property
    def exports(self) -> List[Type]:
        """Types exported by this context"""
        
    def import_from_context(
        self, 
        context: 'ContextInterface', 
        service_type: Type[T],
        alias: str = None
    ) -> None:
        """Import a service from another context"""
        
    def can_export(self, service_type: Type[T]) -> bool:
        """Check if a type can be exported"""
        
    def get_exported_instance(self, service_type: Type[T]) -> T:
        """Get an exported instance"""
```

**Usage Example:**
```python
# Create contexts
customer_context = ContextImpl("customer_management")
payment_context = ContextImpl("payment_processing")

# Import service from another context
payment_context.import_from_context(
    customer_context, 
    CustomerService
)

# Resolve imported service
customer_service = payment_context.resolve(CustomerService)
```

---

## Component API

### BaseComponent

Base class for all injectable components with lifecycle management.

```python title="BaseComponent"
from opusgenie_di._base import BaseComponent

class BaseComponent:
    """Base class for all injectable components"""
    
    def __init__(self) -> None:
        """Initialize component"""
        
    async def initialize(self) -> None:
        """Initialize component (called after dependency injection)"""
        
    async def cleanup(self) -> None:
        """Cleanup component resources"""
        
    @property
    def is_initialized(self) -> bool:
        """Check if component is initialized"""
        
    @property
    def component_id(self) -> str:
        """Unique component identifier"""
```

**Usage Example:**
```python
@og_component()
class CustomerService(BaseComponent):
    
    def __init__(self, db: DatabaseService) -> None:
        super().__init__()
        self.db = db
    
    async def initialize(self) -> None:
        await super().initialize()
        await self.db.connect()
        self.logger.info("Customer service initialized")
    
    async def cleanup(self) -> None:
        await self.db.disconnect()
        await super().cleanup()
```

### Component Metadata

Component registration and configuration metadata.

```python title="Component Metadata"
from opusgenie_di._base.metadata import ComponentMetadata
from opusgenie_di._base.enums import ComponentScope

@dataclass
class ComponentMetadata:
    """Metadata for registered components"""
    
    component_type: Type
    scope: ComponentScope
    tags: Dict[str, str]
    dependencies: List[Type]
    auto_register: bool
    name: Optional[str] = None
    
    @property
    def qualified_name(self) -> str:
        """Fully qualified component name"""
        
    def has_tag(self, key: str, value: str = None) -> bool:
        """Check if component has specific tag"""
```

---

## Scope Management

### Component Scopes

Component lifecycle and instance management scopes.

```python title="Component Scopes"
from opusgenie_di._base.enums import ComponentScope

class ComponentScope(Enum):
    """Component instance scopes"""
    
    SINGLETON = "singleton"    # One instance per context
    TRANSIENT = "transient"    # New instance each time
    SCOPED = "scoped"         # One instance per scope
```

**Scope Behaviors:**

- **SINGLETON**: One instance created and reused throughout the context lifetime
- **TRANSIENT**: New instance created for every resolution request
- **SCOPED**: One instance per defined scope (useful for request-scoped services)

**Usage Example:**
```python
@og_component(scope=ComponentScope.SINGLETON)
class DatabaseService(BaseComponent):
    """Singleton database service"""
    pass

@og_component(scope=ComponentScope.TRANSIENT)
class RequestHandler(BaseComponent):
    """New instance per request"""
    pass
```

### Scope Manager

Manages component scopes and lifecycles.

```python title="Scope Manager"
from opusgenie_di._core.scope_interface import ScopeManager

class ScopeManager:
    """Manages component scopes and lifecycles"""
    
    def create_instance(
        self, 
        component_type: Type[T], 
        metadata: ComponentMetadata
    ) -> T:
        """Create component instance based on scope"""
        
    def get_or_create_singleton(self, component_type: Type[T]) -> T:
        """Get or create singleton instance"""
        
    def create_transient(self, component_type: Type[T]) -> T:
        """Create new transient instance"""
        
    def enter_scope(self, scope_name: str) -> None:
        """Enter a new scope"""
        
    def exit_scope(self, scope_name: str) -> None:
        """Exit current scope"""
```

---

## Global Context

### Global Registration

Simple global context for basic use cases.

```python title="Global Context"
from opusgenie_di._core.global_context import get_global_context, register_component

# Get global context
context = get_global_context()

# Register component globally
@og_component(auto_register=True)
class GlobalService(BaseComponent):
    """Automatically registered to global context"""
    pass

# Manual registration
register_component(DatabaseService, PostgreSQLService)

# Resolve from global context
service = context.resolve(GlobalService)
```

**Functions:**
```python
def get_global_context() -> ContextInterface:
    """Get the global context instance"""

def register_component(
    service_type: Type[T], 
    implementation: Type[T] = None,
    scope: ComponentScope = ComponentScope.SINGLETON
) -> None:
    """Register component in global context"""

def resolve_component(service_type: Type[T]) -> T:
    """Resolve component from global context"""
```

---

## Error Handling

### Core Exceptions

Exception hierarchy for dependency injection errors.

```python title="Core Exceptions"
from opusgenie_di._core.exceptions import (
    DependencyInjectionError,
    ComponentNotFoundError,
    CircularDependencyError,
    ComponentRegistrationError,
    ContextImportError
)

class DependencyInjectionError(Exception):
    """Base exception for DI-related errors"""
    pass

class ComponentNotFoundError(DependencyInjectionError):
    """Component type not found in container"""
    
    def __init__(self, component_type: Type, context_name: str = None):
        self.component_type = component_type
        self.context_name = context_name
        super().__init__(f"Component {component_type.__name__} not found in context {context_name}")

class CircularDependencyError(DependencyInjectionError):
    """Circular dependency detected during resolution"""
    
    def __init__(self, dependency_chain: List[Type]):
        self.dependency_chain = dependency_chain
        chain_names = " -> ".join([t.__name__ for t in dependency_chain])
        super().__init__(f"Circular dependency detected: {chain_names}")

class ComponentRegistrationError(DependencyInjectionError):
    """Error during component registration"""
    pass

class ContextImportError(DependencyInjectionError):
    """Error importing component from another context"""
    
    def __init__(self, component_type: Type, source_context: str, target_context: str):
        super().__init__(
            f"Cannot import {component_type.__name__} from {source_context} to {target_context}"
        )
```

**Usage Example:**
```python
try:
    service = container.resolve(NonExistentService)
except ComponentNotFoundError as e:
    logger.error(f"Service not found: {e.component_type.__name__}")
    
try:
    # This would create A -> B -> A circular dependency
    container.resolve(ComponentA)
except CircularDependencyError as e:
    logger.error(f"Circular dependency: {' -> '.join([t.__name__ for t in e.dependency_chain])}")
```

---

## Type System

### Protocols

Type protocols for framework contracts and interfaces.

```python title="Framework Protocols"
from typing import Protocol, runtime_checkable
from opusgenie_di._base.protocols import Injectable, Configurable

@runtime_checkable
class Injectable(Protocol):
    """Protocol for injectable components"""
    
    def __init__(self, *args, **kwargs) -> None:
        """Component initialization"""
        ...

@runtime_checkable
class Configurable(Protocol):
    """Protocol for configurable components"""
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure component with settings"""
        ...

@runtime_checkable  
class AsyncLifecycle(Protocol):
    """Protocol for components with async lifecycle"""
    
    async def initialize(self) -> None:
        """Async initialization"""
        ...
        
    async def cleanup(self) -> None:
        """Async cleanup"""
        ...
```

These protocols enable type checking and ensure components implement required interfaces:

```python
def process_injectable(component: Injectable) -> None:
    """Function that works with any injectable component"""
    # Type checker ensures component has proper __init__
    pass

# Usage with type checking
@og_component()
class MyService(BaseComponent):  # BaseComponent implements Injectable
    pass

process_injectable(MyService)  # ✅ Type safe
```

This core API provides the foundation for all dependency injection operations in OpusGenie DI, enabling type-safe component registration, resolution, and lifecycle management across multiple contexts.