from .._base import ComponentMetadata as ComponentMetadata, ComponentScope as ComponentScope
from .._base.protocols import ComponentMetadataProtocol as ComponentMetadataProtocol
from .._utils import get_constructor_dependencies as get_constructor_dependencies, get_logger as get_logger, log_component_registration as log_component_registration, log_component_resolution as log_component_resolution, log_error as log_error, validate_component_registration as validate_component_registration
from .container_interface import ContainerInterface as ContainerInterface
from .exceptions import CircularDependencyError as CircularDependencyError, ComponentRegistrationError as ComponentRegistrationError, ComponentResolutionError as ComponentResolutionError
from .scope_impl import ScopeManager as ScopeManager
from _typeshed import Incomplete
from typing import Any, TypeVar

T = TypeVar('T')
TInterface = TypeVar('TInterface')
TImplementation = TypeVar('TImplementation')
logger: Incomplete
_resolution_chain: Incomplete

def _get_resolution_chain() -> list[str]:
    """Get the current resolution chain for this thread."""
def _push_resolution(component_name: str) -> None:
    """Add a component to the resolution chain."""
def _pop_resolution() -> None:
    """Remove the last component from the resolution chain."""
def _check_circular_dependency(component_name: str, context_name: str) -> None:
    """Check if adding this component would create a circular dependency."""

class Container(ContainerInterface[T]):
    """
    Container implementation wrapping dependency-injector containers.

    Provides Angular-like DI functionality by wrapping dependency-injector
    containers with structured logging, metadata management, and
    multi-context support.
    """
    _name: Incomplete
    _context_ref: Incomplete
    _lock: Incomplete
    _scope_manager: Incomplete
    _container: Incomplete
    _component_metadata: dict[str, ComponentMetadata]
    _registered_types: dict[str, type]
    _registration_count: int
    def __init__(self, name: str = 'default', context_ref: Any = None) -> None:
        """
        Initialize the container.

        Args:
            name: Name of the container for identification
            context_ref: Optional reference to the parent context for cross-context resolution
        """
    @property
    def name(self) -> str:
        """Get the container name."""
    def register(self, interface: type[TInterface], implementation: type[TImplementation] | None = None, *, scope: ComponentScope = ..., name: str | None = None, tags: dict[str, Any] | None = None, factory: Any = None) -> None:
        """
        Register a component implementation for an interface.

        Args:
            interface: Interface type to register
            implementation: Implementation type (defaults to interface)
            scope: Component lifecycle scope
            name: Optional component name
            tags: Optional component tags
            factory: Optional factory function for creating instances
        """
    def register_provider(self, interface: type[TInterface], provider: Any, *, name: str | None = None, tags: dict[str, Any] | None = None) -> None:
        """
        Register a component provider for an interface.

        Args:
            interface: Interface type to register
            provider: Provider instance for the interface
            name: Optional component name
            tags: Optional component tags
        """
    def resolve(self, interface: type[TInterface], name: str | None = None) -> TInterface:
        """
        Resolve a component instance for an interface.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance implementing the interface
        """
    async def resolve_async(self, interface: type[TInterface], name: str | None = None) -> TInterface:
        """
        Asynchronously resolve a component instance for an interface.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance implementing the interface
        """
    def is_registered(self, interface: type[TInterface], name: str | None = None) -> bool:
        """
        Check if an interface is registered in the container.

        Args:
            interface: Interface type to check
            name: Optional component name

        Returns:
            True if the interface is registered
        """
    def get_metadata(self, interface: type[TInterface], name: str | None = None) -> ComponentMetadataProtocol:
        """
        Get metadata for a registered component.

        Args:
            interface: Interface type
            name: Optional component name

        Returns:
            ComponentMetadata for the component
        """
    def unregister(self, interface: type[TInterface], name: str | None = None) -> bool:
        """
        Unregister a component from the container.

        Args:
            interface: Interface type to unregister
            name: Optional component name

        Returns:
            True if the component was unregistered, False if it wasn't registered
        """
    def clear(self) -> None:
        """Clear all registrations from the container."""
    def get_registered_types(self) -> list[type]:
        """Get a list of all registered interface types."""
    def get_registration_count(self) -> int:
        """Get the number of registered components."""
    def wire_modules(self, modules: list[str] | None = None) -> None:
        """
        Wire the container for automatic dependency injection.

        Args:
            modules: Optional list of module names to wire
        """
    def shutdown(self) -> None:
        """Shutdown the container and cleanup resources."""
    def enable_auto_wiring(self) -> None:
        """
        Enable automatic dependency injection for this container.

        This method should be called after all components are registered
        to enable automatic dependency resolution.
        """
    def _should_inject_dependency(self, dependency_type: type) -> bool:
        """
        Determine if a dependency should be auto-injected.

        Args:
            dependency_type: The type of the dependency

        Returns:
            True if the dependency should be auto-injected
        """
    def _create_dependency_provider(self, dependency_type: type) -> Any:
        """
        Create a provider for automatic dependency injection.

        Args:
            dependency_type: The type of dependency to inject

        Returns:
            A provider that can resolve the dependency
        """
    def _create_auto_wiring_factory(self, impl_class: type, dependencies: dict[str, tuple[type | None, bool]]) -> Any:
        """
        Create a factory function that automatically resolves and injects dependencies.

        Args:
            impl_class: The implementation class to create instances of
            dependencies: Dictionary of dependencies (param_name -> (type, is_optional))

        Returns:
            Factory function that creates instances with auto-injected dependencies
        """
    def __repr__(self) -> str:
        """Get string representation of the container."""
