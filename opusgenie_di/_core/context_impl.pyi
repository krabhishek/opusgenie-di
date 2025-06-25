from .._base import ComponentScope as ComponentScope
from .._hooks import EventHook as EventHook, emit_event as emit_event
from .._utils import get_logger as get_logger, log_context_creation as log_context_creation, log_error as log_error, log_import_resolution as log_import_resolution, validate_context_name as validate_context_name
from .container_impl import Container as Container
from .context_interface import ContextInterface as ContextInterface
from .exceptions import ComponentResolutionError as ComponentResolutionError, ContextError as ContextError, ImportError as ImportError
from _typeshed import Incomplete
from typing import Any, TypeVar
from weakref import WeakSet

T = TypeVar('T')
TInterface = TypeVar('TInterface')
logger: Incomplete

class ImportDeclaration:
    """
    Declaration for importing a component from another context.

    This represents a cross-context dependency that needs to be resolved
    from a different context than the one making the request.
    """
    component_type: Incomplete
    source_context: Incomplete
    name: Incomplete
    alias: Incomplete
    def __init__(self, component_type: type, source_context: str, name: str | None = None, alias: str | None = None) -> None:
        """
        Initialize the import declaration.

        Args:
            component_type: Type of component to import
            source_context: Name of the context to import from
            name: Optional specific name of the component
            alias: Optional alias to use in the importing context
        """
    def get_provider_name(self) -> str:
        """Get the provider name for this import."""
    def get_import_key(self) -> str:
        """Get a unique key for this import."""
    def __repr__(self) -> str: ...

class ImportManager:
    """
    Manager for handling cross-context imports.

    Manages the resolution of components from other contexts,
    maintaining references to source contexts and handling
    import validation and resolution.
    """
    _context: Incomplete
    _imports: dict[str, ImportDeclaration]
    _source_contexts: dict[str, Context]
    def __init__(self, context: Context) -> None:
        """
        Initialize the import manager.

        Args:
            context: The context this manager belongs to
        """
    def add_import(self, declaration: ImportDeclaration) -> None:
        """
        Add an import declaration.

        Args:
            declaration: Import declaration to add
        """
    def register_source_context(self, context_name: str, context: Context) -> None:
        """
        Register a source context for imports.

        Args:
            context_name: Name of the source context
            context: The source context instance
        """
    def resolve_import(self, component_type: type[T], name: str | None = None) -> T:
        """
        Resolve a component from imports.

        Args:
            component_type: Type of component to resolve
            name: Optional component name

        Returns:
            Resolved component instance

        Raises:
            ImportError: If import cannot be resolved
        """
    def get_imports(self) -> list[ImportDeclaration]:
        """Get all import declarations."""
    def get_import_count(self) -> int:
        """Get the number of imports."""
    def clear_imports(self) -> None:
        """Clear all imports."""

class Context(ContextInterface):
    """
    Context implementation for multi-container dependency injection.

    Provides Angular-like DI functionality with support for multiple
    isolated contexts, hierarchical relationships, and cross-context imports.
    """
    _name: Incomplete
    _parent: Incomplete
    _auto_wire: Incomplete
    _lock: Incomplete
    _child_contexts: WeakSet[Context]
    _container: Container[Any]
    _import_manager: Incomplete
    def __init__(self, name: str, parent: Context | None = None, auto_wire: bool = True) -> None:
        """
        Initialize the context.

        Args:
            name: Unique name for this context
            parent: Optional parent context for hierarchical DI
            auto_wire: Whether to enable automatic dependency wiring
        """
    @property
    def name(self) -> str:
        """Get the context name."""
    @property
    def parent(self) -> Context | None:
        """Get the parent context."""
    def get_container(self, name: str | None = None) -> Container[Any]:
        """
        Get the container from this context.

        Args:
            name: Optional container name (unused for now)

        Returns:
            The container for this context
        """
    def create_child_context(self, name: str) -> Context:
        """
        Create a child context with hierarchical dependency resolution.

        Args:
            name: Name for the child context

        Returns:
            New child context instance
        """
    def register_component(self, interface: type[TInterface], implementation: type[TInterface] | None = None, factory: Any | None = None, **kwargs: Any) -> None:
        """
        Register a component in this context.

        Args:
            interface: Interface type to register
            implementation: Implementation type (defaults to interface)
            scope: Component lifecycle scope
            name: Optional component name
            tags: Optional component tags
            factory: Optional factory function
        """
    def resolve(self, interface: type[TInterface], name: str | None = None) -> TInterface:
        """
        Resolve a component from this context or its hierarchy.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance
        """
    async def resolve_async(self, interface: type[TInterface], name: str | None = None) -> TInterface:
        """
        Asynchronously resolve a component from this context or its hierarchy.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance
        """
    def is_registered(self, interface: type[TInterface], name: str | None = None) -> bool:
        """
        Check if a component is registered in this context or its hierarchy.

        Args:
            interface: Interface type to check
            name: Optional component name

        Returns:
            True if the component is registered
        """
    def add_import(self, declaration: ImportDeclaration) -> None:
        """
        Add an import declaration to this context.

        Args:
            declaration: Import declaration to add
        """
    def register_source_context(self, context_name: str, context: Context) -> None:
        """
        Register a source context for imports.

        Args:
            context_name: Name of the source context
            context: The source context instance
        """
    def shutdown(self) -> None:
        """
        Shutdown the context and cleanup resources.
        """
    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of the context state.

        Returns:
            Dictionary containing context summary information
        """
    def enable_auto_wiring(self) -> None:
        """
        Enable automatic dependency injection for this context.

        This method should be called after all components are registered
        to enable automatic dependency resolution within this context.
        """
    def _register_child_context(self, child_context: Context) -> None:
        """
        Register a child context for lifecycle management.

        Args:
            child_context: Child context to register
        """
    def __repr__(self) -> str:
        """Get string representation of the context."""
