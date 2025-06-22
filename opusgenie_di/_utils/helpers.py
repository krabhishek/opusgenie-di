"""General helper utilities for the dependency injection system."""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def ensure_coroutine(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to ensure a function returns a coroutine.

    If the function is not async, it wraps the result in a coroutine.
    """

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result

    if asyncio.iscoroutinefunction(func):
        return func
    return async_wrapper


def run_async_in_sync(coro: Any) -> Any:
    """
    Run an async coroutine in a sync context.

    Handles both cases where an event loop is already running and when it's not.
    """
    try:
        # Try to get the current event loop
        asyncio.get_running_loop()
        # If we get here, there's already a running loop
        # We can't use asyncio.run(), so we need to create a new task
        import concurrent.futures

        # Run in a separate thread to avoid blocking the current loop
        def run_in_thread() -> Any:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    except RuntimeError:
        # No event loop is running, we can use asyncio.run()
        return asyncio.run(coro)


def safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    """
    Safely get an attribute from an object.

    Returns the default value if the attribute doesn't exist or if accessing it raises an exception.
    """
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def safe_isinstance(obj: Any, class_or_tuple: type | tuple[type, ...]) -> bool:
    """
    Safely check if an object is an instance of a type.

    Returns False if isinstance raises an exception.
    """
    try:
        return isinstance(obj, class_or_tuple)
    except Exception:
        return False


def safe_issubclass(cls: Any, class_or_tuple: type | tuple[type, ...]) -> bool:
    """
    Safely check if a class is a subclass of another class.

    Returns False if issubclass raises an exception.
    """
    try:
        return issubclass(cls, class_or_tuple)
    except Exception:
        return False


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """
    Merge multiple dictionaries, with later ones taking precedence.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def filter_none_values(d: dict[str, Any]) -> dict[str, Any]:
    """
    Filter out None values from a dictionary.

    Args:
        d: Dictionary to filter

    Returns:
        Dictionary with None values removed
    """
    return {k: v for k, v in d.items() if v is not None}


def get_class_name(cls: type | Any) -> str:
    """
    Get the name of a class, handling various edge cases.

    Args:
        cls: Class or object to get name from

    Returns:
        Class name as string
    """
    if hasattr(cls, "__name__"):
        return cls.__name__
    if hasattr(cls, "__class__"):
        return cls.__class__.__name__
    return str(cls)


def get_module_name(cls: type | Any) -> str:
    """
    Get the module name of a class.

    Args:
        cls: Class or object to get module name from

    Returns:
        Module name as string
    """
    if hasattr(cls, "__module__"):
        return cls.__module__
    if hasattr(cls, "__class__") and hasattr(cls.__class__, "__module__"):
        return cls.__class__.__module__
    return "unknown"


def create_unique_key(*parts: Any) -> str:
    """
    Create a unique key from multiple parts.

    Args:
        *parts: Parts to combine into a key

    Returns:
        Unique key string
    """
    return ":".join(str(part) for part in parts if part is not None)


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix
