"""Event loop manager for async lifecycle coordination in DI system."""

import asyncio
from collections.abc import Callable, Coroutine, Generator
from contextlib import contextmanager
import threading
from typing import Any, TypeVar

from .._utils import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


class EventLoopManager:
    """
    Centralized manager for asyncio event loops in the DI system.

    Provides guaranteed event loop access for async component lifecycle
    operations, with fallback handling for sync-only environments.
    """

    def __init__(self) -> None:
        """Initialize the event loop manager."""
        self._lock = threading.RLock()
        self._owned_loop: asyncio.AbstractEventLoop | None = None
        self._loop_thread: threading.Thread | None = None

    def get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """
        Get the current event loop or create a new one if needed.

        Returns:
            Active event loop instance
        """
        try:
            # Try to get existing loop
            return asyncio.get_running_loop()
        except RuntimeError:
            # No loop running, check if we have one in this thread
            try:
                return asyncio.get_event_loop()
            except RuntimeError:
                # Create new loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                logger.debug(
                    "Created new event loop for thread", thread_id=threading.get_ident()
                )
                return loop

    def run_async_sync(self, coro: Coroutine[Any, Any, T]) -> T:
        """
        Run an async coroutine synchronously.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine

        Raises:
            RuntimeError: If unable to execute async code
        """
        try:
            # Try to get running loop
            asyncio.get_running_loop()
            # We're already in an async context, need to handle this differently
            return self._run_in_background(coro)
        except RuntimeError:
            # No loop running, we can use asyncio.run
            return asyncio.run(coro)

    def _run_in_background(self, coro: Coroutine[Any, Any, T]) -> T:
        """
        Run coroutine in background thread when already in async context.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine
        """
        import concurrent.futures

        def run_in_new_loop() -> T:
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_loop)
            return future.result()

    def schedule_cleanup(self, cleanup_func: Callable[[], Any]) -> None:
        """
        Schedule a cleanup function to run async if possible, sync otherwise.

        Args:
            cleanup_func: Function to call for cleanup
        """
        if asyncio.iscoroutinefunction(cleanup_func):
            try:
                loop = asyncio.get_running_loop()
                # Schedule as task
                loop.create_task(cleanup_func())
                logger.debug("Scheduled async cleanup as task")
            except RuntimeError:
                # No running loop, try to run synchronously
                try:
                    self.run_async_sync(cleanup_func())
                    logger.debug("Executed async cleanup synchronously")
                except Exception as e:
                    logger.warning(
                        "Failed to execute async cleanup",
                        error=str(e),
                        cleanup_func=cleanup_func.__name__,
                    )
        else:
            # Sync function, call directly
            try:
                cleanup_func()
                logger.debug("Executed sync cleanup")
            except Exception as e:
                logger.error(
                    "Failed to execute sync cleanup",
                    error=str(e),
                    cleanup_func=cleanup_func.__name__,
                )

    @contextmanager
    def ensure_loop(self) -> Generator[asyncio.AbstractEventLoop, None, None]:
        """
        Context manager that ensures an event loop is available.

        Yields:
            Event loop instance
        """
        with self._lock:
            loop = self.get_or_create_loop()
            try:
                yield loop
            finally:
                # Only close loop if we created it
                if self._owned_loop is loop:
                    if not loop.is_closed():
                        loop.close()
                    self._owned_loop = None

    def is_async_available(self) -> bool:
        """
        Check if async operations are available in current context.

        Returns:
            True if async operations can be performed
        """
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            try:
                asyncio.get_event_loop()
                return True
            except RuntimeError:
                return False

    def run_with_timeout(
        self, coro: Coroutine[Any, Any, T], timeout: float = 30.0
    ) -> T:
        """
        Run coroutine with timeout.

        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds

        Returns:
            Result of the coroutine

        Raises:
            asyncio.TimeoutError: If operation times out
        """

        async def _with_timeout() -> T:
            return await asyncio.wait_for(coro, timeout=timeout)

        return self.run_async_sync(_with_timeout())


# Global event loop manager instance
_event_loop_manager: EventLoopManager | None = None
_manager_lock = threading.RLock()


def get_event_loop_manager() -> EventLoopManager:
    """
    Get the global event loop manager instance.

    Returns:
        EventLoopManager singleton
    """
    global _event_loop_manager

    if _event_loop_manager is None:
        with _manager_lock:
            if _event_loop_manager is None:
                _event_loop_manager = EventLoopManager()
                logger.debug("Created global event loop manager")

    return _event_loop_manager


def run_async_safely[T](coro: Coroutine[Any, Any, T]) -> T | None:
    """
    Safely run async coroutine, with fallback handling.

    Args:
        coro: Coroutine to execute

    Returns:
        Result of coroutine or None if failed
    """
    try:
        manager = get_event_loop_manager()
        return manager.run_async_sync(coro)
    except Exception as e:
        logger.warning(
            "Failed to run async coroutine safely",
            error=str(e),
            coro_name=getattr(coro, "__name__", str(coro)),
        )
        return None


def schedule_async_cleanup(cleanup_func: Callable[[], Any]) -> None:
    """
    Schedule async cleanup function safely.

    Args:
        cleanup_func: Cleanup function to schedule
    """
    manager = get_event_loop_manager()
    manager.schedule_cleanup(cleanup_func)
