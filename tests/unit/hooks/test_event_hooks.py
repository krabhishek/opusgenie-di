"""Tests for event hooks system."""

from typing import Any

import pytest

from opusgenie_di._hooks.event_hooks import (
    EventHook,
    EventHookManager,
    clear_all_hooks,
    emit_event,
    get_hook_manager,
    register_hook,
    set_hooks_enabled,
    unregister_hook,
)
from opusgenie_di._testing import reset_global_state


class TestEventHook:
    """Test EventHook enum."""

    def test_event_hook_values(self) -> None:
        """Test that EventHook enum has expected values."""
        assert EventHook.CONTEXT_CREATED.value == "context_created"
        assert EventHook.CONTEXT_DESTROYED.value == "context_destroyed"
        assert EventHook.COMPONENT_REGISTERED.value == "component_registered"
        assert EventHook.COMPONENT_UNREGISTERED.value == "component_unregistered"
        assert EventHook.COMPONENT_RESOLVED.value == "component_resolved"
        assert (
            EventHook.COMPONENT_RESOLUTION_FAILED.value == "component_resolution_failed"
        )
        assert EventHook.MODULE_REGISTERED.value == "module_registered"
        assert EventHook.MODULE_BUILT.value == "module_built"
        assert EventHook.IMPORT_RESOLVED.value == "import_resolved"
        assert EventHook.IMPORT_FAILED.value == "import_failed"
        assert EventHook.LIFECYCLE_STAGE_CHANGED.value == "lifecycle_stage_changed"
        assert EventHook.ERROR_OCCURRED.value == "error_occurred"


