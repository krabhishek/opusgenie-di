from .._base import ComponentScope as ComponentScope
from .._utils import get_logger as get_logger, log_error as log_error
from .event_loop_manager import get_event_loop_manager as get_event_loop_manager, run_async_safely as run_async_safely
from .exceptions import ScopeError as ScopeError
from .scope_interface import ScopeManagerInterface as ScopeManagerInterface
from _typeshed import Incomplete
from collections.abc import Callable as Callable, Coroutine, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, TypeVar
from weakref import WeakValueDictionary

T = TypeVar('T')
logger: Incomplete
_current_scope: ContextVar[str | None]

class ScopeManager(ScopeManagerInterface):
    """
    Implementation of scope manager for component lifecycle management.

    Manages component instances according to their configured scope,
    providing proper caching and disposal strategies.
    """
    _lock: Incomplete
    _singletons: dict[str, Any]
    _scoped_instances: dict[str, dict[str, Any]]
    _disposable_instances: WeakValueDictionary[int, Any]
    _lifecycle_callback: Incomplete
    def __init__(self, lifecycle_callback: Callable[..., None] | None = None) -> None:
        """
        Initialize the scope manager.

        Args:
            lifecycle_callback: Optional callback for lifecycle events.
                                Called with (event_name, **kwargs)
        """
    def _trigger_lifecycle_event(self, event: str, **kwargs: Any) -> None:
        """Trigger a lifecycle event callback if configured."""
    def get_or_create(self, key: str, factory: Callable[[], T], scope: ComponentScope) -> T:
        """
        Get an existing instance or create a new one according to scope rules.

        Args:
            key: Unique key for the component instance
            factory: Factory function to create new instances
            scope: Component scope for lifecycle management

        Returns:
            Component instance
        """
    async def get_or_create_async(self, key: str, factory: Callable[[], Coroutine[Any, Any, T]], scope: ComponentScope) -> T:
        """
        Asynchronously get an existing instance or create a new one.

        Args:
            key: Unique key for the component instance
            factory: Async factory function to create new instances
            scope: Component scope for lifecycle management

        Returns:
            Component instance
        """
    def clear_scope(self, scope: ComponentScope) -> None:
        """
        Clear all instances for a specific scope.

        Args:
            scope: Scope to clear
        """
    def clear_all(self) -> None:
        """Clear all cached instances across all scopes."""
    def dispose(self, instance: T | None = None) -> None:
        """
        Dispose of a component instance and clean up resources.

        Args:
            instance: Component instance to dispose. If None, disposes all instances.
        """
    def has_instance(self, key: str, scope: ComponentScope) -> bool:
        """
        Check if an instance exists for the given key and scope.

        Args:
            key: Instance key
            scope: Component scope

        Returns:
            True if instance exists
        """
    def get_instance_count(self, scope: ComponentScope | None = None) -> int:
        """
        Get the number of cached instances.

        Args:
            scope: Optional scope to filter by, None for all scopes

        Returns:
            Number of cached instances
        """
    def get_scopes(self) -> list[ComponentScope]:
        """
        Get all scopes that have cached instances.

        Returns:
            List of scopes with instances
        """
    def create_or_get_instance(self, component_type: type[T], scope: ComponentScope, factory: Callable[[], T]) -> T:
        """
        Convenience method that matches test expectations.

        Args:
            component_type: Component type (used to generate key)
            scope: Component scope for lifecycle management
            factory: Factory function to create new instances

        Returns:
            Component instance
        """
    @contextmanager
    def create_scope(self) -> Generator[str, None, None]:
        """
        Create a new scope context.

        Returns:
            Context manager that provides a new scope for scoped components
        """
    def has_active_scope(self) -> bool:
        """
        Check if there's currently an active scope context.

        Returns:
            True if inside a scope context, False otherwise
        """
    def _get_or_create_singleton(self, key: str, factory: Callable[[], T]) -> T:
        """Get or create a singleton instance."""
    async def _get_or_create_singleton_async(self, key: str, factory: Callable[[], Coroutine[Any, Any, T]]) -> T:
        """Asynchronously get or create a singleton instance."""
    def _create_transient(self, factory: Callable[[], T]) -> T:
        """Create a transient instance."""
    async def _create_transient_async(self, factory: Callable[[], Coroutine[Any, Any, T]]) -> T:
        """Asynchronously create a transient instance."""
    def _get_or_create_scoped(self, key: str, factory: Callable[[], T]) -> T:
        """Get or create a scoped instance."""
    async def _get_or_create_scoped_async(self, key: str, factory: Callable[[], Coroutine[Any, Any, T]]) -> T:
        """Asynchronously get or create a scoped instance."""
    def _create_factory(self, factory: Callable[[], T]) -> T:
        """Create an instance using factory method."""
    async def _create_factory_async(self, factory: Callable[[], Coroutine[Any, Any, T]]) -> T:
        """Asynchronously create an instance using factory method."""
    def _track_disposable(self, instance: Any) -> None:
        """Track an instance for disposal if it has disposal methods."""
    def _has_disposal_methods(self, instance: Any) -> bool:
        """Check if an instance has disposal methods."""
    def _dispose_instances(self, instances: Any) -> None:
        """Dispose of multiple instances."""
    def _dispose_instance(self, instance: Any) -> None:
        """Dispose of a single instance using event loop manager."""
