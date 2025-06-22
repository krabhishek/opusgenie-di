"""Tests for central hook manager."""

from typing import Any

from opusgenie_di._hooks.event_hooks import EventHook
from opusgenie_di._hooks.hook_manager import (
    HookManager,
    clear_all_hooks,
    emit_event,
    emit_lifecycle_event,
    get_global_hook_manager,
    get_hooks_summary,
    register_event_hook,
    register_lifecycle_hook,
    set_hooks_enabled,
)
from opusgenie_di._hooks.lifecycle_hooks import LifecycleHook
from opusgenie_di._testing import MockComponent, reset_global_state


class TestHookManager:
    """Test HookManager class."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()
        self.manager = HookManager()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_init(self) -> None:
        """Test manager initialization."""
        manager = HookManager()

        assert hasattr(manager, "_event_manager")
        assert hasattr(manager, "_lifecycle_manager")
        assert manager._event_manager is not None
        assert manager._lifecycle_manager is not None

    def test_register_event_hook(self) -> None:
        """Test registering an event hook."""
        hook_called = []

        def event_hook(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)

        # Verify hook was registered by emitting event
        event_data = {"context_name": "test"}
        self.manager.emit_event(EventHook.CONTEXT_CREATED, event_data)

        assert len(hook_called) == 1
        assert hook_called[0] == event_data

    def test_unregister_event_hook(self) -> None:
        """Test unregistering an event hook."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        result = self.manager.unregister_event_hook(
            EventHook.CONTEXT_CREATED, event_hook
        )

        assert result is True

        # Try to unregister again
        result = self.manager.unregister_event_hook(
            EventHook.CONTEXT_CREATED, event_hook
        )
        assert result is False

    def test_emit_event(self) -> None:
        """Test emitting an event."""
        hook_called = []

        def event_hook(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        self.manager.register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)

        event_data = {"component_type": "TestComponent"}
        self.manager.emit_event(EventHook.COMPONENT_REGISTERED, event_data)

        assert len(hook_called) == 1
        assert hook_called[0] == event_data

    def test_register_lifecycle_hook(self) -> None:
        """Test registering a lifecycle hook."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(LifecycleHook.BEFORE_START, lifecycle_hook)

        # Verify hook was registered by emitting event
        test_component = MockComponent()
        self.manager.emit_lifecycle_event(LifecycleHook.BEFORE_START, test_component)

        assert len(hook_called) == 1
        assert hook_called[0][0] is test_component

    def test_emit_lifecycle_event(self) -> None:
        """Test emitting a lifecycle event."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(
            LifecycleHook.AFTER_INITIALIZATION, lifecycle_hook
        )

        test_component = MockComponent()
        self.manager.emit_lifecycle_event(
            LifecycleHook.AFTER_INITIALIZATION,
            test_component,
            initialized_at="2023-01-01T10:00:00",
        )

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert component is test_component
        assert event_data["initialized_at"] == "2023-01-01T10:00:00"

    def test_clear_all_hooks(self) -> None:
        """Test clearing all hooks."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            pass

        # Register various hooks
        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        self.manager.register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)
        self.manager.register_lifecycle_hook(LifecycleHook.BEFORE_START, lifecycle_hook)

        # Verify hooks are registered
        assert self.manager.get_event_hook_count() > 0

        self.manager.clear_all_hooks()

        # Verify all hooks are cleared
        assert self.manager.get_event_hook_count() == 0

    def test_get_event_hook_count_all(self) -> None:
        """Test getting total event hook count."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        self.manager.register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)

        assert self.manager.get_event_hook_count() == 2

    def test_get_event_hook_count_specific(self) -> None:
        """Test getting event hook count for specific event."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        self.manager.register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)

        assert self.manager.get_event_hook_count(EventHook.CONTEXT_CREATED) == 2
        assert self.manager.get_event_hook_count(EventHook.COMPONENT_REGISTERED) == 1

    def test_set_hooks_enabled(self) -> None:
        """Test enabling/disabling hooks."""
        assert self.manager.is_hooks_enabled() is True

        self.manager.set_hooks_enabled(False)
        assert self.manager.is_hooks_enabled() is False

        self.manager.set_hooks_enabled(True)
        assert self.manager.is_hooks_enabled() is True

    def test_hooks_disabled_no_execution(self) -> None:
        """Test that hooks don't execute when disabled."""
        hook_called = []

        def event_hook(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        self.manager.set_hooks_enabled(False)

        self.manager.emit_event(EventHook.CONTEXT_CREATED, {"test": "data"})

        assert len(hook_called) == 0

    def test_get_summary(self) -> None:
        """Test getting hook manager summary."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        # Register some hooks
        self.manager.register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        self.manager.register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)

        summary = self.manager.get_summary()

        assert "event_hooks" in summary
        assert summary["event_hooks"]["total_count"] == 2
        assert len(summary["event_hooks"]["registered_events"]) == 2
        assert "context_created" in summary["event_hooks"]["registered_events"]
        assert "component_registered" in summary["event_hooks"]["registered_events"]
        assert summary["hooks_enabled"] is True


class TestGlobalHookManagerFunctions:
    """Test global hook manager convenience functions."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_get_global_hook_manager(self) -> None:
        """Test getting global hook manager."""
        manager1 = get_global_hook_manager()
        manager2 = get_global_hook_manager()

        # Should return same instance
        assert manager1 is manager2
        assert isinstance(manager1, HookManager)

    def test_register_event_hook_global(self) -> None:
        """Test global register_event_hook function."""
        hook_called = []

        def event_hook(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        register_event_hook(EventHook.CONTEXT_CREATED, event_hook)

        # Verify hook was registered
        emit_event(EventHook.CONTEXT_CREATED, {"test": "data"})

        assert len(hook_called) == 1
        assert hook_called[0] == {"test": "data"}

    def test_register_lifecycle_hook_global(self) -> None:
        """Test global register_lifecycle_hook function."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        register_lifecycle_hook(LifecycleHook.BEFORE_START, lifecycle_hook)

        # Verify hook was registered
        test_component = MockComponent()
        emit_lifecycle_event(LifecycleHook.BEFORE_START, test_component)

        assert len(hook_called) == 1
        assert hook_called[0][0] is test_component

    def test_emit_event_global(self) -> None:
        """Test global emit_event function."""
        hook_called = []

        def event_hook(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        register_event_hook(EventHook.MODULE_REGISTERED, event_hook)

        event_data = {"module_name": "test_module"}
        emit_event(EventHook.MODULE_REGISTERED, event_data)

        assert len(hook_called) == 1
        assert hook_called[0] == event_data

    def test_emit_lifecycle_event_global(self) -> None:
        """Test global emit_lifecycle_event function."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        register_lifecycle_hook(LifecycleHook.AFTER_STOP, lifecycle_hook)

        test_component = MockComponent()
        emit_lifecycle_event(
            LifecycleHook.AFTER_STOP, test_component, stopped_at="2023-01-01T11:00:00"
        )

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert component is test_component
        assert event_data["stopped_at"] == "2023-01-01T11:00:00"

    def test_clear_all_hooks_global(self) -> None:
        """Test global clear_all_hooks function."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)

        manager = get_global_hook_manager()
        assert manager.get_event_hook_count() == 2

        clear_all_hooks()

        assert manager.get_event_hook_count() == 0

    def test_set_hooks_enabled_global(self) -> None:
        """Test global set_hooks_enabled function."""
        manager = get_global_hook_manager()

        assert manager.is_hooks_enabled() is True

        set_hooks_enabled(False)
        assert manager.is_hooks_enabled() is False

        set_hooks_enabled(True)
        assert manager.is_hooks_enabled() is True

    def test_get_hooks_summary_global(self) -> None:
        """Test global get_hooks_summary function."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        register_event_hook(EventHook.IMPORT_RESOLVED, event_hook)
        register_event_hook(EventHook.IMPORT_FAILED, event_hook)

        summary = get_hooks_summary()

        assert "event_hooks" in summary
        assert summary["event_hooks"]["total_count"] == 2
        assert summary["hooks_enabled"] is True


class TestHookManagerIntegration:
    """Test hook manager integration scenarios."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_mixed_hook_types(self) -> None:
        """Test using both event and lifecycle hooks together."""
        events_captured = []

        def event_hook(event_data: dict[str, Any]) -> None:
            events_captured.append(("event", event_data))

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            events_captured.append(("lifecycle", component, event_data))

        # Register both types of hooks
        register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)
        register_lifecycle_hook(LifecycleHook.BEFORE_INITIALIZATION, lifecycle_hook)
        register_lifecycle_hook(LifecycleHook.AFTER_INITIALIZATION, lifecycle_hook)

        # Emit various events
        emit_event(EventHook.CONTEXT_CREATED, {"context_name": "test"})

        test_component = MockComponent()
        emit_lifecycle_event(LifecycleHook.BEFORE_INITIALIZATION, test_component)

        emit_event(EventHook.COMPONENT_REGISTERED, {"component_type": "MockComponent"})
        emit_lifecycle_event(LifecycleHook.AFTER_INITIALIZATION, test_component)

        # Verify all events were captured
        assert len(events_captured) == 4
        assert events_captured[0][0] == "event"
        assert events_captured[1][0] == "lifecycle"
        assert events_captured[2][0] == "event"
        assert events_captured[3][0] == "lifecycle"

    def test_hook_manager_state_isolation(self) -> None:
        """Test that clearing hooks doesn't affect new registrations."""
        hook1_calls = []
        hook2_calls = []

        def hook1(event_data: dict[str, Any]) -> None:
            hook1_calls.append(event_data)

        def hook2(event_data: dict[str, Any]) -> None:
            hook2_calls.append(event_data)

        # Register first hook
        register_event_hook(EventHook.CONTEXT_CREATED, hook1)
        emit_event(EventHook.CONTEXT_CREATED, {"test": 1})

        assert len(hook1_calls) == 1

        # Clear all hooks
        clear_all_hooks()

        # Register second hook
        register_event_hook(EventHook.CONTEXT_CREATED, hook2)
        emit_event(EventHook.CONTEXT_CREATED, {"test": 2})

        # First hook should not be called again
        assert len(hook1_calls) == 1
        assert len(hook2_calls) == 1

    def test_hook_execution_control(self) -> None:
        """Test controlling hook execution globally."""
        hook_calls = []

        def event_hook(event_data: dict[str, Any]) -> None:
            hook_calls.append(event_data)

        register_event_hook(EventHook.ERROR_OCCURRED, event_hook)

        # Emit with hooks enabled
        emit_event(EventHook.ERROR_OCCURRED, {"error": "test1"})
        assert len(hook_calls) == 1

        # Disable hooks
        set_hooks_enabled(False)
        emit_event(EventHook.ERROR_OCCURRED, {"error": "test2"})
        assert len(hook_calls) == 1  # Should not increase

        # Re-enable hooks
        set_hooks_enabled(True)
        emit_event(EventHook.ERROR_OCCURRED, {"error": "test3"})
        assert len(hook_calls) == 2

    def test_comprehensive_hook_summary(self) -> None:
        """Test getting comprehensive summary with various hooks."""

        def event_hook(event_data: dict[str, Any]) -> None:
            pass

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            pass

        # Register variety of hooks
        register_event_hook(EventHook.CONTEXT_CREATED, event_hook)
        register_event_hook(EventHook.CONTEXT_DESTROYED, event_hook)
        register_event_hook(EventHook.COMPONENT_REGISTERED, event_hook)
        register_event_hook(EventHook.MODULE_BUILT, event_hook)

        register_lifecycle_hook(LifecycleHook.BEFORE_START, lifecycle_hook)
        register_lifecycle_hook(LifecycleHook.AFTER_STOP, lifecycle_hook)

        summary = get_hooks_summary()

        assert summary["event_hooks"]["total_count"] >= 4
        assert len(summary["event_hooks"]["registered_events"]) >= 4
        assert summary["hooks_enabled"] is True

    def test_event_propagation_through_managers(self) -> None:
        """Test that events propagate correctly through the manager hierarchy."""
        event_received = []
        lifecycle_received = []

        def event_hook(event_data: dict[str, Any]) -> None:
            event_received.append(event_data)

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            lifecycle_received.append((component, event_data))

        # Get the global manager
        manager = get_global_hook_manager()

        # Register hooks through manager
        manager.register_event_hook(EventHook.MODULE_REGISTERED, event_hook)
        manager.register_lifecycle_hook(LifecycleHook.BEFORE_CLEANUP, lifecycle_hook)

        # Emit through global functions
        emit_event(EventHook.MODULE_REGISTERED, {"module": "test"})

        test_component = MockComponent()
        emit_lifecycle_event(LifecycleHook.BEFORE_CLEANUP, test_component)

        # Verify events were received
        assert len(event_received) == 1
        assert event_received[0]["module"] == "test"

        assert len(lifecycle_received) == 1
        assert lifecycle_received[0][0] is test_component

    def test_hook_manager_with_complex_scenarios(self) -> None:
        """Test hook manager with complex real-world scenarios."""
        audit_log = []

        def audit_hook(event_data: dict[str, Any]) -> None:
            audit_log.append(
                {
                    "timestamp": event_data.get("timestamp", "unknown"),
                    "event": event_data.get("event_type", "unknown"),
                    "details": event_data,
                }
            )

        def component_lifecycle_hook(
            component: Any, event_data: dict[str, Any]
        ) -> None:
            audit_log.append(
                {
                    "timestamp": event_data.get("timestamp", "unknown"),
                    "event": f"lifecycle_{event_data['lifecycle_hook']}",
                    "component": type(component).__name__,
                    "details": event_data,
                }
            )

        # Set up comprehensive auditing
        for event in [
            EventHook.CONTEXT_CREATED,
            EventHook.COMPONENT_REGISTERED,
            EventHook.ERROR_OCCURRED,
        ]:
            register_event_hook(event, audit_hook)

        for hook in [LifecycleHook.AFTER_INITIALIZATION, LifecycleHook.BEFORE_CLEANUP]:
            register_lifecycle_hook(hook, component_lifecycle_hook)

        # Simulate application flow
        emit_event(
            EventHook.CONTEXT_CREATED,
            {
                "event_type": "context_created",
                "context_name": "app_context",
                "timestamp": "2023-01-01T10:00:00",
            },
        )

        test_component = MockComponent()
        emit_lifecycle_event(
            LifecycleHook.AFTER_INITIALIZATION,
            test_component,
            timestamp="2023-01-01T10:00:01",
        )

        emit_event(
            EventHook.COMPONENT_REGISTERED,
            {
                "event_type": "component_registered",
                "component_type": "MockComponent",
                "timestamp": "2023-01-01T10:00:02",
            },
        )

        emit_event(
            EventHook.ERROR_OCCURRED,
            {
                "event_type": "error_occurred",
                "error": "Test error",
                "timestamp": "2023-01-01T10:00:03",
            },
        )

        emit_lifecycle_event(
            LifecycleHook.BEFORE_CLEANUP,
            test_component,
            timestamp="2023-01-01T10:00:04",
        )

        # Verify audit log
        assert len(audit_log) == 5
        assert audit_log[0]["event"] == "context_created"
        assert audit_log[1]["event"] == "lifecycle_after_initialization"
        assert audit_log[2]["event"] == "component_registered"
        assert audit_log[3]["event"] == "error_occurred"
        assert audit_log[4]["event"] == "lifecycle_before_cleanup"
