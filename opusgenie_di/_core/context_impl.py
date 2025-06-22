"""Context implementation for multi-container dependency injection."""

from threading import RLock
import time
from typing import Any, TypeVar
from weakref import WeakSet

from .._base import ComponentScope
from .._hooks import EventHook, emit_event
from .._utils import (
    get_logger,
    log_context_creation,
    log_error,
    log_import_resolution,
    validate_context_name,
)
from .container_impl import Container
from .context_interface import ContextInterface
from .exceptions import ComponentResolutionError, ContextError, ImportError

T = TypeVar("T")
TInterface = TypeVar("TInterface")

logger = get_logger(__name__)


class ImportDeclaration:
    """
    Declaration for importing a component from another context.

    This represents a cross-context dependency that needs to be resolved
    from a different context than the one making the request.
    """

    def __init__(
        self,
        component_type: type,
        source_context: str,
        name: str | None = None,
        alias: str | None = None,
    ) -> None:
        """
        Initialize the import declaration.

        Args:
            component_type: Type of component to import
            source_context: Name of the context to import from
            name: Optional specific name of the component
            alias: Optional alias to use in the importing context
        """
        self.component_type = component_type
        self.source_context = source_context
        self.name = name
        self.alias = alias

    def get_provider_name(self) -> str:
        """Get the provider name for this import."""
        return self.name or self.component_type.__name__

    def get_import_key(self) -> str:
        """Get a unique key for this import."""
        return f"{self.source_context}:{self.get_provider_name()}"

    def __repr__(self) -> str:
        return (
            f"ImportDeclaration(type={self.component_type.__name__}, "
            f"from={self.source_context}, name={self.name}, alias={self.alias})"
        )


class ImportManager:
    """
    Manager for handling cross-context imports.

    Manages the resolution of components from other contexts,
    maintaining references to source contexts and handling
    import validation and resolution.
    """

    def __init__(self, context: "Context") -> None:
        """
        Initialize the import manager.

        Args:
            context: The context this manager belongs to
        """
        self._context = context
        self._imports: dict[str, ImportDeclaration] = {}
        self._source_contexts: dict[str, Context] = {}

    def add_import(self, declaration: ImportDeclaration) -> None:
        """
        Add an import declaration.

        Args:
            declaration: Import declaration to add
        """
        import_key = declaration.get_import_key()
        self._imports[import_key] = declaration

        logger.debug(
            "Added import declaration",
            context=self._context.name,
            import_key=import_key,
            component=declaration.component_type.__name__,
            source_context=declaration.source_context,
        )

    def register_source_context(self, context_name: str, context: "Context") -> None:
        """
        Register a source context for imports.

        Args:
            context_name: Name of the source context
            context: The source context instance
        """
        self._source_contexts[context_name] = context
        logger.debug(
            "Registered source context",
            context=self._context.name,
            source_context=context_name,
        )

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
        provider_name = name or component_type.__name__

        # Find matching import declaration
        matching_import = None
        for declaration in self._imports.values():
            if (
                declaration.component_type == component_type
                and declaration.get_provider_name() == provider_name
            ):
                matching_import = declaration
                break

        if not matching_import:
            raise ImportError(
                f"No import declaration found for {component_type.__name__}",
                component_type=component_type.__name__,
                target_context=self._context.name,
                details=f"Component '{provider_name}' not found in imports",
            )

        # Get source context
        source_context = self._source_contexts.get(matching_import.source_context)
        if not source_context:
            raise ImportError(
                f"Source context '{matching_import.source_context}' not available",
                component_type=component_type.__name__,
                source_context=matching_import.source_context,
                target_context=self._context.name,
                details="Source context not registered with import manager",
            )

        # Resolve from source context
        try:
            start_time = time.time()
            instance: T = source_context.resolve(component_type, matching_import.name)
            resolution_time_ms = (time.time() - start_time) * 1000

            log_import_resolution(
                component_type,
                matching_import.source_context,
                self._context.name,
                resolution_time_ms=resolution_time_ms,
            )

            return instance

        except Exception as e:
            raise ImportError(
                f"Failed to resolve import for {component_type.__name__}",
                component_type=component_type.__name__,
                source_context=matching_import.source_context,
                target_context=self._context.name,
                details=str(e),
            ) from e

    def get_imports(self) -> list[ImportDeclaration]:
        """Get all import declarations."""
        return list(self._imports.values())

    def get_import_count(self) -> int:
        """Get the number of imports."""
        return len(self._imports)

    def clear_imports(self) -> None:
        """Clear all imports."""
        self._imports.clear()
        self._source_contexts.clear()
        logger.debug("Cleared all imports", context=self._context.name)


