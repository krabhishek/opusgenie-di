from .._base import LifecycleStage as LifecycleStage
from .._utils import get_logger as get_logger
from _typeshed import Incomplete
from collections.abc import Callable
from enum import Enum
from typing import Any

logger: Incomplete

class LifecycleHook(Enum):
    """Enumeration of lifecycle hooks."""
    BEFORE_INITIALIZATION = 'before_initialization'
    AFTER_INITIALIZATION = 'after_initialization'
    BEFORE_START = 'before_start'
    AFTER_START = 'after_start'
    BEFORE_STOP = 'before_stop'
    AFTER_STOP = 'after_stop'
    BEFORE_CLEANUP = 'before_cleanup'
    AFTER_CLEANUP = 'after_cleanup'
    INITIALIZATION_ERROR = 'initialization_error'
    START_ERROR = 'start_error'
    STOP_ERROR = 'stop_error'
    CLEANUP_ERROR = 'cleanup_error'
LifecycleHookFunction = Callable[[Any, dict[str, Any]], None]

class LifecycleHookManager:
    """
    Manager for component lifecycle hooks.

    Provides hooks for component lifecycle events to enable
    custom behavior during component initialization, startup,
    shutdown, and cleanup.
    """
    _hooks: dict[LifecycleHook, list[LifecycleHookFunction]]
    def __init__(self) -> None:
        """Initialize the lifecycle hook manager."""
    def register_lifecycle_hook(self, hook: LifecycleHook, hook_function: LifecycleHookFunction) -> None:
        """
        Register a lifecycle hook function.

        Args:
            hook: The lifecycle hook to register for
            hook_function: Function to call during lifecycle event
        """
    def emit_lifecycle_event(self, hook: LifecycleHook, component: Any, stage: LifecycleStage | None = None, **extra_data: Any) -> None:
        """
        Emit a lifecycle event.

        Args:
            hook: The lifecycle hook to emit
            component: The component involved in the lifecycle event
            stage: Optional lifecycle stage
            **extra_data: Additional data to include in the event
        """
    def execute_lifecycle_hook(self, hook: LifecycleHook, component: Any, stage: LifecycleStage | None = None, **extra_data: Any) -> None:
        """
        Execute lifecycle hooks for a component.

        This is a convenience method that emits the lifecycle event.

        Args:
            hook: The lifecycle hook to execute
            component: The component involved in the lifecycle event
            stage: Optional lifecycle stage
            **extra_data: Additional data to include in the event
        """
    def clear_lifecycle_hooks(self) -> None:
        """Clear all lifecycle hooks."""

_global_lifecycle_manager: Incomplete

def get_lifecycle_hook_manager() -> LifecycleHookManager:
    """Get the global lifecycle hook manager."""
def register_lifecycle_hook(hook: LifecycleHook, hook_function: LifecycleHookFunction) -> None:
    """
    Register a lifecycle hook function.

    This is a convenience function that uses the global lifecycle manager.

    Args:
        hook: The lifecycle hook to register for
        hook_function: Function to call during lifecycle event
    """
def emit_lifecycle_event(hook: LifecycleHook, component: Any, stage: LifecycleStage | None = None, **extra_data: Any) -> None:
    """
    Emit a lifecycle event.

    This is a convenience function that uses the global lifecycle manager.

    Args:
        hook: The lifecycle hook to emit
        component: The component involved in the lifecycle event
        stage: Optional lifecycle stage
        **extra_data: Additional data to include in the event
    """
