"""Scope manager interface for component lifecycle management."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from .._base import ComponentScope

T = TypeVar("T")


class ScopeManagerInterface(ABC):
    """
    Abstract base class for component scope management.

    Scope managers handle component lifecycle according to their
    configured scope, enabling proper resource management and
    instance caching strategies.
    """

    @abstractmethod
    def get_or_create(
        self,
        key: str,
        factory: Callable[[], T],
        scope: ComponentScope,
    ) -> T:
        """
        Get an existing instance or create a new one according to scope rules.

        Args:
            key: Unique key for the component instance
            factory: Factory function to create new instances
            scope: Component scope for lifecycle management

        Returns:
            Component instance
        """
        ...

    @abstractmethod
    async def get_or_create_async(
        self,
        key: str,
        factory: Callable[[], Coroutine[Any, Any, T]],
        scope: ComponentScope,
    ) -> T:
        """
        Asynchronously get an existing instance or create a new one.

        Args:
            key: Unique key for the component instance
            factory: Async factory function to create new instances
            scope: Component scope for lifecycle management

        Returns:
            Component instance
        """
        ...

    @abstractmethod
    def clear_scope(self, scope: ComponentScope) -> None:
        """
        Clear all instances for a specific scope.

        Args:
            scope: Scope to clear
        """
        ...

    @abstractmethod
    def clear_all(self) -> None:
        """Clear all cached instances across all scopes."""
        ...

    @abstractmethod
    def dispose(self, instance: T) -> None:
        """
        Dispose of a component instance and clean up resources.

        Args:
            instance: Component instance to dispose
        """
        ...

    @abstractmethod
    def has_instance(self, key: str, scope: ComponentScope) -> bool:
        """
        Check if an instance exists for the given key and scope.

        Args:
            key: Instance key
            scope: Component scope

        Returns:
            True if instance exists
        """
        ...

    @abstractmethod
    def get_instance_count(self, scope: ComponentScope | None = None) -> int:
        """
        Get the number of cached instances.

        Args:
            scope: Optional scope to filter by, None for all scopes

        Returns:
            Number of cached instances
        """
        ...

    @abstractmethod
    def get_scopes(self) -> list[ComponentScope]:
        """
        Get all scopes that have cached instances.

        Returns:
            List of scopes with instances
        """
        ...
