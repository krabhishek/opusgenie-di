"""Provider interface for component creation."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from .._base import ComponentScope

T = TypeVar("T")


class ProviderInterface[T](ABC):
    """
    Abstract base class for component providers.

    Providers are responsible for creating component instances with
    proper configuration and dependencies.
    """

    @abstractmethod
    def provide(self, *args: Any, **kwargs: Any) -> T:
        """
        Create and return a component instance.

        Args:
            *args: Positional arguments for component creation
            **kwargs: Keyword arguments for component creation

        Returns:
            Component instance
        """
        ...

    @abstractmethod
    async def provide_async(self, *args: Any, **kwargs: Any) -> T:
        """
        Asynchronously create and return a component instance.

        Args:
            *args: Positional arguments for component creation
            **kwargs: Keyword arguments for component creation

        Returns:
            Component instance
        """
        ...

    @abstractmethod
    def get_scope(self) -> ComponentScope:
        """
        Get the scope for components created by this provider.

        Returns:
            Component scope
        """
        ...

    @abstractmethod
    def get_component_type(self) -> type:
        """
        Get the type of components created by this provider.

        Returns:
            Component type
        """
        ...

    @abstractmethod
    def can_provide(self, component_type: type) -> bool:
        """
        Check if this provider can create instances of the given type.

        Args:
            component_type: Type to check

        Returns:
            True if this provider can create instances of the type
        """
        ...

    @abstractmethod
    def dispose(self, instance: T) -> None:
        """
        Dispose of a component instance created by this provider.

        Args:
            instance: Instance to dispose
        """
        ...


class ComponentProvider(ProviderInterface[T]):
    """
    Base implementation of a component provider.

    This provides a simple implementation for most common provider scenarios.
    """

    def __init__(
        self,
        component_type: type[T],
        scope: ComponentScope = ComponentScope.SINGLETON,
        factory: Any = None,
    ) -> None:
        """
        Initialize the provider.

        Args:
            component_type: Type of component to provide
            scope: Scope for component lifecycle
            factory: Optional factory function
        """
        self._component_type = component_type
        self._scope = scope
        self._factory = factory or component_type

    def provide(self, *args: Any, **kwargs: Any) -> T:
        """Create and return a component instance."""
        return self._factory(*args, **kwargs)

    async def provide_async(self, *args: Any, **kwargs: Any) -> T:
        """Asynchronously create and return a component instance."""
        # For now, delegate to sync version
        # Could be enhanced to support actual async factories
        return self.provide(*args, **kwargs)

    def get_scope(self) -> ComponentScope:
        """Get the scope for components created by this provider."""
        return self._scope

    def get_component_type(self) -> type:
        """Get the type of components created by this provider."""
        return self._component_type

    def can_provide(self, component_type: type) -> bool:
        """Check if this provider can create instances of the given type."""
        return component_type == self._component_type or (
            isinstance(component_type, type)
            and issubclass(self._component_type, component_type)
        )

    def dispose(self, instance: T) -> None:
        """Dispose of a component instance created by this provider."""
        # Check if instance has cleanup methods
        if hasattr(instance, "cleanup"):
            if callable(instance.cleanup):
                instance.cleanup()
        elif hasattr(instance, "dispose"):
            if callable(instance.dispose):
                instance.dispose()
        elif hasattr(instance, "close") and callable(instance.close):
            instance.close()
