"""Hook system for extending the dependency injection framework."""

from .event_hooks import (
    EventHook,
    EventHookManager,
    HookFunction,
    clear_all_hooks,
    emit_event,
    get_hook_manager,
    register_hook,
    set_hooks_enabled,
    unregister_hook,
)
from .hook_manager import (
    HookManager,
    get_global_hook_manager,
    get_hooks_summary,
)
from .hook_manager import (
    clear_all_hooks as clear_all_hooks_global,
)
from .hook_manager import (
    emit_event as emit_event_global,
)
from .hook_manager import (
    emit_lifecycle_event as emit_lifecycle_event_global,
)
from .hook_manager import (
    register_event_hook as register_event_hook_global,
)
from .hook_manager import (
    register_lifecycle_hook as register_lifecycle_hook_global,
)
from .hook_manager import (
    set_hooks_enabled as set_hooks_enabled_global,
)
from .lifecycle_hooks import (
    LifecycleHook,
    LifecycleHookFunction,
    LifecycleHookManager,
    emit_lifecycle_event,
    get_lifecycle_hook_manager,
    register_lifecycle_hook,
)

__all__ = [
    # Event hooks
    "EventHook",
    "EventHookManager",
    "HookFunction",
    "get_hook_manager",
    "register_hook",
    "unregister_hook",
    "emit_event",
    "clear_all_hooks",
    "set_hooks_enabled",
    # Lifecycle hooks
    "LifecycleHook",
    "LifecycleHookFunction",
    "LifecycleHookManager",
    "get_lifecycle_hook_manager",
    "register_lifecycle_hook",
    "emit_lifecycle_event",
    # Central hook manager
    "HookManager",
    "get_global_hook_manager",
    "register_event_hook_global",
    "register_lifecycle_hook_global",
    "emit_event_global",
    "emit_lifecycle_event_global",
    "clear_all_hooks_global",
    "set_hooks_enabled_global",
    "get_hooks_summary",
]
