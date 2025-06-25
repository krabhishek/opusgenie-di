import asyncio
import threading
from .._utils import get_logger as get_logger
from _typeshed import Incomplete
from collections.abc import Callable as Callable, Coroutine, Generator
from contextlib import contextmanager
from typing import Any, TypeVar

T = TypeVar('T')
logger: Incomplete

class EventLoopManager:
    """
    Centralized manager for asyncio event loops in the DI system.

    Provides guaranteed event loop access for async component lifecycle
    operations, with fallback handling for sync-only environments.
    """
    _lock: Incomplete
    _owned_loop: asyncio.AbstractEventLoop | None
    _loop_thread: threading.Thread | None
    def __init__(self) -> None:
        """Initialize the event loop manager."""
    def get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """
        Get the current event loop or create a new one if needed.

        Returns:
            Active event loop instance
        """
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
    def _run_in_background(self, coro: Coroutine[Any, Any, T]) -> T:
        """
        Run coroutine in background thread when already in async context.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine
        """
    def schedule_cleanup(self, cleanup_func: Callable[[], Any]) -> None:
        """
        Schedule a cleanup function to run async if possible, sync otherwise.

        Args:
            cleanup_func: Function to call for cleanup
        """
    @contextmanager
    def ensure_loop(self) -> Generator[asyncio.AbstractEventLoop, None, None]:
        """
        Context manager that ensures an event loop is available.

        Yields:
            Event loop instance
        """
    def is_async_available(self) -> bool:
        """
        Check if async operations are available in current context.

        Returns:
            True if async operations can be performed
        """
    def run_with_timeout(self, coro: Coroutine[Any, Any, T], timeout: float = 30.0) -> T:
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

_event_loop_manager: EventLoopManager | None
_manager_lock: Incomplete

def get_event_loop_manager() -> EventLoopManager:
    """
    Get the global event loop manager instance.

    Returns:
        EventLoopManager singleton
    """
def run_async_safely[T](coro: Coroutine[Any, Any, T]) -> T | None:
    """
    Safely run async coroutine, with fallback handling.

    Args:
        coro: Coroutine to execute

    Returns:
        Result of coroutine or None if failed
    """
def schedule_async_cleanup(cleanup_func: Callable[[], Any]) -> None:
    """
    Schedule async cleanup function safely.

    Args:
        cleanup_func: Cleanup function to schedule
    """
