# Modules API Reference

*Complete reference for context modules, imports, and the module builder*

---

## Context Module Builder

### ContextModuleBuilder

The primary tool for building and connecting multiple contexts into a cohesive application.

```python title="Context Module Builder"
from opusgenie_di._modules.builder import ContextModuleBuilder
from opusgenie_di._modules.import_declaration import ModuleContextImport

class ContextModuleBuilder:
    """Builder for creating and connecting multiple contexts"""
    
    def __init__(self) -> None:
        """Initialize the module builder"""
        
    async def build_contexts(
        self,
        *module_classes: Type,
        validate_imports: bool = True
    ) -> Dict[str, ContextInterface]:
        """
        Build all contexts from module classes.
        
        Args:
            module_classes: Context module classes decorated with @og_context
            validate_imports: Whether to validate import dependencies
            
        Returns:
            Dictionary mapping context names to context instances
        """
        
    async def build_single_context(
        self,
        module_class: Type,
        dependencies: Dict[str, ContextInterface] = None
    ) -> ContextInterface:
        """Build a single context with optional dependencies"""
        
    def validate_module_dependencies(
        self,
        module_classes: List[Type]
    ) -> List[str]:
        """Validate that all import dependencies can be satisfied"""
        
    def get_build_order(
        self,
        module_classes: List[Type]
    ) -> List[Type]:
        """Determine the correct build order for contexts"""
```

**Usage Examples:**

```python
# Define context modules
@og_context(
    name="infrastructure",
    providers=[DatabaseService, RedisCache],
    exports=[DatabaseService, RedisCache]
)
class InfrastructureModule:
    pass

@og_context(
    name="customer_management",
    imports=[
        ModuleContextImport(DatabaseService, from_context="infrastructure")
    ],
    providers=[CustomerService, CustomerRepository],
    exports=[CustomerService]
)
class CustomerModule:
    pass

@og_context(
    name="payment_processing",
    imports=[
        ModuleContextImport(DatabaseService, from_context="infrastructure"),
        ModuleContextImport(CustomerService, from_context="customer_management")
    ],
    providers=[PaymentService],
    exports=[PaymentService]
)
class PaymentModule:
    pass

# Build all contexts
builder = ContextModuleBuilder()
contexts = await builder.build_contexts(
    InfrastructureModule,
    CustomerModule,
    PaymentModule
)

# Access contexts
infrastructure = contexts["infrastructure"]
customer_context = contexts["customer_management"]
payment_context = contexts["payment_processing"]

# Use services
customer_service = customer_context.resolve(CustomerService)
payment_service = payment_context.resolve(PaymentService)
```

---

## Import Declarations

### ModuleContextImport

Specification for importing components from other contexts.

```python title="Module Context Import"
from opusgenie_di._modules.import_declaration import ModuleContextImport

@dataclass
class ModuleContextImport:
    """Declaration for importing a component from another context"""
    
    component_type: Type
    from_context: str
    alias: Optional[str] = None
    required: bool = True
    
    def __post_init__(self) -> None:
        """Validate import declaration"""
        
    @property
    def import_name(self) -> str:
        """Get the name used for importing (alias or component name)"""
        
    def validate_compatibility(
        self,
        export_metadata: ComponentMetadata
    ) -> bool:
        """Validate that import is compatible with export"""
```

**Usage Examples:**

```python
# Basic import
customer_import = ModuleContextImport(
    component_type=CustomerService,
    from_context="customer_management"
)

# Import with alias
db_import = ModuleContextImport(
    component_type=DatabaseService,
    from_context="infrastructure",
    alias="primary_db"
)

# Optional import (won't fail if not available)
optional_import = ModuleContextImport(
    component_type=CacheService,
    from_context="infrastructure",
    required=False
)

# Use in context definition
@og_context(
    name="payment_processing",
    imports=[customer_import, db_import, optional_import],
    providers=[PaymentService]
)
class PaymentModule:
    pass
```

### Import Resolution

How imports are resolved during context building.

