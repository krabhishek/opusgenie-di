"""Core dependency injection components."""

from .container_impl import Container
from .container_interface import ContainerInterface
from .context_impl import Context, ImportDeclaration, ImportManager
from .context_interface import ContextInterface
from .event_loop_manager import (
    EventLoopManager,
    get_event_loop_manager,
    run_async_safely,
    schedule_async_cleanup,
)
from .exceptions import (
    CircularDependencyError,
    ComponentRegistrationError,
    ComponentResolutionError,
    ConfigurationError,
    ContainerError,
    ContextError,
    DIError,
    ImportError,
    LifecycleError,
    ModuleError,
    ProviderError,
    ScopeError,
    ValidationError,
)
from .global_context import (
    GlobalContext,
    get_global_context,
    get_global_context_summary,
    is_global_context_initialized,
    register_global_component,
    reset_global_context,
    resolve_global_component,
    resolve_global_component_async,
)
from .provider_interface import ComponentProvider, ProviderInterface
from .scope_impl import ScopeManager
from .scope_interface import ScopeManagerInterface

__all__ = [
    # Core interfaces
    "ContainerInterface",
    "ContextInterface",
    "ScopeManagerInterface",
    "ProviderInterface",
    # Core implementations
    "Container",
    "Context",
    "ScopeManager",
    "ComponentProvider",
    # Event loop management
    "EventLoopManager",
    "get_event_loop_manager",
    "run_async_safely",
    "schedule_async_cleanup",
    # Import system
    "ImportDeclaration",
    "ImportManager",
    # Global context
    "GlobalContext",
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
]
