"""Event hooks for extensibility in the dependency injection system."""

from collections import defaultdict
from collections.abc import Callable
from enum import Enum
from typing import Any

from .._utils import get_logger, log_error

logger = get_logger(__name__)


class EventHook(Enum):
    """Enumeration of available event hooks."""

    # Context events
    CONTEXT_CREATED = "context_created"
    CONTEXT_DESTROYED = "context_destroyed"

    # Component events
    COMPONENT_REGISTERED = "component_registered"
    COMPONENT_UNREGISTERED = "component_unregistered"
    COMPONENT_RESOLVED = "component_resolved"
    COMPONENT_RESOLUTION_FAILED = "component_resolution_failed"

    # Module events
    MODULE_REGISTERED = "module_registered"
    MODULE_BUILT = "module_built"

    # Import events
    IMPORT_RESOLVED = "import_resolved"
    IMPORT_FAILED = "import_failed"

    # Lifecycle events
    LIFECYCLE_STAGE_CHANGED = "lifecycle_stage_changed"

    # Error events
    ERROR_OCCURRED = "error_occurred"


# Type alias for hook functions
HookFunction = Callable[[dict[str, Any]], None]


class EventHookManager:
    """
    Manager for event hooks in the dependency injection system.

    Provides extension points for external systems to hook into
    DI operations and events.
    """

    def __init__(self) -> None:
        """Initialize the hook manager."""
        self._hooks: dict[EventHook, list[HookFunction]] = defaultdict(list)
        self._enabled = True

    def register_hook(self, event: EventHook, hook_function: HookFunction) -> None:
        """
        Register a hook function for an event.

        Args:
            event: The event to hook into
            hook_function: Function to call when event occurs
        """
        if not callable(hook_function):
            raise ValueError("Hook function must be callable")

        self._hooks[event].append(hook_function)
        logger.debug(
            "Registered event hook",
            event_type=event.value,
            hook_function=hook_function.__name__,
        )

    def unregister_hook(self, event: EventHook, hook_function: HookFunction) -> bool:
        """
        Unregister a hook function for an event.

        Args:
            event: The event to unhook from
            hook_function: Function to remove

        Returns:
            True if the hook was removed, False if it wasn't registered
        """
        if hook_function in self._hooks[event]:
            self._hooks[event].remove(hook_function)
            logger.debug(
                "Unregistered event hook",
                event_type=event.value,
                hook_function=hook_function.__name__,
            )
            return True
        return False

    def emit(self, event: EventHook, event_data: dict[str, Any]) -> None:
        """
        Emit an event to all registered hooks.

        Args:
            event: The event to emit
            event_data: Data to pass to hook functions
        """
        if not self._enabled:
            return

        if event not in self._hooks or not self._hooks[event]:
            return

        logger.debug(
            "Emitting event",
            event_type=event.value,
            hook_count=len(self._hooks[event]),
            event_data_keys=list(event_data.keys()),
        )

        for hook_function in self._hooks[event]:
            try:
                hook_function(event_data)
            except Exception as e:
                log_error(
                    "event_hook_execution",
                    e,
                    hook_function=hook_function.__name__,
                    event_type=event.value,
                )
                # Continue with other hooks even if one fails

    def get_hook_count(self, event: EventHook | None = None) -> int:
        """
        Get the number of registered hooks.

        Args:
            event: Optional event to filter by

        Returns:
            Number of registered hooks
        """
        if event is None:
            return sum(len(hooks) for hooks in self._hooks.values())
        return len(self._hooks[event])

    def clear_hooks(self, event: EventHook | None = None) -> None:
        """
        Clear hooks for an event or all events.

        Args:
            event: Optional event to clear hooks for, None for all events
        """
        if event is None:
            self._hooks.clear()
            logger.debug("Cleared all event hooks")
        else:
            self._hooks[event].clear()
            logger.debug("Cleared event hooks", event_type=event.value)

    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable hook execution.

        Args:
            enabled: Whether to enable hook execution
        """
        self._enabled = enabled
        logger.debug("Set hook execution enabled", enabled=enabled)

    def is_enabled(self) -> bool:
        """Check if hook execution is enabled."""
        return self._enabled

    def get_registered_events(self) -> list[EventHook]:
        """Get a list of events that have registered hooks."""
        return [event for event, hooks in self._hooks.items() if hooks]


# Global hook manager instance
_global_hook_manager = EventHookManager()


def get_hook_manager() -> EventHookManager:
    """Get the global hook manager instance."""
    return _global_hook_manager


def register_hook(event: EventHook, hook_function: HookFunction) -> None:
    """
    Register a hook function for an event.

    This is a convenience function that uses the global hook manager.

    Args:
        event: The event to hook into
        hook_function: Function to call when event occurs
    """
    _global_hook_manager.register_hook(event, hook_function)


def unregister_hook(event: EventHook, hook_function: HookFunction) -> bool:
    """
    Unregister a hook function for an event.

    This is a convenience function that uses the global hook manager.

    Args:
        event: The event to unhook from
        hook_function: Function to remove

    Returns:
        True if the hook was removed, False if it wasn't registered
    """
    return _global_hook_manager.unregister_hook(event, hook_function)


def emit_event(event: EventHook, event_data: dict[str, Any]) -> None:
    """
    Emit an event to all registered hooks.

    This is a convenience function that uses the global hook manager.

    Args:
        event: The event to emit
        event_data: Data to pass to hook functions
    """
    _global_hook_manager.emit(event, event_data)


def clear_all_hooks() -> None:
    """Clear all registered hooks."""
    _global_hook_manager.clear_hooks()


def set_hooks_enabled(enabled: bool) -> None:
    """Enable or disable hook execution globally."""
    _global_hook_manager.set_enabled(enabled)
