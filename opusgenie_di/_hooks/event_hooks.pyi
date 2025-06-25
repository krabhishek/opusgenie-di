from .._utils import get_logger as get_logger, log_error as log_error
from _typeshed import Incomplete
from collections.abc import Callable
from enum import Enum
from typing import Any

logger: Incomplete

class EventHook(Enum):
    """Enumeration of available event hooks."""
    CONTEXT_CREATED = 'context_created'
    CONTEXT_DESTROYED = 'context_destroyed'
    COMPONENT_REGISTERED = 'component_registered'
    COMPONENT_UNREGISTERED = 'component_unregistered'
    COMPONENT_RESOLVED = 'component_resolved'
    COMPONENT_RESOLUTION_FAILED = 'component_resolution_failed'
    MODULE_REGISTERED = 'module_registered'
    MODULE_BUILT = 'module_built'
    IMPORT_RESOLVED = 'import_resolved'
    IMPORT_FAILED = 'import_failed'
    LIFECYCLE_STAGE_CHANGED = 'lifecycle_stage_changed'
    ERROR_OCCURRED = 'error_occurred'
HookFunction = Callable[[dict[str, Any]], None]

class EventHookManager:
    """
    Manager for event hooks in the dependency injection system.

    Provides extension points for external systems to hook into
    DI operations and events.
    """
    _hooks: dict[EventHook, list[HookFunction]]
    _enabled: bool
    def __init__(self) -> None:
        """Initialize the hook manager."""
    def register_hook(self, event: EventHook, hook_function: HookFunction) -> None:
        """
        Register a hook function for an event.

        Args:
            event: The event to hook into
            hook_function: Function to call when event occurs
        """
    def unregister_hook(self, event: EventHook, hook_function: HookFunction) -> bool:
        """
        Unregister a hook function for an event.

        Args:
            event: The event to unhook from
            hook_function: Function to remove

        Returns:
            True if the hook was removed, False if it wasn't registered
        """
    def emit(self, event: EventHook, event_data: dict[str, Any]) -> None:
        """
        Emit an event to all registered hooks.

        Args:
            event: The event to emit
            event_data: Data to pass to hook functions
        """
    def get_hook_count(self, event: EventHook | None = None) -> int:
        """
        Get the number of registered hooks.

        Args:
            event: Optional event to filter by

        Returns:
            Number of registered hooks
        """
    def clear_hooks(self, event: EventHook | None = None) -> None:
        """
        Clear hooks for an event or all events.

        Args:
            event: Optional event to clear hooks for, None for all events
        """
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable hook execution.

        Args:
            enabled: Whether to enable hook execution
        """
    def is_enabled(self) -> bool:
        """Check if hook execution is enabled."""
    def get_registered_events(self) -> list[EventHook]:
        """Get a list of events that have registered hooks."""

_global_hook_manager: Incomplete

def get_hook_manager() -> EventHookManager:
    """Get the global hook manager instance."""
def register_hook(event: EventHook, hook_function: HookFunction) -> None:
    """
    Register a hook function for an event.

    This is a convenience function that uses the global hook manager.

    Args:
        event: The event to hook into
        hook_function: Function to call when event occurs
    """
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
def emit_event(event: EventHook, event_data: dict[str, Any]) -> None:
    """
    Emit an event to all registered hooks.

    This is a convenience function that uses the global hook manager.

    Args:
        event: The event to emit
        event_data: Data to pass to hook functions
    """
def clear_all_hooks() -> None:
    """Clear all registered hooks."""
def set_hooks_enabled(enabled: bool) -> None:
    """Enable or disable hook execution globally."""