class TestEventHookManager:
    """Test EventHookManager class."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()
        self.manager = EventHookManager()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_init(self) -> None:
        """Test manager initialization."""
        manager = EventHookManager()

        assert manager._enabled is True
        assert len(manager._hooks) == 0

    def test_register_hook_valid(self) -> None:
        """Test registering a valid hook function."""

        def hook_func(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook_func)

        assert EventHook.CONTEXT_CREATED in self.manager._hooks
        assert hook_func in self.manager._hooks[EventHook.CONTEXT_CREATED]

    def test_register_hook_invalid_function(self) -> None:
        """Test registering non-callable hook raises error."""
        with pytest.raises(ValueError, match="Hook function must be callable"):
            self.manager.register_hook(EventHook.CONTEXT_CREATED, "not_callable")  # type: ignore

    def test_register_multiple_hooks_same_event(self) -> None:
        """Test registering multiple hooks for same event."""

        def hook1(event_data: dict[str, Any]) -> None:
            pass

        def hook2(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook1)
        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook2)

        hooks = self.manager._hooks[EventHook.CONTEXT_CREATED]
        assert len(hooks) == 2
        assert hook1 in hooks
        assert hook2 in hooks

    def test_unregister_hook_success(self) -> None:
        """Test successful hook unregistration."""

        def hook_func(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook_func)

        result = self.manager.unregister_hook(EventHook.CONTEXT_CREATED, hook_func)

        assert result is True
        assert hook_func not in self.manager._hooks[EventHook.CONTEXT_CREATED]

    def test_unregister_hook_not_registered(self) -> None:
        """Test unregistering hook that wasn't registered."""

        def hook_func(event_data: dict[str, Any]) -> None:
            pass

        result = self.manager.unregister_hook(EventHook.CONTEXT_CREATED, hook_func)

        assert result is False

    def test_emit_no_hooks(self) -> None:
        """Test emitting event when no hooks are registered."""
        # Should not raise any exceptions
        self.manager.emit(EventHook.CONTEXT_CREATED, {"test": "data"})

    def test_emit_with_hooks(self) -> None:
        """Test emitting event with registered hooks."""
        hook_called = []

        def hook_func(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook_func)
        event_data = {"context_name": "test"}

        self.manager.emit(EventHook.CONTEXT_CREATED, event_data)

        assert len(hook_called) == 1
        assert hook_called[0] == event_data

    def test_emit_multiple_hooks(self) -> None:
        """Test emitting event with multiple hooks."""
        hook1_called = []
        hook2_called = []

        def hook1(event_data: dict[str, Any]) -> None:
            hook1_called.append(event_data)

        def hook2(event_data: dict[str, Any]) -> None:
            hook2_called.append(event_data)

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook1)
        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook2)

        event_data = {"context_name": "test"}
        self.manager.emit(EventHook.CONTEXT_CREATED, event_data)

        assert len(hook1_called) == 1
        assert len(hook2_called) == 1
        assert hook1_called[0] == event_data
        assert hook2_called[0] == event_data

    def test_emit_hook_exception(self) -> None:
        """Test emitting event when hook raises exception."""

        def failing_hook(event_data: dict[str, Any]) -> None:
            raise ValueError("Hook failed")

        def successful_hook(event_data: dict[str, Any]) -> None:
            successful_hook.called = True  # type: ignore

        successful_hook.called = False  # type: ignore

        self.manager.register_hook(EventHook.CONTEXT_CREATED, failing_hook)
        self.manager.register_hook(EventHook.CONTEXT_CREATED, successful_hook)

        # Should not raise exception and should continue with other hooks
        self.manager.emit(EventHook.CONTEXT_CREATED, {"test": "data"})

        assert successful_hook.called is True  # type: ignore

    def test_emit_disabled(self) -> None:
        """Test emitting event when hooks are disabled."""
        hook_called = []

        def hook_func(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook_func)
        self.manager.set_enabled(False)

        self.manager.emit(EventHook.CONTEXT_CREATED, {"test": "data"})

        assert len(hook_called) == 0

    def test_get_hook_count_all(self) -> None:
        """Test getting total hook count."""

        def hook1(event_data: dict[str, Any]) -> None:
            pass

        def hook2(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook1)
        self.manager.register_hook(EventHook.CONTEXT_DESTROYED, hook2)

        assert self.manager.get_hook_count() == 2

    def test_get_hook_count_specific_event(self) -> None:
        """Test getting hook count for specific event."""

        def hook1(event_data: dict[str, Any]) -> None:
            pass

        def hook2(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook1)
        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook2)
        self.manager.register_hook(EventHook.CONTEXT_DESTROYED, hook1)

        assert self.manager.get_hook_count(EventHook.CONTEXT_CREATED) == 2
        assert self.manager.get_hook_count(EventHook.CONTEXT_DESTROYED) == 1

    def test_clear_hooks_all(self) -> None:
        """Test clearing all hooks."""

        def hook_func(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook_func)
        self.manager.register_hook(EventHook.CONTEXT_DESTROYED, hook_func)

        assert self.manager.get_hook_count() == 2

        self.manager.clear_hooks()

        assert self.manager.get_hook_count() == 0

    def test_clear_hooks_specific_event(self) -> None:
        """Test clearing hooks for specific event."""

        def hook_func(event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook_func)
        self.manager.register_hook(EventHook.CONTEXT_DESTROYED, hook_func)

        assert self.manager.get_hook_count() == 2

        self.manager.clear_hooks(EventHook.CONTEXT_CREATED)

        assert self.manager.get_hook_count() == 1
        assert self.manager.get_hook_count(EventHook.CONTEXT_CREATED) == 0
        assert self.manager.get_hook_count(EventHook.CONTEXT_DESTROYED) == 1

    def test_set_enabled(self) -> None:
        """Test enabling/disabling hook execution."""
        assert self.manager.is_enabled() is True

        self.manager.set_enabled(False)
        assert self.manager.is_enabled() is False

        self.manager.set_enabled(True)
        assert self.manager.is_enabled() is True

    def test_get_registered_events(self) -> None:
        """Test getting list of events with registered hooks."""

        def hook_func(event_data: dict[str, Any]) -> None:
            pass

        # No hooks registered initially
        assert self.manager.get_registered_events() == []

        self.manager.register_hook(EventHook.CONTEXT_CREATED, hook_func)
        self.manager.register_hook(EventHook.COMPONENT_REGISTERED, hook_func)

        events = self.manager.get_registered_events()
        assert len(events) == 2
        assert EventHook.CONTEXT_CREATED in events
        assert EventHook.COMPONENT_REGISTERED in events


