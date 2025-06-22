"""Lifecycle hooks for component lifecycle management."""

from collections.abc import Callable
from enum import Enum
from typing import Any

from .._base import LifecycleStage
from .._utils import get_logger
from .event_hooks import EventHookManager

logger = get_logger(__name__)


class LifecycleHook(Enum):
    """Enumeration of lifecycle hooks."""

    # Component lifecycle hooks
    BEFORE_INITIALIZATION = "before_initialization"
    AFTER_INITIALIZATION = "after_initialization"
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"
    BEFORE_CLEANUP = "before_cleanup"
    AFTER_CLEANUP = "after_cleanup"

    # Error hooks
    INITIALIZATION_ERROR = "initialization_error"
    START_ERROR = "start_error"
    STOP_ERROR = "stop_error"
    CLEANUP_ERROR = "cleanup_error"


# Type alias for lifecycle hook functions
LifecycleHookFunction = Callable[[Any, dict[str, Any]], None]


class LifecycleHookManager:
    """
    Manager for component lifecycle hooks.

    Provides hooks for component lifecycle events to enable
    custom behavior during component initialization, startup,
    shutdown, and cleanup.
    """

    def __init__(self) -> None:
        """Initialize the lifecycle hook manager."""
        self._hook_manager = EventHookManager()

    def register_lifecycle_hook(
        self, hook: LifecycleHook, hook_function: LifecycleHookFunction
    ) -> None:
        """
        Register a lifecycle hook function.

        Args:
            hook: The lifecycle hook to register for
            hook_function: Function to call during lifecycle event
        """

        def wrapper(event_data: dict[str, Any]) -> None:
            component = event_data.get("component")
            hook_function(component, event_data)

        # Convert LifecycleHook to EventHook by using the value as event name
        from .event_hooks import EventHook

        # Create a synthetic event hook for lifecycle events
        try:
            event_hook = EventHook(hook.value)
        except ValueError:
            # If the lifecycle hook doesn't have a corresponding event hook,
            # we'll use the generic LIFECYCLE_STAGE_CHANGED event
            event_hook = EventHook.LIFECYCLE_STAGE_CHANGED

        self._hook_manager.register_hook(event_hook, wrapper)

    def emit_lifecycle_event(
        self,
        hook: LifecycleHook,
        component: Any,
        stage: LifecycleStage | None = None,
        **extra_data: Any,
    ) -> None:
        """
        Emit a lifecycle event.

        Args:
            hook: The lifecycle hook to emit
            component: The component involved in the lifecycle event
            stage: Optional lifecycle stage
            **extra_data: Additional data to include in the event
        """
        event_data = {
            "component": component,
            "component_type": type(component).__name__,
            "component_id": getattr(component, "component_id", None),
            "lifecycle_hook": hook.value,
            "lifecycle_stage": stage.value if stage else None,
            **extra_data,
        }

        from .event_hooks import EventHook

        try:
            event_hook = EventHook(hook.value)
        except ValueError:
            event_hook = EventHook.LIFECYCLE_STAGE_CHANGED

        self._hook_manager.emit(event_hook, event_data)

    def execute_lifecycle_hook(
        self,
        hook: LifecycleHook,
        component: Any,
        stage: LifecycleStage | None = None,
        **extra_data: Any,
    ) -> None:
        """
        Execute lifecycle hooks for a component.

        This is a convenience method that emits the lifecycle event.

        Args:
            hook: The lifecycle hook to execute
            component: The component involved in the lifecycle event
            stage: Optional lifecycle stage
            **extra_data: Additional data to include in the event
        """
        self.emit_lifecycle_event(hook, component, stage, **extra_data)

    def clear_lifecycle_hooks(self) -> None:
        """Clear all lifecycle hooks."""
        self._hook_manager.clear_hooks()


# Global lifecycle hook manager
_global_lifecycle_manager = LifecycleHookManager()


def get_lifecycle_hook_manager() -> LifecycleHookManager:
    """Get the global lifecycle hook manager."""
    return _global_lifecycle_manager


def register_lifecycle_hook(
    hook: LifecycleHook, hook_function: LifecycleHookFunction
) -> None:
    """
    Register a lifecycle hook function.

    This is a convenience function that uses the global lifecycle manager.

    Args:
        hook: The lifecycle hook to register for
        hook_function: Function to call during lifecycle event
    """
    _global_lifecycle_manager.register_lifecycle_hook(hook, hook_function)


def emit_lifecycle_event(
    hook: LifecycleHook,
    component: Any,
    stage: LifecycleStage | None = None,
    **extra_data: Any,
) -> None:
    """
    Emit a lifecycle event.

    This is a convenience function that uses the global lifecycle manager.

    Args:
        hook: The lifecycle hook to emit
        component: The component involved in the lifecycle event
        stage: Optional lifecycle stage
        **extra_data: Additional data to include in the event
    """
    _global_lifecycle_manager.emit_lifecycle_event(hook, component, stage, **extra_data)