```python title="Import Resolution Process"
# 1. Context builder analyzes all import declarations
imports = [
    ModuleContextImport(DatabaseService, from_context="infrastructure"),
    ModuleContextImport(CustomerService, from_context="customer_management")
]

# 2. Builder determines dependency order
build_order = builder.get_build_order([
    InfrastructureModule,    # Built first (no dependencies)
    CustomerModule,          # Built second (depends on infrastructure)  
    PaymentModule           # Built last (depends on infrastructure + customer)
])

# 3. For each context, imports are resolved from already-built contexts
for module_class in build_order:
    context = await builder.build_single_context(
        module_class,
        dependencies=already_built_contexts
    )
    # Imports are automatically wired during build
```

---

## Provider Configuration

### Provider Configuration and Normalization

How providers are configured and normalized within contexts.

```python title="Provider Configuration"
from opusgenie_di._modules.provider_config import (
    ProviderConfig,
    normalize_providers,
    validate_provider_exports
)

@dataclass
class ProviderConfig:
    """Configuration for a provider within a context"""
    
    component_type: Type
    implementation_type: Optional[Type] = None
    scope: Optional[ComponentScope] = None
    name: Optional[str] = None
    
    @classmethod
    def from_type(cls, component_type: Type) -> 'ProviderConfig':
        """Create provider config from component type"""
        
    def to_registration_args(self) -> Dict[str, Any]:
        """Convert to container registration arguments"""

def normalize_providers(
    providers: List[Union[Type, ProviderConfig]]
) -> List[ProviderConfig]:
    """Normalize mixed provider specifications to ProviderConfig objects"""

def validate_provider_exports(
    providers: List[ProviderConfig],
    exports: List[Type]
) -> List[str]:
    """Validate that all exports are provided by the context"""
```

**Usage Examples:**

```python
# Different ways to specify providers

# 1. Simple type specification (uses component metadata)
@og_context(
    name="simple_context",
    providers=[CustomerService, CustomerRepository]  # Types only
)
class SimpleModule:
    pass

# 2. Mixed provider specifications
@og_context(
    name="complex_context",
    providers=[
        CustomerService,  # Use component metadata
        ProviderConfig(  # Custom configuration
            component_type=DatabaseService,
            implementation_type=PostgreSQLService,
            scope=ComponentScope.SINGLETON,
            name="primary_database"
        ),
        ProviderConfig(  # Interface implementation
            component_type=EmailService,
            implementation_type=SMTPEmailService
        )
    ]
)
class ComplexModule:
    pass

# 3. Programmatic provider configuration
providers = [
    ProviderConfig.from_type(CustomerService),
    ProviderConfig(
        component_type=PaymentGateway,
        implementation_type=StripeGateway if is_production() else MockGateway
    )
]

@og_context(
    name="dynamic_context",
    providers=providers
)
class DynamicModule:
    pass
```

---

## Context Lifecycle

### Context Initialization and Cleanup

Managing the lifecycle of contexts and their components.

```python title="Context Lifecycle Management"
class ContextInterface:
    """Context lifecycle methods"""
    
    async def initialize_all(self) -> None:
        """Initialize all components in dependency order"""
        
    async def cleanup_all(self) -> None:
        """Cleanup all components in reverse dependency order"""
        
    def get_initialization_order(self) -> List[Type]:
        """Get component initialization order based on dependencies"""
        
    def get_cleanup_order(self) -> List[Type]:
        """Get component cleanup order (reverse of initialization)"""

# Builder provides lifecycle management
builder = ContextModuleBuilder()

# Build contexts (automatically initializes components)
contexts = await builder.build_contexts(
    InfrastructureModule,
    CustomerModule,
    PaymentModule
)

# Manual lifecycle control
customer_context = contexts["customer_management"]

# Get lifecycle order
init_order = customer_context.get_initialization_order()
print(f"Initialization order: {[t.__name__ for t in init_order]}")

# Manual cleanup (usually done automatically)
await customer_context.cleanup_all()
```

### Dependency Resolution Order

How the builder determines the correct order for context building and component initialization.

```python title="Dependency Order Resolution"
# Example dependency graph:
# InfrastructureModule: no dependencies
# CustomerModule: depends on InfrastructureModule (imports DatabaseService)
# PaymentModule: depends on InfrastructureModule + CustomerModule
# NotificationModule: depends on CustomerModule

modules = [
    PaymentModule,        # Has dependencies
    InfrastructureModule, # No dependencies  
    CustomerModule,       # Has dependencies
    NotificationModule    # Has dependencies
]

# Builder determines correct order
builder = ContextModuleBuilder()
build_order = builder.get_build_order(modules)

# Result: [InfrastructureModule, CustomerModule, PaymentModule, NotificationModule]
print([m.__name__ for m in build_order])

# Within each context, component initialization order is also determined
customer_context = await builder.build_single_context(CustomerModule)
component_order = customer_context.get_initialization_order()

# Components with fewer dependencies initialize first
# Example: [DatabaseService, CustomerRepository, CustomerService]
```

