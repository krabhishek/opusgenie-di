"""Context interface for multi-container dependency injection."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from .container_interface import ContainerInterface

TInterface = TypeVar("TInterface")


class ContextInterface(ABC):
    """
    Abstract base class for dependency injection contexts.

    Contexts enable multi-container dependency injection with proper
    isolation and hierarchy management. This supports complex applications
    with multiple scopes of component visibility and lifecycle.
    """

    @abstractmethod
    def get_container(self, name: str | None = None) -> ContainerInterface[TInterface]:
        """
        Get a container from this context.

        Args:
            name: Optional container name

        Returns:
            Container instance
        """
        ...

    @abstractmethod
    def create_child_context(self, name: str) -> "ContextInterface":
        """
        Create a child context with hierarchical dependency resolution.

        Args:
            name: Name for the child context

        Returns:
            New child context instance
        """
        ...

    @abstractmethod
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
            **kwargs: Additional registration parameters
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of this context.

        Returns:
            Context name
        """
        ...

    @property
    @abstractmethod
    def parent(self) -> "ContextInterface | None":
        """
        Get the parent context if this is a child context.

        Returns:
            Parent context or None if this is a root context
        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the context and cleanup resources.
        """
        ...
