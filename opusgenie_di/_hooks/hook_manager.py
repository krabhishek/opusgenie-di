"""Central hook manager for coordinating all hook types."""

from typing import Any

from .._utils import get_logger
from .event_hooks import EventHook, HookFunction
from .lifecycle_hooks import LifecycleHook, LifecycleHookFunction

logger = get_logger(__name__)


class HookManager:
    """
    Central manager for all types of hooks in the DI system.

    Coordinates event hooks, lifecycle hooks, and provides a unified
    interface for hook management.
    """

    def __init__(self) -> None:
        """Initialize the central hook manager."""
        from .event_hooks import get_hook_manager
        from .lifecycle_hooks import get_lifecycle_hook_manager

        self._event_manager = get_hook_manager()
        self._lifecycle_manager = get_lifecycle_hook_manager()

    # Event hook methods

    def register_event_hook(
        self, event: EventHook, hook_function: HookFunction
    ) -> None:
        """Register an event hook."""
        self._event_manager.register_hook(event, hook_function)

    def unregister_event_hook(
        self, event: EventHook, hook_function: HookFunction
    ) -> bool:
        """Unregister an event hook."""
        return self._event_manager.unregister_hook(event, hook_function)

    def emit_event(self, event: EventHook, event_data: dict[str, Any]) -> None:
        """Emit an event."""
        self._event_manager.emit(event, event_data)

    # Lifecycle hook methods

    def register_lifecycle_hook(
        self, hook: LifecycleHook, hook_function: LifecycleHookFunction
    ) -> None:
        """Register a lifecycle hook."""
        self._lifecycle_manager.register_lifecycle_hook(hook, hook_function)

    def emit_lifecycle_event(
        self,
        hook: LifecycleHook,
        component: Any,
        **extra_data: Any,
    ) -> None:
        """Emit a lifecycle event."""
        self._lifecycle_manager.emit_lifecycle_event(hook, component, **extra_data)

    # Management methods

    def clear_all_hooks(self) -> None:
        """Clear all hooks of all types."""
        self._event_manager.clear_hooks()
        self._lifecycle_manager.clear_lifecycle_hooks()
        logger.debug("Cleared all hooks")

    def get_event_hook_count(self, event: EventHook | None = None) -> int:
        """Get the number of registered event hooks."""
        return self._event_manager.get_hook_count(event)

    def set_hooks_enabled(self, enabled: bool) -> None:
        """Enable or disable all hook execution."""
        self._event_manager.set_enabled(enabled)
        logger.debug("Set all hooks enabled", enabled=enabled)

    def is_hooks_enabled(self) -> bool:
        """Check if hook execution is enabled."""
        return self._event_manager.is_enabled()

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all registered hooks."""
        return {
            "event_hooks": {
                "total_count": self._event_manager.get_hook_count(),
                "registered_events": [
                    event.value for event in self._event_manager.get_registered_events()
                ],
            },
            "hooks_enabled": self._event_manager.is_enabled(),
        }


# Global hook manager instance
_global_hook_manager = HookManager()


def get_global_hook_manager() -> HookManager:
    """Get the global hook manager instance."""
    return _global_hook_manager


# Convenience functions for global hook management


def register_event_hook(event: EventHook, hook_function: HookFunction) -> None:
    """Register an event hook using the global manager."""
    _global_hook_manager.register_event_hook(event, hook_function)


def register_lifecycle_hook(
    hook: LifecycleHook, hook_function: LifecycleHookFunction
) -> None:
    """Register a lifecycle hook using the global manager."""
    _global_hook_manager.register_lifecycle_hook(hook, hook_function)


def emit_event(event: EventHook, event_data: dict[str, Any]) -> None:
    """Emit an event using the global manager."""
    _global_hook_manager.emit_event(event, event_data)


def emit_lifecycle_event(
    hook: LifecycleHook,
    component: Any,
    **extra_data: Any,
) -> None:
    """Emit a lifecycle event using the global manager."""
    _global_hook_manager.emit_lifecycle_event(hook, component, **extra_data)


def clear_all_hooks() -> None:
    """Clear all hooks using the global manager."""
    _global_hook_manager.clear_all_hooks()


def set_hooks_enabled(enabled: bool) -> None:
    """Enable or disable hooks using the global manager."""
    _global_hook_manager.set_hooks_enabled(enabled)


def get_hooks_summary() -> dict[str, Any]:
    """Get hooks summary using the global manager."""
    return _global_hook_manager.get_summary()
