# Decorators API Reference

*Complete reference for OpusGenie DI decorators and configuration*

---

## Component Decorator

### @og_component

Primary decorator for marking classes as injectable components.

```python title="Component Decorator"
from opusgenie_di import og_component
from opusgenie_di._base.enums import ComponentScope

@og_component(
    scope: ComponentScope = ComponentScope.SINGLETON,
    auto_register: bool = False,
    tags: Dict[str, str] = None,
    name: str = None
)
def og_component(cls: Type[T] = None, **kwargs) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """
    Decorator for marking classes as injectable components.
    
    Args:
        scope: Component lifecycle scope (SINGLETON, TRANSIENT, SCOPED)
        auto_register: Whether to auto-register in global context
        tags: Metadata tags for component categorization
        name: Optional name for component registration
        
    Returns:
        Decorated class with component metadata attached
    """
```

**Usage Examples:**

```python
# Basic component
@og_component()
class CustomerService(BaseComponent):
    pass

# Singleton with auto-registration
@og_component(scope=ComponentScope.SINGLETON, auto_register=True)
class DatabaseService(BaseComponent):
    pass

# Tagged component
@og_component(
    tags={"domain": "payment", "layer": "service"},
    name="payment_processor"
)
class PaymentService(BaseComponent):
    pass

# Transient component
@og_component(scope=ComponentScope.TRANSIENT)
class RequestHandler(BaseComponent):
    pass
```

### Decorator Options

Configuration options for the component decorator.

```python title="Decorator Options"
from opusgenie_di._decorators.decorator_options import ComponentOptions

@dataclass
class ComponentOptions:
    """Configuration options for @og_component decorator"""
    
    scope: ComponentScope = ComponentScope.SINGLETON
    auto_register: bool = False
    tags: Dict[str, str] = field(default_factory=dict)
    name: Optional[str] = None
    
    def to_metadata(self, component_type: Type) -> ComponentMetadata:
        """Convert options to component metadata"""
        
    def validate(self) -> None:
        """Validate decorator options"""
```

**Advanced Configuration:**

```python
# Domain-specific service
@og_component(
    scope=ComponentScope.SINGLETON,
    tags={
        "domain": "banking",
        "subdomain": "loans",
        "layer": "application_service",
        "version": "2.1"
    }
)
class LoanApplicationService(BaseComponent):
    pass

# Infrastructure component
@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=True,
    tags={
        "layer": "infrastructure", 
        "type": "repository",
        "database": "postgresql"
    },
    name="customer_repository"
)
class PostgreSQLCustomerRepository(BaseComponent):
    pass
```

---

## Context Decorator

### @og_context

Decorator for defining context modules with providers, imports, and exports.

```python title="Context Decorator"
from opusgenie_di import og_context
from opusgenie_di._modules.import_declaration import ModuleContextImport

@og_context(
    name: str,
    providers: List[Type] = None,
    imports: List[ModuleContextImport] = None,
    exports: List[Type] = None,
    description: str = "",
    version: str = "1.0.0"
)
def og_context(cls: Type = None, **kwargs) -> Union[Type, Callable[[Type], Type]]:
    """
    Decorator for defining context modules.
    
    Args:
        name: Unique name for the context
        providers: List of component types provided by this context
        imports: List of imports from other contexts
        exports: List of component types exported to other contexts
        description: Human-readable context description
        version: Context version for compatibility tracking
        
    Returns:
        Decorated class with context metadata attached
    """
```

**Usage Examples:**

```python
# Basic context
@og_context(
    name="customer_management",
    providers=[CustomerService, CustomerRepository]
)
class CustomerManagementModule:
    pass

# Context with imports and exports
@og_context(
    name="payment_processing",
    providers=[PaymentService, PaymentRepository],
    imports=[
        ModuleContextImport(DatabaseService, from_context="infrastructure"),
        ModuleContextImport(CustomerService, from_context="customer_management")
    ],
    exports=[PaymentService],
    description="Payment processing and transaction management",
    version="2.1.0"
)
class PaymentProcessingModule:
    pass

# Infrastructure context
@og_context(
    name="infrastructure", 
    providers=[
        DatabaseService,
        RedisCache, 
        EventBus,
        ConfigService
    ],
    exports=[
        DatabaseService,
        RedisCache,
        EventBus,
        ConfigService
    ],
    description="Shared infrastructure services",
    version="1.5.0"
)
class InfrastructureModule:
    pass
```

### Context Options

Configuration for context module definitions.

```python title="Context Options"
from opusgenie_di._decorators.decorator_options import ContextOptions

@dataclass
class ContextOptions:
    """Configuration options for @og_context decorator"""
    
    name: str
    providers: List[Type] = field(default_factory=list)
    imports: List[ModuleContextImport] = field(default_factory=list)
    exports: List[Type] = field(default_factory=list)
    description: str = ""
    version: str = "1.0.0"
    
    def validate(self) -> None:
        """Validate context configuration"""
        
    def get_provider_types(self) -> Set[Type]:
        """Get all provider types"""
        
    def get_import_types(self) -> Set[Type]:
        """Get all imported types"""
        
    def get_export_types(self) -> Set[Type]:
        """Get all exported types"""
```

**Context Validation:**

```python
# The decorator validates context definitions
@og_context(
    name="invalid_context",
    providers=[ServiceA],
    exports=[ServiceB]  # ❌ Error: ServiceB not in providers
)
class InvalidModule:
    pass
# Raises: ContextValidationError("Cannot export ServiceB: not provided by context")

# Valid context
@og_context(
    name="valid_context",
    providers=[ServiceA, ServiceB],
    exports=[ServiceB]  # ✅ OK: ServiceB is provided
)
class ValidModule:
    pass
```

