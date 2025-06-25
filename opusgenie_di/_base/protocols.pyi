from .enums import ComponentScope as ComponentScope, LifecycleStage as LifecycleStage
from abc import abstractmethod
from typing import Any, Protocol, TypeVar

T = TypeVar('T', covariant=True)

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
    @abstractmethod
    def get_component_name(self) -> str | None:
        """Get the human-readable name for this component."""

class InjectableProtocol(Protocol):
    """
    Protocol for objects that can be injected as dependencies.

    This is a marker protocol that indicates an object can be used
    as a dependency in the injection system.
    """

class ComponentProviderProtocol[T](Protocol):
    """
    Protocol for component providers.

    Providers are responsible for creating component instances with
    proper configuration and dependencies.
    """
    @abstractmethod
    def provide(self) -> T:
        """Create and return a component instance."""
    @abstractmethod
    def get_scope(self) -> ComponentScope:
        """Get the scope for components created by this provider."""

class LifecycleProtocol(Protocol):
    """
    Protocol for components that have lifecycle management.

    Components implementing this protocol can be managed through
    their lifecycle stages by the DI system.
    """
    @abstractmethod
    def get_lifecycle_stage(self) -> LifecycleStage:
        """Get the current lifecycle stage of the component."""
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component."""
    @abstractmethod
    async def start(self) -> None:
        """Start the component."""
    @abstractmethod
    async def stop(self) -> None:
        """Stop the component."""
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up component resources."""

class ComponentMetadataProtocol(Protocol):
    """
    Protocol for component metadata.

    Defines the interface for accessing component metadata
    information used by the DI system.
    """
    @abstractmethod
    def get_component_type(self) -> type:
        """Get the component type."""
    @abstractmethod
    def get_scope(self) -> ComponentScope:
        """Get the component scope."""
    @abstractmethod
    def get_tags(self) -> dict[str, Any]:
        """Get component tags."""
    @abstractmethod
    def get_dependencies(self) -> list[type]:
        """Get component dependencies."""

class RegistrableProtocol(Protocol):
    """
    Protocol for components that can be registered in the DI system.

    This protocol ensures components have the necessary methods
    for registration and management.
    """
    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize the component with dependencies."""