---

## Module Metadata

### Context Metadata Management

Metadata attached to context modules and how it's used during building.

```python title="Context Metadata"
from opusgenie_di._registry.module_metadata import (
    ContextMetadata,
    get_context_metadata,
    validate_context_metadata
)

@dataclass
class ContextMetadata:
    """Metadata for context modules"""
    
    name: str
    providers: List[Type]
    imports: List[ModuleContextImport]
    exports: List[Type]
    description: str
    version: str
    module_class: Type
    
    def get_import_dependencies(self) -> Set[str]:
        """Get names of contexts this module depends on"""
        
    def get_exported_types(self) -> Set[Type]:
        """Get all types exported by this context"""
        
    def validate_exports(self) -> List[str]:
        """Validate that all exports are provided"""
        
    def is_compatible_with(self, other: 'ContextMetadata') -> bool:
        """Check compatibility with another context"""

# Access metadata from decorated modules
@og_context(
    name="payment_processing",
    providers=[PaymentService, PaymentRepository],
    exports=[PaymentService],
    description="Payment processing context",
    version="2.1.0"
)
class PaymentModule:
    pass

metadata = get_context_metadata(PaymentModule)
print(f"Context: {metadata.name}")
print(f"Version: {metadata.version}")
print(f"Exports: {[t.__name__ for t in metadata.exports]}")

# Validation
errors = validate_context_metadata(metadata)
if errors:
    print(f"Validation errors: {errors}")
```

---

## Advanced Module Patterns

### Dynamic Context Building

Building contexts dynamically based on configuration or runtime conditions.

```python title="Dynamic Context Building"
def create_database_context(database_type: str) -> Type:
    """Create database context based on configuration"""
    
    if database_type == "postgresql":
        providers = [PostgreSQLService, PostgreSQLRepository]
    elif database_type == "mysql":
        providers = [MySQLService, MySQLRepository]
    else:
        raise ValueError(f"Unsupported database: {database_type}")
    
    @og_context(
        name="database",
        providers=providers,
        exports=[DatabaseService, Repository]
    )
    class DatabaseModule:
        pass
    
    return DatabaseModule

# Usage
db_type = os.getenv("DATABASE_TYPE", "postgresql")
DatabaseModule = create_database_context(db_type)

builder = ContextModuleBuilder()
contexts = await builder.build_contexts(DatabaseModule, ApplicationModule)
```

### Context Composition

Composing larger applications from smaller, focused contexts.

```python title="Context Composition"
# Microservice-style context composition
def create_banking_application():
    """Compose full banking application from contexts"""
    
    # Core infrastructure
    infrastructure_contexts = [
        InfrastructureModule,
        DatabaseModule,
        CacheModule,
        EventBusModule
    ]
    
    # Business domains
    domain_contexts = [
        CustomerManagementModule,
        AccountManagementModule,
        PaymentProcessingModule,
        LoanProcessingModule
    ]
    
    # Cross-cutting concerns
    support_contexts = [
        ComplianceModule,
        NotificationModule,
        MonitoringModule,
        SecurityModule
    ]
    
    all_contexts = infrastructure_contexts + domain_contexts + support_contexts
    
    return all_contexts

# Build complete application
banking_modules = create_banking_application()
builder = ContextModuleBuilder()

# Validate before building
validation_errors = builder.validate_module_dependencies(banking_modules)
if validation_errors:
    raise Exception(f"Module validation failed: {validation_errors}")

# Build application
app_contexts = await builder.build_contexts(*banking_modules)

# Application is now ready to use
customer_service = app_contexts["customer_management"].resolve(CustomerService)
payment_service = app_contexts["payment_processing"].resolve(PaymentService)
```

This modules API enables sophisticated application composition through well-defined context boundaries, making it easy to build maintainable, scalable applications with clear separation of concerns.