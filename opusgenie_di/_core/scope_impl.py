"""Scope manager implementation for component lifecycle management."""

import asyncio
from collections import defaultdict
from collections.abc import Callable, Coroutine, Generator
from contextlib import contextmanager
from contextvars import ContextVar
import threading
from typing import Any, TypeVar
import uuid
from weakref import WeakValueDictionary

from .._base import ComponentScope
from .._utils import get_logger, log_error
from .event_loop_manager import get_event_loop_manager, run_async_safely
from .exceptions import ScopeError
from .scope_interface import ScopeManagerInterface

T = TypeVar("T")

logger = get_logger(__name__)

# Context variable to track the current scope
_current_scope: ContextVar[str | None] = ContextVar("current_scope", default=None)


class ScopeManager(ScopeManagerInterface):
    """
    Implementation of scope manager for component lifecycle management.

    Manages component instances according to their configured scope,
    providing proper caching and disposal strategies.
    """

    def __init__(self, lifecycle_callback: Callable[..., None] | None = None) -> None:
        """
        Initialize the scope manager.

        Args:
            lifecycle_callback: Optional callback for lifecycle events.
                                Called with (event_name, **kwargs)
        """
        self._lock = threading.RLock()
        self._singletons: dict[str, Any] = {}
        self._scoped_instances: dict[str, dict[str, Any]] = defaultdict(dict)
        self._disposable_instances: WeakValueDictionary[int, Any] = (
            WeakValueDictionary()
        )
        self._lifecycle_callback = lifecycle_callback

    def _trigger_lifecycle_event(self, event: str, **kwargs: Any) -> None:
        """Trigger a lifecycle event callback if configured."""
        if self._lifecycle_callback is not None:
            try:
                self._lifecycle_callback(event, **kwargs)
            except Exception as e:
                logger.warning(
                    "Error in lifecycle callback", event=event, error=str(e), **kwargs
                )

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
        try:
            with self._lock:
                if scope == ComponentScope.SINGLETON:
                    return self._get_or_create_singleton(key, factory)
                if scope == ComponentScope.TRANSIENT:
                    return self._create_transient(factory)
                if scope == ComponentScope.SCOPED:
                    return self._get_or_create_scoped(key, factory)
                if scope == ComponentScope.FACTORY:
                    return self._create_factory(factory)
                raise ScopeError(
                    f"Unsupported scope: {scope}",
                    scope=scope.value,
                    details=f"Scope {scope.value} is not supported by this manager",
                )

        except Exception as e:
            log_error(
                "get_or_create",
                e,
                component_type=None,
            )
            raise ScopeError(
                f"Failed to get or create instance for key '{key}'",
                scope=scope.value,
                details=str(e),
            ) from e

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
        try:
            # For async operations, we need to handle locking carefully
            # to avoid blocking the event loop
            if scope == ComponentScope.SINGLETON:
                return await self._get_or_create_singleton_async(key, factory)
            if scope == ComponentScope.TRANSIENT:
                return await self._create_transient_async(factory)
            if scope == ComponentScope.SCOPED:
                return await self._get_or_create_scoped_async(key, factory)
            if scope == ComponentScope.FACTORY:
                return await self._create_factory_async(factory)
            raise ScopeError(
                f"Unsupported scope: {scope}",
                scope=scope.value,
                details=f"Scope {scope.value} is not supported by this manager",
            )

        except Exception as e:
            log_error(
                "get_or_create_async",
                e,
                component_type=None,
            )
            raise ScopeError(
                f"Failed to get or create instance async for key '{key}'",
                scope=scope.value,
                details=str(e),
            ) from e

    def clear_scope(self, scope: ComponentScope) -> None:
        """
        Clear all instances for a specific scope.

        Args:
            scope: Scope to clear
        """
        with self._lock:
            if scope == ComponentScope.SINGLETON:
                self._dispose_instances(self._singletons.values())
                self._singletons.clear()
                logger.debug("Cleared singleton scope")
            elif scope == ComponentScope.SCOPED:
                for scoped_dict in self._scoped_instances.values():
                    self._dispose_instances(scoped_dict.values())
                self._scoped_instances.clear()
                logger.debug("Cleared scoped instances")
            # Transient and factory instances are not cached, so nothing to clear

    def clear_all(self) -> None:
        """Clear all cached instances across all scopes."""
        with self._lock:
            # Dispose of all singleton instances
            self._dispose_instances(self._singletons.values())
            self._singletons.clear()

            # Dispose of all scoped instances
            for scoped_dict in self._scoped_instances.values():
                self._dispose_instances(scoped_dict.values())
            self._scoped_instances.clear()

            logger.debug("Cleared all cached instances")

    def dispose(self, instance: T | None = None) -> None:
        """
        Dispose of a component instance and clean up resources.

        Args:
            instance: Component instance to dispose. If None, disposes all instances.
        """
        if instance is None:
            # Dispose all instances (clear all scopes)
            self.clear_all()
        else:
            self._dispose_instance(instance)

    def has_instance(self, key: str, scope: ComponentScope) -> bool:
        """
        Check if an instance exists for the given key and scope.

        Args:
            key: Instance key
            scope: Component scope

        Returns:
            True if instance exists
        """
        with self._lock:
            if scope == ComponentScope.SINGLETON:
                return key in self._singletons
            if scope == ComponentScope.SCOPED:
                return any(
                    key in scoped_dict
                    for scoped_dict in self._scoped_instances.values()
                )
            # Transient and factory instances are not cached
            return False

    def get_instance_count(self, scope: ComponentScope | None = None) -> int:
        """
        Get the number of cached instances.

        Args:
            scope: Optional scope to filter by, None for all scopes

        Returns:
            Number of cached instances
        """
        with self._lock:
            if scope is None:
                total = len(self._singletons)
                total += sum(
                    len(scoped_dict) for scoped_dict in self._scoped_instances.values()
                )
                return total
            if scope == ComponentScope.SINGLETON:
                return len(self._singletons)
            if scope == ComponentScope.SCOPED:
                return sum(
                    len(scoped_dict) for scoped_dict in self._scoped_instances.values()
                )
            # Transient and factory instances are not cached
            return 0

    def get_scopes(self) -> list[ComponentScope]:
        """
        Get all scopes that have cached instances.

        Returns:
            List of scopes with instances
        """
        scopes = []
        with self._lock:
            if self._singletons:
                scopes.append(ComponentScope.SINGLETON)
            if any(self._scoped_instances.values()):
                scopes.append(ComponentScope.SCOPED)
        return scopes

    def create_or_get_instance(
        self,
        component_type: type[T],
        scope: ComponentScope,
        factory: Callable[[], T],
    ) -> T:
        """
        Convenience method that matches test expectations.

        Args:
            component_type: Component type (used to generate key)
            scope: Component scope for lifecycle management
            factory: Factory function to create new instances

        Returns:
            Component instance
        """
        key = component_type.__name__
        return self.get_or_create(key, factory, scope)

    @contextmanager
    def create_scope(self) -> Generator[str, None, None]:
        """
        Create a new scope context.

        Returns:
            Context manager that provides a new scope for scoped components
        """
        scope_id = str(uuid.uuid4())
        token = _current_scope.set(scope_id)
        try:
            logger.debug("Created scope context", scope_id=scope_id)
            yield scope_id
        finally:
            # Clean up scope when exiting
            with self._lock:
                if scope_id in self._scoped_instances:
                    self._dispose_instances(self._scoped_instances[scope_id].values())
                    del self._scoped_instances[scope_id]
            _current_scope.reset(token)
            logger.debug("Disposed scope context", scope_id=scope_id)

    def has_active_scope(self) -> bool:
        """
        Check if there's currently an active scope context.

        Returns:
            True if inside a scope context, False otherwise
        """
        return _current_scope.get() is not None

    # Private methods

    def _get_or_create_singleton(self, key: str, factory: Callable[[], T]) -> T:
        """Get or create a singleton instance."""
        if key in self._singletons:
            return self._singletons[key]  # type: ignore[no-any-return]

        instance = factory()
        self._singletons[key] = instance
        self._track_disposable(instance)
        logger.debug(
            "Created singleton instance", key=key, instance_type=type(instance).__name__
        )

        # Trigger lifecycle event
        self._trigger_lifecycle_event(
            "instance_created",
            component_type=type(instance).__name__,
            scope=ComponentScope.SINGLETON,
            key=key,
        )

        return instance

    async def _get_or_create_singleton_async(
        self, key: str, factory: Callable[[], Coroutine[Any, Any, T]]
    ) -> T:
        """Asynchronously get or create a singleton instance."""
        # Check if instance already exists (non-blocking)
        with self._lock:
            if key in self._singletons:
                return self._singletons[key]  # type: ignore[no-any-return]

        # Create instance asynchronously
        instance = await factory()

        # Store the instance (with lock)
        with self._lock:
            # Double-check in case another coroutine created it
            if key in self._singletons:
                # Another coroutine beat us to it, dispose our instance and return the existing one
                self._dispose_instance(instance)
                return self._singletons[key]  # type: ignore[no-any-return]

            self._singletons[key] = instance
            self._track_disposable(instance)
            logger.debug(
                "Created singleton instance async",
                key=key,
                instance_type=type(instance).__name__,
            )
            return instance

    def _create_transient(self, factory: Callable[[], T]) -> T:
        """Create a transient instance."""
        instance = factory()
        self._track_disposable(instance)
        logger.debug(
            "Created transient instance", instance_type=type(instance).__name__
        )
        return instance

    async def _create_transient_async(
        self, factory: Callable[[], Coroutine[Any, Any, T]]
    ) -> T:
        """Asynchronously create a transient instance."""
        instance = await factory()
        self._track_disposable(instance)
        logger.debug(
            "Created transient instance async", instance_type=type(instance).__name__
        )
        return instance

    def _get_or_create_scoped(self, key: str, factory: Callable[[], T]) -> T:
        """Get or create a scoped instance."""
        current_scope = _current_scope.get()

        # If no scope is active, behave like transient
        if current_scope is None:
            return self._create_transient(factory)

        if key in self._scoped_instances[current_scope]:
            return self._scoped_instances[current_scope][key]  # type: ignore[no-any-return]

        instance = factory()
        self._scoped_instances[current_scope][key] = instance
        self._track_disposable(instance)
        logger.debug(
            "Created scoped instance",
            key=key,
            scope=current_scope,
            instance_type=type(instance).__name__,
        )

        # Trigger lifecycle event
        self._trigger_lifecycle_event(
            "instance_created",
            component_type=type(instance).__name__,
            scope=ComponentScope.SCOPED,
            key=key,
            scope_id=current_scope,
        )

        return instance

    async def _get_or_create_scoped_async(
        self, key: str, factory: Callable[[], Coroutine[Any, Any, T]]
    ) -> T:
        """Asynchronously get or create a scoped instance."""
        current_scope = _current_scope.get()

        # If no scope is active, behave like transient
        if current_scope is None:
            return await self._create_transient_async(factory)

        # Check if instance already exists
        with self._lock:
            if key in self._scoped_instances[current_scope]:
                return self._scoped_instances[current_scope][key]  # type: ignore[no-any-return]

        # Create instance asynchronously
        instance = await factory()

        # Store the instance
        with self._lock:
            # Double-check in case another coroutine created it
            if key in self._scoped_instances[current_scope]:
                self._dispose_instance(instance)
                return self._scoped_instances[current_scope][key]  # type: ignore[no-any-return]

            self._scoped_instances[current_scope][key] = instance
            self._track_disposable(instance)
            logger.debug(
                "Created scoped instance async",
                key=key,
                scope=current_scope,
                instance_type=type(instance).__name__,
            )
            return instance

    def _create_factory(self, factory: Callable[[], T]) -> T:
        """Create an instance using factory method."""
        instance = factory()
        self._track_disposable(instance)
        logger.debug("Created factory instance", instance_type=type(instance).__name__)
        return instance

    async def _create_factory_async(
        self, factory: Callable[[], Coroutine[Any, Any, T]]
    ) -> T:
        """Asynchronously create an instance using factory method."""
        instance = await factory()
        self._track_disposable(instance)
        logger.debug(
            "Created factory instance async", instance_type=type(instance).__name__
        )
        return instance

    def _track_disposable(self, instance: Any) -> None:
        """Track an instance for disposal if it has disposal methods."""
        if self._has_disposal_methods(instance):
            self._disposable_instances[id(instance)] = instance

    def _has_disposal_methods(self, instance: Any) -> bool:
        """Check if an instance has disposal methods."""
        disposal_methods = ["cleanup", "dispose", "close", "shutdown"]
        return any(
            hasattr(instance, method) and callable(getattr(instance, method))
            for method in disposal_methods
        )

    def _dispose_instances(self, instances: Any) -> None:
        """Dispose of multiple instances."""
        for instance in instances:
            self._dispose_instance(instance)

    def _dispose_instance(self, instance: Any) -> None:
        """Dispose of a single instance using event loop manager."""
        try:
            get_event_loop_manager()

            # Try cleanup methods in order of preference
            cleanup_methods = [
                (
                    "cleanup",
                    instance.cleanup
                    if hasattr(instance, "cleanup") and callable(instance.cleanup)
                    else None,
                ),
                (
                    "dispose",
                    instance.dispose
                    if hasattr(instance, "dispose") and callable(instance.dispose)
                    else None,
                ),
                (
                    "close",
                    instance.close
                    if hasattr(instance, "close") and callable(instance.close)
                    else None,
                ),
                (
                    "shutdown",
                    instance.shutdown
                    if hasattr(instance, "shutdown") and callable(instance.shutdown)
                    else None,
                ),
            ]

            for method_name, method in cleanup_methods:
                if method is not None:
                    if asyncio.iscoroutinefunction(method):
                        # Handle async cleanup using event loop manager
                        result = run_async_safely(method())
                        if result is not None:  # Success
                            logger.debug(
                                "Disposed instance using async method",
                                instance_type=type(instance).__name__,
                                method=method_name,
                            )
                            # Trigger disposal lifecycle event for successful async disposal
                            self._trigger_lifecycle_event(
                                "instance_disposed",
                                component_type=type(instance).__name__,
                                method=method_name,
                            )
                        else:  # Failed
                            logger.warning(
                                "Failed to dispose instance using async method",
                                instance_type=type(instance).__name__,
                                method=method_name,
                            )
                    else:
                        # Handle sync cleanup
                        method()
                        logger.debug(
                            "Disposed instance using sync method",
                            instance_type=type(instance).__name__,
                            method=method_name,
                        )

                    # Trigger disposal lifecycle event
                    self._trigger_lifecycle_event(
                        "instance_disposed",
                        component_type=type(instance).__name__,
                        method=method_name,
                    )
                    break  # Only call the first available method
            else:
                logger.debug(
                    "No disposal method found for instance",
                    instance_type=type(instance).__name__,
                )

        except Exception as e:
            logger.warning(
                "Error disposing instance",
                instance_type=type(instance).__name__,
                error=str(e),
            )
