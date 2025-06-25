import abc
from .._base import ComponentScope as ComponentScope
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar('T')

class ProviderInterface[T](ABC, metaclass=abc.ABCMeta):
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
    @abstractmethod
    def get_scope(self) -> ComponentScope:
        """
        Get the scope for components created by this provider.

        Returns:
            Component scope
        """
    @abstractmethod
    def get_component_type(self) -> type:
        """
        Get the type of components created by this provider.

        Returns:
            Component type
        """
    @abstractmethod
    def can_provide(self, component_type: type) -> bool:
        """
        Check if this provider can create instances of the given type.

        Args:
            component_type: Type to check

        Returns:
            True if this provider can create instances of the type
        """
    @abstractmethod
    def dispose(self, instance: T) -> None:
        """
        Dispose of a component instance created by this provider.

        Args:
            instance: Instance to dispose
        """

class ComponentProvider(ProviderInterface[T]):
    """
    Base implementation of a component provider.

    This provides a simple implementation for most common provider scenarios.
    """
    _component_type: Incomplete
    _scope: Incomplete
    _factory: Incomplete
    def __init__(self, component_type: type[T], scope: ComponentScope = ..., factory: Any = None) -> None:
        """
        Initialize the provider.

        Args:
            component_type: Type of component to provide
            scope: Scope for component lifecycle
            factory: Optional factory function
        """
    def provide(self, *args: Any, **kwargs: Any) -> T:
        """Create and return a component instance."""
    async def provide_async(self, *args: Any, **kwargs: Any) -> T:
        """Asynchronously create and return a component instance."""
    def get_scope(self) -> ComponentScope:
        """Get the scope for components created by this provider."""
    def get_component_type(self) -> type:
        """Get the type of components created by this provider."""
    def can_provide(self, component_type: type) -> bool:
        """Check if this provider can create instances of the given type."""
    def dispose(self, instance: T) -> None:
        """Dispose of a component instance created by this provider."""
