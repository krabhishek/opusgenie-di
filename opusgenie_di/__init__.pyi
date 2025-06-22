# Core base components - with explicit re-export
from ._base import (
    BaseComponent as BaseComponent,
)
from ._base import (
    ComponentLayer as ComponentLayer,
)
from ._base import (
    ComponentMetadata as ComponentMetadata,
)
from ._base import (
    ComponentScope as ComponentScope,
)
from ._base import (
    LifecycleStage as LifecycleStage,
)
from ._base import (
    RegistrationStrategy as RegistrationStrategy,
)

# Core DI system
from ._core import (
    CircularDependencyError as CircularDependencyError,
)
from ._core import (
    ComponentRegistrationError as ComponentRegistrationError,
)
from ._core import (
    ComponentResolutionError as ComponentResolutionError,
)
from ._core import (
    ConfigurationError as ConfigurationError,
)
from ._core import (
    Container as Container,
)
from ._core import (
    ContainerError as ContainerError,
)
from ._core import (
    Context as Context,
)
from ._core import (
    ContextError as ContextError,
)
from ._core import (
    DIError as DIError,
)
from ._core import (
    GlobalContext as GlobalContext,
)
from ._core import (
    ImportDeclaration as ImportDeclaration,
)
from ._core import (
    ImportError as ImportError,
)
from ._core import (
    LifecycleError as LifecycleError,
)
from ._core import (
    ModuleError as ModuleError,
)
from ._core import (
    ProviderError as ProviderError,
)
from ._core import (
    ScopeError as ScopeError,
)
from ._core import (
    ValidationError as ValidationError,
)
from ._core import (
    get_global_context as get_global_context,
)
from ._core import (
    get_global_context_summary as get_global_context_summary,
)
from ._core import (
    is_global_context_initialized as is_global_context_initialized,
)
from ._core import (
    register_global_component as register_global_component,
)
from ._core import (
    reset_global_context as reset_global_context,
)
from ._core import (
    resolve_global_component as resolve_global_component,
)
from ._core import (
    resolve_global_component_async as resolve_global_component_async,
)

# Decorators
from ._decorators import (
    ComponentOptions as ComponentOptions,
)
from ._decorators import (
    ContextOptions as ContextOptions,
)
from ._decorators import (
    get_all_context_modules as get_all_context_modules,
)
from ._decorators import (
    get_component_metadata as get_component_metadata,
)
from ._decorators import (
    get_component_options as get_component_options,
)
from ._decorators import (
    get_enhanced_tags as get_enhanced_tags,
)
from ._decorators import (
    get_module_metadata as get_module_metadata,
)
from ._decorators import (
    get_module_options as get_module_options,
)
from ._decorators import (
    is_context_module as is_context_module,
)
from ._decorators import (
    is_og_component as is_og_component,
)
from ._decorators import (
    og_component as og_component,
)
from ._decorators import (
    og_context as og_context,
)
from ._decorators import (
    register_component_manually as register_component_manually,
)
from ._decorators import (
    validate_all_module_dependencies as validate_all_module_dependencies,
)

# Hook system
from ._hooks import (
    EventHook as EventHook,
)
from ._hooks import (
    HookFunction as HookFunction,
)
from ._hooks import (
    LifecycleHook as LifecycleHook,
)
from ._hooks import (
    LifecycleHookFunction as LifecycleHookFunction,
)
from ._hooks import (
    clear_all_hooks as clear_all_hooks,
)
from ._hooks import (
    emit_event as emit_event,
)
from ._hooks import (
    emit_lifecycle_event as emit_lifecycle_event,
)
from ._hooks import (
    get_hooks_summary as get_hooks_summary,
)
from ._hooks import (
    register_hook as register_hook,
)
from ._hooks import (
    register_lifecycle_hook as register_lifecycle_hook,
)
from ._hooks import (
    set_hooks_enabled as set_hooks_enabled,
)

# Module system
from ._modules import (
    ContextModuleBuilder as ContextModuleBuilder,
)
from ._modules import (
    ModuleContextImport as ModuleContextImport,
)
from ._modules import (
    ProviderConfig as ProviderConfig,
)

# Registry
from ._registry import (
    ModuleMetadata as ModuleMetadata,
)
from ._registry import (
    get_global_registry as get_global_registry,
)

# Testing utilities
from ._testing import (
    MockComponent as MockComponent,
)
from ._testing import (
    TestEventCollector as TestEventCollector,
)
from ._testing import (
    create_test_context as create_test_context,
)
from ._testing import (
    reset_global_state as reset_global_state,
)

__version__: str
__author__: str

__all__ = [
    "__version__",
    "__author__",
    "BaseComponent",
    "ComponentScope",
    "ComponentLayer",
    "ComponentMetadata",
    "LifecycleStage",
    "RegistrationStrategy",
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
    "ContextModuleBuilder",
    "ModuleContextImport",
    "ProviderConfig",
    "ModuleMetadata",
    "get_global_registry",
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
    "MockComponent",
    "TestEventCollector",
    "create_test_context",
    "reset_global_state",
]