---

## Decorator Utilities

### Metadata Access

Utilities for accessing decorator metadata at runtime.

```python title="Metadata Utilities"
from opusgenie_di._decorators.decorator_utils import (
    get_component_metadata,
    get_context_metadata,
    is_component,
    is_context_module
)

def get_component_metadata(component_type: Type) -> Optional[ComponentMetadata]:
    """Get component metadata from decorated class"""

def get_context_metadata(module_type: Type) -> Optional[ContextMetadata]:
    """Get context metadata from decorated module"""

def is_component(obj: Any) -> bool:
    """Check if object is a decorated component"""

def is_context_module(obj: Any) -> bool:
    """Check if object is a decorated context module"""
```

**Usage Examples:**

```python
@og_component(scope=ComponentScope.SINGLETON, tags={"domain": "payment"})
class PaymentService(BaseComponent):
    pass

# Access metadata
metadata = get_component_metadata(PaymentService)
print(metadata.scope)  # ComponentScope.SINGLETON
print(metadata.tags)   # {"domain": "payment"}

# Check if decorated
if is_component(PaymentService):
    print("PaymentService is a component")

# Context metadata
@og_context(name="payment_context", version="2.0")
class PaymentModule:
    pass

context_meta = get_context_metadata(PaymentModule)
print(context_meta.name)     # "payment_context"
print(context_meta.version)  # "2.0"
```

### Component Registration

Utilities for programmatic component registration.

```python title="Registration Utilities"
from opusgenie_di._decorators.decorator_utils import (
    register_component_metadata,
    auto_register_components,
    scan_for_components
)

def register_component_metadata(
    component_type: Type,
    metadata: ComponentMetadata
) -> None:
    """Register component metadata programmatically"""

def auto_register_components(context: ContextInterface) -> None:
    """Auto-register components marked for auto-registration"""

def scan_for_components(
    module_or_package: Any,
    pattern: str = "**/*.py"
) -> List[Type]:
    """Scan module/package for decorated components"""
```

**Usage Examples:**

```python
# Programmatic registration
metadata = ComponentMetadata(
    component_type=CustomService,
    scope=ComponentScope.SINGLETON,
    tags={"layer": "service"},
    auto_register=True
)
register_component_metadata(CustomService, metadata)

# Auto-register all marked components
context = ContextImpl("my_context")
auto_register_components(context)

# Scan for components
import my_package
components = scan_for_components(my_package)
for component in components:
    print(f"Found component: {component.__name__}")
```

---

## Advanced Decorator Patterns

### Conditional Registration

Patterns for conditional component registration.

```python title="Conditional Registration"
import os
from opusgenie_di import og_component

# Environment-based registration
@og_component(auto_register=os.getenv("ENVIRONMENT") == "production")
class ProductionEmailService(BaseComponent):
    pass

@og_component(auto_register=os.getenv("ENVIRONMENT") == "development")
class MockEmailService(BaseComponent):
    pass

# Feature flag registration
@og_component(auto_register=bool(os.getenv("FEATURE_ADVANCED_ANALYTICS")))
class AdvancedAnalyticsService(BaseComponent):
    pass
```

### Tagged Component Queries

Using tags for component discovery and organization.

```python title="Tagged Component Discovery"
# Domain-tagged components
@og_component(tags={"domain": "banking", "subdomain": "loans"})
class LoanService(BaseComponent):
    pass

@og_component(tags={"domain": "banking", "subdomain": "accounts"})
class AccountService(BaseComponent):
    pass

@og_component(tags={"domain": "banking", "subdomain": "payments"})
class PaymentService(BaseComponent):
    pass

# Layer-tagged components
@og_component(tags={"layer": "repository", "database": "postgresql"})
class PostgreSQLRepository(BaseComponent):
    pass

@og_component(tags={"layer": "service", "type": "application"})
class ApplicationService(BaseComponent):
    pass

# Query by tags
def get_banking_services(context: ContextInterface) -> List[Type]:
    """Get all banking domain services"""
    return [
        component_type for component_type in context.get_registered_types()
        if get_component_metadata(component_type).has_tag("domain", "banking")
    ]

def get_repositories(context: ContextInterface) -> List[Type]:
    """Get all repository components"""
    return [
        component_type for component_type in context.get_registered_types()
        if get_component_metadata(component_type).has_tag("layer", "repository")
    ]
```

### Decorator Composition

Combining decorators for complex scenarios.

```python title="Decorator Composition"
from functools import wraps

# Custom decorator that adds component + additional behavior
def monitored_component(scope=ComponentScope.SINGLETON, **kwargs):
    """Decorator that combines @og_component with monitoring"""
    
    def decorator(cls):
        # Apply component decorator
        component_cls = og_component(scope=scope, **kwargs)(cls)
        
        # Add monitoring behavior
        original_init = component_cls.__init__
        
        @wraps(original_init)
        def monitored_init(self, *args, **kwargs):
            print(f"Creating monitored component: {cls.__name__}")
            original_init(self, *args, **kwargs)
            
        component_cls.__init__ = monitored_init
        return component_cls
    
    return decorator

# Usage
@monitored_component(tags={"monitored": "true"})
class MonitoredService(BaseComponent):
    pass
```

This decorator API provides powerful and flexible ways to configure components and contexts in OpusGenie DI, enabling clean separation of concerns and sophisticated dependency injection patterns.