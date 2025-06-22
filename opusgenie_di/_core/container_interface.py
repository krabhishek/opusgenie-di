"""Container interface for dependency injection."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from .._base import ComponentMetadataProtocol, ComponentProviderProtocol, ComponentScope

# Type variables for generic interfaces
T = TypeVar("T")
TInterface = TypeVar("TInterface")
TImplementation = TypeVar("TImplementation")


class ContainerInterface[T](ABC):
    """
    Abstract base class for dependency injection containers.

    Containers are the core infrastructure for dependency injection,
    managing component registration, resolution, and lifecycle.
    """

    @abstractmethod
    def register(
        self,
        interface: type[TInterface],
        implementation: type[TImplementation] | None = None,
        *,
        scope: ComponentScope = ComponentScope.SINGLETON,
        name: str | None = None,
        tags: dict[str, Any] | None = None,
        factory: Any = None,
    ) -> None:
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
        ...

    @abstractmethod
    def register_provider(
        self,
        interface: type[TInterface],
        provider: ComponentProviderProtocol[TInterface],
        *,
        name: str | None = None,
        tags: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a component provider for an interface.

        Args:
            interface: Interface type to register
            provider: Provider instance for the interface
            name: Optional component name
            tags: Optional component tags
        """
        ...

    @abstractmethod
    def resolve(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface:
        """
        Resolve a component instance for an interface.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance implementing the interface
        """
        ...

    @abstractmethod
    async def resolve_async(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface:
        """
        Asynchronously resolve a component instance for an interface.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance implementing the interface
        """
        ...

    @abstractmethod
    def is_registered(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool:
        """
        Check if an interface is registered in the container.

        Args:
            interface: Interface type to check
            name: Optional component name

        Returns:
            True if the interface is registered
        """
        ...

    @abstractmethod
    def get_metadata(
        self, interface: type[TInterface], name: str | None = None
    ) -> ComponentMetadataProtocol:
        """
        Get metadata for a registered component.

        Args:
            interface: Interface type
            name: Optional component name

        Returns:
            ComponentMetadata for the component
        """
        ...

    @abstractmethod
    def unregister(self, interface: type[TInterface], name: str | None = None) -> bool:
        """
        Unregister a component from the container.

        Args:
            interface: Interface type to unregister
            name: Optional component name

        Returns:
            True if the component was unregistered, False if it wasn't registered
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all registrations from the container."""
        ...

    @abstractmethod
    def get_registered_types(self) -> list[type]:
        """Get a list of all registered interface types."""
        ...

    @abstractmethod
    def get_registration_count(self) -> int:
        """Get the number of registered components."""
        ...