class Context(ContextInterface):
    """
    Context implementation for multi-container dependency injection.

    Provides Angular-like DI functionality with support for multiple
    isolated contexts, hierarchical relationships, and cross-context imports.
    """

    def __init__(
        self,
        name: str,
        parent: "Context | None" = None,
        auto_wire: bool = True,
    ) -> None:
        """
        Initialize the context.

        Args:
            name: Unique name for this context
            parent: Optional parent context for hierarchical DI
            auto_wire: Whether to enable automatic dependency wiring
        """
        validate_context_name(name)

        self._name = name
        self._parent = parent
        self._auto_wire = auto_wire
        self._lock = RLock()
        self._child_contexts: WeakSet[Context] = WeakSet()

        # Create underlying container with reference to this context
        self._container: Container[Any] = Container(name, context_ref=self)

        # Initialize import manager
        self._import_manager = ImportManager(self)

        # Register with parent if applicable
        if parent:
            parent._register_child_context(self)

        log_context_creation(
            name,
            parent.name if parent else None,
            auto_wire=auto_wire,
        )

        # Emit context creation event
        emit_event(
            EventHook.CONTEXT_CREATED,
            {
                "context_name": name,
                "parent_context": parent.name if parent else None,
                "auto_wire": auto_wire,
                "creation_time": time.time(),
            },
        )

    @property
    def name(self) -> str:
        """Get the context name."""
        return self._name

    @property
    def parent(self) -> "Context | None":
        """Get the parent context."""
        return self._parent

    def get_container(self, name: str | None = None) -> Container[Any]:
        """
        Get the container from this context.

        Args:
            name: Optional container name (unused for now)

        Returns:
            The container for this context
        """
        return self._container

    def create_child_context(self, name: str) -> "Context":
        """
        Create a child context with hierarchical dependency resolution.

        Args:
            name: Name for the child context

        Returns:
            New child context instance
        """
        return Context(name=name, parent=self, auto_wire=self._auto_wire)

    def register_component(
        self,
        interface: type[TInterface],
        implementation: type[TInterface] | None = None,
        **kwargs: Any,
    ) -> None:
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
        # Extract parameters from kwargs with defaults
        scope = kwargs.get("scope", ComponentScope.SINGLETON)
        name = kwargs.get("name")
        tags = kwargs.get("tags")
        factory = kwargs.get("factory")

        try:
            with self._lock:
                self._container.register(
                    interface=interface,
                    implementation=implementation,
                    scope=scope,
                    name=name,
                    tags=tags,
                    factory=factory,
                )

                # Emit component registration event
                emit_event(
                    EventHook.COMPONENT_REGISTERED,
                    {
                        "context_name": self._name,
                        "interface_name": interface.__name__,
                        "implementation_name": (implementation or interface).__name__,
                        "scope": scope.value,
                        "component_name": name,
                        "tags": tags or {},
                        "registration_time": time.time(),
                    },
                )

        except Exception as e:
            emit_event(
                EventHook.ERROR_OCCURRED,
                {
                    "context_name": self._name,
                    "operation": "register_component",
                    "error": str(e),
                    "component_type": (implementation or interface).__name__,
                },
            )
            raise

    def resolve(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface:
        """
        Resolve a component from this context or its hierarchy.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance
        """
        start_time = time.time()

        try:
            with self._lock:
                # Try to resolve from this context's container
                if self._container.is_registered(interface, name):
                    instance: TInterface = self._container.resolve(interface, name)
                    resolution_time_ms = (time.time() - start_time) * 1000

                    emit_event(
                        EventHook.COMPONENT_RESOLVED,
                        {
                            "context_name": self._name,
                            "interface_name": interface.__name__,
                            "component_name": name,
                            "resolution_time_ms": resolution_time_ms,
                            "resolution_source": "direct",
                        },
                    )

                    return instance

                # Try to resolve from imports
                try:
                    import_instance: TInterface = self._import_manager.resolve_import(
                        interface, name
                    )
                    resolution_time_ms = (time.time() - start_time) * 1000

                    emit_event(
                        EventHook.COMPONENT_RESOLVED,
                        {
                            "context_name": self._name,
                            "interface_name": interface.__name__,
                            "component_name": name,
                            "resolution_time_ms": resolution_time_ms,
                            "resolution_source": "import",
                        },
                    )

                    return import_instance

                except ImportError:
                    # Import resolution failed, continue to parent context
                    pass

                # Try parent context if available
                if self._parent:
                    logger.debug(
                        "Component not found in context, trying parent",
                        context=self._name,
                        parent=self._parent.name,
                        component=interface.__name__,
                    )
                    return self._parent.resolve(interface, name)

                # Component not found anywhere
                raise ComponentResolutionError(
                    f"No registration found for interface '{interface.__name__}'",
                    component_type=interface.__name__,
                    details=f"Component '{name or interface.__name__}' not registered in context hierarchy",
                    context_name=self._name,
                )

        except ComponentResolutionError:
            emit_event(
                EventHook.COMPONENT_RESOLUTION_FAILED,
                {
                    "context_name": self._name,
                    "interface_name": interface.__name__,
                    "component_name": name,
                    "resolution_time_ms": (time.time() - start_time) * 1000,
                },
            )
            raise
        except Exception as e:
            log_error(
                "resolve_component",
                e,
                context_name=self._name,
                component_type=interface,
            )
            emit_event(
                EventHook.ERROR_OCCURRED,
                {
                    "context_name": self._name,
                    "operation": "resolve_component",
                    "error": str(e),
                    "component_type": interface.__name__,
                },
            )
            raise ComponentResolutionError(
                f"Failed to resolve component {interface.__name__}",
                component_type=interface.__name__,
                details=str(e),
                context_name=self._name,
            ) from e

    async def resolve_async(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface:
        """
        Asynchronously resolve a component from this context or its hierarchy.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance
        """
        # For now, delegate to sync resolution
        # Could be enhanced to support actual async resolution
        return self.resolve(interface, name)

    def is_registered(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool:
        """
        Check if a component is registered in this context or its hierarchy.

        Args:
            interface: Interface type to check
            name: Optional component name

        Returns:
            True if the component is registered
        """
        with self._lock:
            # Check this context
            if self._container.is_registered(interface, name):
                return True

            # Check imports
            try:
                self._import_manager.resolve_import(interface, name)
                return True
            except ImportError:
                pass

            # Check parent context
            if self._parent:
                return self._parent.is_registered(interface, name)

            return False

    def add_import(self, declaration: ImportDeclaration) -> None:
        """
        Add an import declaration to this context.

        Args:
            declaration: Import declaration to add
        """
        self._import_manager.add_import(declaration)

    def register_source_context(self, context_name: str, context: "Context") -> None:
        """
        Register a source context for imports.

        Args:
            context_name: Name of the source context
            context: The source context instance
        """
        self._import_manager.register_source_context(context_name, context)

    def shutdown(self) -> None:
        """
        Shutdown the context and cleanup resources.
        """
        try:
            with self._lock:
                # Shutdown child contexts first
                for child_context in list(self._child_contexts):
                    try:
                        child_context.shutdown()
                    except Exception as e:
                        logger.warning(
                            "Error shutting down child context",
                            parent_context=self._name,
                            child_context=child_context.name,
                            error=str(e),
                        )

                # Clear imports
                self._import_manager.clear_imports()

                # Shutdown container
                self._container.shutdown()

                logger.debug("Shutdown context", context=self._name)

                # Emit context destruction event
                emit_event(
                    EventHook.CONTEXT_DESTROYED,
                    {
                        "context_name": self._name,
                        "shutdown_time": time.time(),
                    },
                )

        except Exception as e:
            log_error(
                "shutdown_context",
                e,
                context_name=self._name,
            )
            raise ContextError(
                f"Failed to shutdown context '{self._name}'",
                details=str(e),
                context_name=self._name,
                operation="shutdown",
            ) from e

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of the context state.

        Returns:
            Dictionary containing context summary information
        """
        with self._lock:
            return {
                "name": self._name,
                "parent": self._parent.name if self._parent else None,
                "component_count": self._container.get_registration_count(),
                "import_count": self._import_manager.get_import_count(),
                "child_count": len(self._child_contexts),
                "auto_wire": self._auto_wire,
                "registered_types": self._container.get_registered_types(),
                "imports": [
                    {
                        "component": decl.component_type.__name__,
                        "source_context": decl.source_context,
                        "name": decl.name,
                        "alias": decl.alias,
                    }
                    for decl in self._import_manager.get_imports()
                ],
            }

    def enable_auto_wiring(self) -> None:
        """
        Enable automatic dependency injection for this context.

        This method should be called after all components are registered
        to enable automatic dependency resolution within this context.
        """
        try:
            with self._lock:
                # Set auto-wiring flag to True
                self._auto_wire = True
                self._container.enable_auto_wiring()
                logger.debug(
                    "Enabled auto-wiring for context",
                    context=self._name,
                    component_count=self._container.get_registration_count(),
                )

        except Exception as e:
            log_error(
                "enable_context_auto_wiring",
                e,
                context_name=self._name,
            )
            raise ContextError(
                f"Failed to enable auto-wiring for context '{self._name}'",
                details=str(e),
                context_name=self._name,
                operation="enable_auto_wiring",
            ) from e

    def _register_child_context(self, child_context: "Context") -> None:
        """
        Register a child context for lifecycle management.

        Args:
            child_context: Child context to register
        """
        with self._lock:
            self._child_contexts.add(child_context)

    def __repr__(self) -> str:
        """Get string representation of the context."""
        parent_name = self._parent.name if self._parent else "None"
        return (
            f"Context(name='{self._name}', parent='{parent_name}', "
            f"components={self._container.get_registration_count()})"
        )
