from .._utils import get_logger as get_logger
from .event_hooks import EventHook as EventHook, HookFunction as HookFunction
from .lifecycle_hooks import LifecycleHook as LifecycleHook, LifecycleHookFunction as LifecycleHookFunction
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class HookManager:
    """
    Central manager for all types of hooks in the DI system.

    Coordinates event hooks, lifecycle hooks, and provides a unified
    interface for hook management.
    """
    _event_manager: Incomplete
    _lifecycle_manager: Incomplete
    def __init__(self) -> None:
        """Initialize the central hook manager."""
    def register_event_hook(self, event: EventHook, hook_function: HookFunction) -> None:
        """Register an event hook."""
    def unregister_event_hook(self, event: EventHook, hook_function: HookFunction) -> bool:
        """Unregister an event hook."""
    def emit_event(self, event: EventHook, event_data: dict[str, Any]) -> None:
        """Emit an event."""
    def register_lifecycle_hook(self, hook: LifecycleHook, hook_function: LifecycleHookFunction) -> None:
        """Register a lifecycle hook."""
    def emit_lifecycle_event(self, hook: LifecycleHook, component: Any, **extra_data: Any) -> None:
        """Emit a lifecycle event."""
    def clear_all_hooks(self) -> None:
        """Clear all hooks of all types."""
    def get_event_hook_count(self, event: EventHook | None = None) -> int:
        """Get the number of registered event hooks."""
    def set_hooks_enabled(self, enabled: bool) -> None:
        """Enable or disable all hook execution."""
    def is_hooks_enabled(self) -> bool:
        """Check if hook execution is enabled."""
    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all registered hooks."""

_global_hook_manager: Incomplete

def get_global_hook_manager() -> HookManager:
    """Get the global hook manager instance."""
def register_event_hook(event: EventHook, hook_function: HookFunction) -> None:
    """Register an event hook using the global manager."""
def register_lifecycle_hook(hook: LifecycleHook, hook_function: LifecycleHookFunction) -> None:
    """Register a lifecycle hook using the global manager."""
def emit_event(event: EventHook, event_data: dict[str, Any]) -> None:
    """Emit an event using the global manager."""
def emit_lifecycle_event(hook: LifecycleHook, component: Any, **extra_data: Any) -> None:
    """Emit a lifecycle event using the global manager."""
def clear_all_hooks() -> None:
    """Clear all hooks using the global manager."""
def set_hooks_enabled(enabled: bool) -> None:
    """Enable or disable hooks using the global manager."""
def get_hooks_summary() -> dict[str, Any]:
    """Get hooks summary using the global manager."""
