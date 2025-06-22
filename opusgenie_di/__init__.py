"""
OpusGenie Dependency Injection Framework

A powerful, multi-context dependency injection framework for Python that provides
Angular-style dependency injection with support for multiple isolated contexts,
cross-context imports, declarative module definitions, and comprehensive
lifecycle management.

Key Features:
- Multi-Context Architecture: Create isolated dependency contexts
- Declarative Configuration: Use @og_component and @og_context decorators
- Cross-Context Imports: Import dependencies between contexts
- Component Scopes: Singleton, Transient, and Scoped lifecycles
- Type Safety: Full type safety with Python type hints
- Event System: Built-in event hooks for monitoring and extension
- Framework Agnostic: No dependencies on specific frameworks

Example Usage:

    # Basic component registration
    from opusgenie_di import og_component, BaseComponent, ComponentScope

    @og_component(scope=ComponentScope.SINGLETON)
    class DatabaseService(BaseComponent):
        def get_data(self): return "data"

    # Multi-context module system
    from opusgenie_di import og_context, ModuleContextImport, ContextModuleBuilder

    @og_context(
        name="business_context",
        imports=[ModuleContextImport(DatabaseService, from_context="infrastructure")],
        providers=[BusinessService]
    )
    class BusinessModule: pass

    # Build and use contexts
    builder = ContextModuleBuilder()
    contexts = await builder.build_contexts(InfrastructureModule, BusinessModule)
"""

# Core base components
from ._base import (
    BaseComponent,
    ComponentLayer,
    ComponentMetadata,
    ComponentScope,
    LifecycleStage,
    RegistrationStrategy,
)

# Core DI system
from ._core import (
    CircularDependencyError,
    ComponentRegistrationError,
    ComponentResolutionError,
    ConfigurationError,
    Container,
    ContainerError,
    Context,
    ContextError,
    DIError,
    GlobalContext,
    ImportDeclaration,
    ImportError,
    LifecycleError,
    ModuleError,
    ProviderError,
    ScopeError,
    ValidationError,
    get_global_context,
    get_global_context_summary,
    is_global_context_initialized,
    register_global_component,
    reset_global_context,
    resolve_global_component,
    resolve_global_component_async,
)

# Decorators
from ._decorators import (
    ComponentOptions,
    ContextOptions,
    get_all_context_modules,
    get_component_metadata,
    get_component_options,
    get_enhanced_tags,
    get_module_metadata,
    get_module_options,
    is_context_module,
    is_og_component,
    og_component,
    og_context,
    register_component_manually,
    validate_all_module_dependencies,
)

# Hook system
from ._hooks import (
    EventHook,
    HookFunction,
    LifecycleHook,
    LifecycleHookFunction,
    clear_all_hooks,
    emit_event,
    emit_lifecycle_event,
    get_hooks_summary,
    register_hook,
    register_lifecycle_hook,
    set_hooks_enabled,
)

# Module system
from ._modules import (
    ContextModuleBuilder,
    ModuleContextImport,
    ProviderConfig,
)

# Registry
from ._registry import (
    ModuleMetadata,
    get_global_registry,
)

# Testing utilities
from ._testing import (
    MockComponent,
    TestEventCollector,
    create_test_context,
    reset_global_state,
)

# Version information
__version__ = "0.1.4"
__author__ = "Abhishek Pathak"

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Core base components
    "BaseComponent",
    "ComponentScope",
    "ComponentLayer",
    "ComponentMetadata",
    "LifecycleStage",
    "RegistrationStrategy",
    # Core DI system
    "Context",
    "Container",
    "GlobalContext",
    "ImportDeclaration",
    "get_global_context",
    "register_global_component",
    "resolve_global_component",
    "resolve_global_component_async",
    "reset_global_context",
    "get_global_context_summary",
    "is_global_context_initialized",
    # Exceptions
    "DIError",
    "ContainerError",
    "ContextError",
    "ComponentRegistrationError",
    "ComponentResolutionError",
    "CircularDependencyError",
    "ScopeError",
    "ProviderError",
    "ImportError",
    "ModuleError",
    "LifecycleError",
    "ValidationError",
    "ConfigurationError",
    # Decorators
    "og_component",
    "og_context",
    "ComponentOptions",
    "ContextOptions",
    "get_component_options",
    "get_component_metadata",
    "get_enhanced_tags",
    "is_og_component",
    "register_component_manually",
    "get_module_metadata",
    "get_module_options",
    "is_context_module",
    "get_all_context_modules",
    "validate_all_module_dependencies",
    # Module system
    "ContextModuleBuilder",
    "ModuleContextImport",
    "ProviderConfig",
    "ModuleMetadata",
    "get_global_registry",
    # Hook system
    "EventHook",
    "LifecycleHook",
    "HookFunction",
    "LifecycleHookFunction",
    "register_hook",
    "register_lifecycle_hook",
    "emit_event",
    "emit_lifecycle_event",
    "clear_all_hooks",
    "set_hooks_enabled",
    "get_hooks_summary",
    # Testing utilities
    "MockComponent",
    "TestEventCollector",
    "create_test_context",
    "reset_global_state",
]