class TestGlobalHookFunctions:
    """Test global hook convenience functions."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_get_hook_manager(self) -> None:
        """Test getting global hook manager."""
        manager1 = get_hook_manager()
        manager2 = get_hook_manager()

        # Should return same instance
        assert manager1 is manager2
        assert isinstance(manager1, EventHookManager)

    def test_register_hook_function(self) -> None:
        """Test global register_hook function."""

        def hook_func(event_data: dict[str, Any]) -> None:
            hook_func.called = True  # type: ignore

        hook_func.called = False  # type: ignore

        register_hook(EventHook.CONTEXT_CREATED, hook_func)

        # Verify hook was registered by emitting event
        emit_event(EventHook.CONTEXT_CREATED, {"test": "data"})

        assert hook_func.called is True  # type: ignore

    def test_unregister_hook_function(self) -> None:
        """Test global unregister_hook function."""

        def hook_func(event_data: dict[str, Any]) -> None:
            hook_func.called = True  # type: ignore

        hook_func.called = False  # type: ignore

        register_hook(EventHook.CONTEXT_CREATED, hook_func)
        result = unregister_hook(EventHook.CONTEXT_CREATED, hook_func)

        assert result is True

        # Verify hook was unregistered
        emit_event(EventHook.CONTEXT_CREATED, {"test": "data"})

        assert hook_func.called is False  # type: ignore

    def test_emit_event_function(self) -> None:
        """Test global emit_event function."""
        hook_called = []

        def hook_func(event_data: dict[str, Any]) -> None:
            hook_called.append(event_data)

        register_hook(EventHook.CONTEXT_CREATED, hook_func)

        event_data = {"context_name": "test"}
        emit_event(EventHook.CONTEXT_CREATED, event_data)

        assert len(hook_called) == 1
        assert hook_called[0] == event_data

    def test_clear_all_hooks_function(self) -> None:
        """Test global clear_all_hooks function."""

        def hook_func(event_data: dict[str, Any]) -> None:
            pass

        register_hook(EventHook.CONTEXT_CREATED, hook_func)
        register_hook(EventHook.CONTEXT_DESTROYED, hook_func)

        manager = get_hook_manager()
        assert manager.get_hook_count() == 2

        clear_all_hooks()

        assert manager.get_hook_count() == 0

    def test_set_hooks_enabled_function(self) -> None:
        """Test global set_hooks_enabled function."""
        manager = get_hook_manager()

        assert manager.is_enabled() is True

        set_hooks_enabled(False)
        assert manager.is_enabled() is False

        set_hooks_enabled(True)
        assert manager.is_enabled() is True


class TestEventHookIntegration:
    """Test event hook integration scenarios."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_complex_hook_scenario(self) -> None:
        """Test complex scenario with multiple events and hooks."""
        events_received = []

        def context_hook(event_data: dict[str, Any]) -> None:
            events_received.append(("context", event_data))

        def component_hook(event_data: dict[str, Any]) -> None:
            events_received.append(("component", event_data))

        def error_hook(event_data: dict[str, Any]) -> None:
            events_received.append(("error", event_data))

        # Register hooks for different events
        register_hook(EventHook.CONTEXT_CREATED, context_hook)
        register_hook(EventHook.COMPONENT_REGISTERED, component_hook)
        register_hook(EventHook.ERROR_OCCURRED, error_hook)

        # Emit various events
        emit_event(EventHook.CONTEXT_CREATED, {"context_name": "test_context"})
        emit_event(EventHook.COMPONENT_REGISTERED, {"component_type": "TestComponent"})
        emit_event(EventHook.ERROR_OCCURRED, {"error": "Test error"})

        # Verify all events were received
        assert len(events_received) == 3
        assert events_received[0][0] == "context"
        assert events_received[1][0] == "component"
        assert events_received[2][0] == "error"

    def test_hook_execution_order(self) -> None:
        """Test that hooks are executed in registration order."""
        execution_order = []

        def hook1(event_data: dict[str, Any]) -> None:
            execution_order.append(1)

        def hook2(event_data: dict[str, Any]) -> None:
            execution_order.append(2)

        def hook3(event_data: dict[str, Any]) -> None:
            execution_order.append(3)

        register_hook(EventHook.CONTEXT_CREATED, hook1)
        register_hook(EventHook.CONTEXT_CREATED, hook2)
        register_hook(EventHook.CONTEXT_CREATED, hook3)

        emit_event(EventHook.CONTEXT_CREATED, {})

        assert execution_order == [1, 2, 3]

    def test_hook_data_isolation(self) -> None:
        """Test that event data is properly passed to hooks."""
        received_data = []

        def hook_func(event_data: dict[str, Any]) -> None:
            received_data.append(event_data.copy())

        register_hook(EventHook.CONTEXT_CREATED, hook_func)

        # Emit events with different data
        emit_event(EventHook.CONTEXT_CREATED, {"id": 1, "name": "context1"})
        emit_event(EventHook.CONTEXT_CREATED, {"id": 2, "name": "context2"})

        assert len(received_data) == 2
        assert received_data[0]["id"] == 1
        assert received_data[0]["name"] == "context1"
        assert received_data[1]["id"] == 2
        assert received_data[1]["name"] == "context2"

    def test_hook_exception_isolation(self) -> None:
        """Test that exception in one hook doesn't affect others."""
        successful_hooks_called = []

        def failing_hook(event_data: dict[str, Any]) -> None:
            raise RuntimeError("Hook failed")

        def successful_hook1(event_data: dict[str, Any]) -> None:
            successful_hooks_called.append(1)

        def successful_hook2(event_data: dict[str, Any]) -> None:
            successful_hooks_called.append(2)

        register_hook(EventHook.CONTEXT_CREATED, successful_hook1)
        register_hook(EventHook.CONTEXT_CREATED, failing_hook)
        register_hook(EventHook.CONTEXT_CREATED, successful_hook2)

        # Should not raise exception
        emit_event(EventHook.CONTEXT_CREATED, {})

        # Both successful hooks should have been called
        assert successful_hooks_called == [1, 2]

    def test_dynamic_hook_management(self) -> None:
        """Test adding and removing hooks dynamically."""
        hook_calls = []

        def hook_func(event_data: dict[str, Any]) -> None:
            hook_calls.append(event_data)

        # Start with no hooks
        emit_event(EventHook.CONTEXT_CREATED, {"test": 1})
        assert len(hook_calls) == 0

        # Add hook
        register_hook(EventHook.CONTEXT_CREATED, hook_func)
        emit_event(EventHook.CONTEXT_CREATED, {"test": 2})
        assert len(hook_calls) == 1

        # Remove hook
        unregister_hook(EventHook.CONTEXT_CREATED, hook_func)
        emit_event(EventHook.CONTEXT_CREATED, {"test": 3})
        assert len(hook_calls) == 1  # Should not increase

    def test_hook_with_complex_data(self) -> None:
        """Test hooks with complex event data structures."""
        received_data = None

        def hook_func(event_data: dict[str, Any]) -> None:
            nonlocal received_data
            received_data = event_data

        register_hook(EventHook.COMPONENT_REGISTERED, hook_func)

        complex_data = {
            "component_type": "ComplexComponent",
            "metadata": {
                "scope": "singleton",
                "tags": {"env": "test", "version": "1.0"},
            },
            "dependencies": ["ServiceA", "ServiceB"],
            "context_info": {"name": "test_context", "layer": "application"},
        }

        emit_event(EventHook.COMPONENT_REGISTERED, complex_data)

        assert received_data == complex_data
        assert received_data["metadata"]["scope"] == "singleton"
        assert "ServiceA" in received_data["dependencies"]
