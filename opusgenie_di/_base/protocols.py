"""Protocol definitions for dependency injection components."""

from abc import abstractmethod
from typing import Any, Protocol, TypeVar, runtime_checkable

from .enums import ComponentScope, LifecycleStage

# Type variable for generic protocols (covariant for Protocol)
T = TypeVar("T", covariant=True)


@runtime_checkable
class ComponentProtocol(Protocol):
    """
    Protocol for components that can be managed by the DI system.

    This protocol defines the minimum interface that components must implement
    to be effectively managed by the dependency injection system.
    """

    component_id: str
    component_name: str | None
    component_type: str | None

    @abstractmethod
    def get_component_id(self) -> str:
        """Get the unique identifier for this component."""
        ...

    @abstractmethod
    def get_component_name(self) -> str | None:
        """Get the human-readable name for this component."""
        ...


@runtime_checkable
class InjectableProtocol(Protocol):
    """
    Protocol for objects that can be injected as dependencies.

    This is a marker protocol that indicates an object can be used
    as a dependency in the injection system.
    """


@runtime_checkable
class ComponentProviderProtocol[T](Protocol):
    """
    Protocol for component providers.

    Providers are responsible for creating component instances with
    proper configuration and dependencies.
    """

    @abstractmethod
    def provide(self) -> T:
        """Create and return a component instance."""
        ...

    @abstractmethod
    def get_scope(self) -> ComponentScope:
        """Get the scope for components created by this provider."""
        ...


@runtime_checkable
class LifecycleProtocol(Protocol):
    """
    Protocol for components that have lifecycle management.

    Components implementing this protocol can be managed through
    their lifecycle stages by the DI system.
    """

    @abstractmethod
    def get_lifecycle_stage(self) -> LifecycleStage:
        """Get the current lifecycle stage of the component."""
        ...

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component."""
        ...

    @abstractmethod
    async def start(self) -> None:
        """Start the component."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the component."""
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up component resources."""
        ...


@runtime_checkable
class ComponentMetadataProtocol(Protocol):
    """
    Protocol for component metadata.

    Defines the interface for accessing component metadata
    information used by the DI system.
    """

    @abstractmethod
    def get_component_type(self) -> type:
        """Get the component type."""
        ...

    @abstractmethod
    def get_scope(self) -> ComponentScope:
        """Get the component scope."""
        ...

    @abstractmethod
    def get_tags(self) -> dict[str, Any]:
        """Get component tags."""
        ...

    @abstractmethod
    def get_dependencies(self) -> list[type]:
        """Get component dependencies."""
        ...


@runtime_checkable
class RegistrableProtocol(Protocol):
    """
    Protocol for components that can be registered in the DI system.

    This protocol ensures components have the necessary methods
    for registration and management.
    """

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the component with dependencies."""
        ...
