"""Tests for lifecycle hooks system."""

from typing import Any

from opusgenie_di._base import BaseComponent, LifecycleStage
from opusgenie_di._hooks.lifecycle_hooks import (
    LifecycleHook,
    LifecycleHookManager,
    emit_lifecycle_event,
    get_lifecycle_hook_manager,
    register_lifecycle_hook,
)
from opusgenie_di._testing import MockComponent, reset_global_state


class TestLifecycleHook:
    """Test LifecycleHook enum."""

    def test_lifecycle_hook_values(self) -> None:
        """Test that LifecycleHook enum has expected values."""
        assert LifecycleHook.BEFORE_INITIALIZATION.value == "before_initialization"
        assert LifecycleHook.AFTER_INITIALIZATION.value == "after_initialization"
        assert LifecycleHook.BEFORE_START.value == "before_start"
        assert LifecycleHook.AFTER_START.value == "after_start"
        assert LifecycleHook.BEFORE_STOP.value == "before_stop"
        assert LifecycleHook.AFTER_STOP.value == "after_stop"
        assert LifecycleHook.BEFORE_CLEANUP.value == "before_cleanup"
        assert LifecycleHook.AFTER_CLEANUP.value == "after_cleanup"
        assert LifecycleHook.INITIALIZATION_ERROR.value == "initialization_error"
        assert LifecycleHook.START_ERROR.value == "start_error"
        assert LifecycleHook.STOP_ERROR.value == "stop_error"
        assert LifecycleHook.CLEANUP_ERROR.value == "cleanup_error"


class TestLifecycleHookManager:
    """Test LifecycleHookManager class."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()
        self.manager = LifecycleHookManager()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_init(self) -> None:
        """Test manager initialization."""
        manager = LifecycleHookManager()

        assert hasattr(manager, "_hooks")
        assert manager._hooks is not None

    def test_register_lifecycle_hook(self) -> None:
        """Test registering a lifecycle hook."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(
            LifecycleHook.BEFORE_INITIALIZATION, lifecycle_hook
        )

        # Verify hook was registered by emitting event
        test_component = MockComponent()
        self.manager.emit_lifecycle_event(
            LifecycleHook.BEFORE_INITIALIZATION, test_component
        )

        assert len(hook_called) == 1
        assert hook_called[0][0] is test_component

    def test_emit_lifecycle_event_basic(self) -> None:
        """Test basic lifecycle event emission."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(
            LifecycleHook.AFTER_INITIALIZATION, lifecycle_hook
        )

        test_component = MockComponent()
        self.manager.emit_lifecycle_event(
            LifecycleHook.AFTER_INITIALIZATION, test_component
        )

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert component is test_component
        assert event_data["component"] is test_component
        assert event_data["component_type"] == "MockComponent"
        assert event_data["lifecycle_hook"] == "after_initialization"

    def test_emit_lifecycle_event_with_stage(self) -> None:
        """Test lifecycle event emission with stage."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(LifecycleHook.BEFORE_START, lifecycle_hook)

        test_component = MockComponent()
        self.manager.emit_lifecycle_event(
            LifecycleHook.BEFORE_START, test_component, stage=LifecycleStage.STARTUP
        )

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert event_data["lifecycle_stage"] == "startup"

    def test_emit_lifecycle_event_with_extra_data(self) -> None:
        """Test lifecycle event emission with extra data."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(
            LifecycleHook.BEFORE_CLEANUP, lifecycle_hook
        )

        test_component = MockComponent()
        self.manager.emit_lifecycle_event(
            LifecycleHook.BEFORE_CLEANUP,
            test_component,
            reason="test_cleanup",
            context_name="test_context",
        )

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert event_data["reason"] == "test_cleanup"
        assert event_data["context_name"] == "test_context"

    def test_emit_lifecycle_event_with_component_id(self) -> None:
        """Test lifecycle event emission with component that has ID."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(LifecycleHook.AFTER_START, lifecycle_hook)

        # Create component with component_id attribute
        test_component = MockComponent()
        test_component.component_id = "test_component_123"  # type: ignore

        self.manager.emit_lifecycle_event(LifecycleHook.AFTER_START, test_component)

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert event_data["component_id"] == "test_component_123"

    def test_execute_lifecycle_hook(self) -> None:
        """Test execute_lifecycle_hook convenience method."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        self.manager.register_lifecycle_hook(LifecycleHook.BEFORE_STOP, lifecycle_hook)

        test_component = MockComponent()
        self.manager.execute_lifecycle_hook(
            LifecycleHook.BEFORE_STOP,
            test_component,
            stage=LifecycleStage.STOPPING,
            shutdown_reason="test",
        )

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert component is test_component
        assert event_data["lifecycle_stage"] == "stopping"
        assert event_data["shutdown_reason"] == "test"

    def test_clear_lifecycle_hooks(self) -> None:
        """Test clearing all lifecycle hooks."""

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            pass

        self.manager.register_lifecycle_hook(
            LifecycleHook.BEFORE_INITIALIZATION, lifecycle_hook
        )
        self.manager.register_lifecycle_hook(
            LifecycleHook.AFTER_INITIALIZATION, lifecycle_hook
        )

        # Verify hooks are registered
        assert len(self.manager._hooks) > 0

        self.manager.clear_lifecycle_hooks()

        # Verify hooks are cleared
        assert len(self.manager._hooks) == 0

    def test_hook_function_parameters(self) -> None:
        """Test that hook functions receive correct parameters."""
        received_component = None
        received_event_data = None

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            nonlocal received_component, received_event_data
            received_component = component
            received_event_data = event_data

        self.manager.register_lifecycle_hook(
            LifecycleHook.INITIALIZATION_ERROR, lifecycle_hook
        )

        test_component = MockComponent()
        self.manager.emit_lifecycle_event(
            LifecycleHook.INITIALIZATION_ERROR,
            test_component,
            error_message="Test error",
        )

        assert received_component is test_component
        assert received_event_data["component"] is test_component
        assert received_event_data["error_message"] == "Test error"

    def test_multiple_hooks_same_event(self) -> None:
        """Test multiple hooks for the same lifecycle event."""
        hook1_called = []
        hook2_called = []

        def hook1(component: Any, event_data: dict[str, Any]) -> None:
            hook1_called.append(component)

        def hook2(component: Any, event_data: dict[str, Any]) -> None:
            hook2_called.append(component)

        self.manager.register_lifecycle_hook(LifecycleHook.BEFORE_START, hook1)
        self.manager.register_lifecycle_hook(LifecycleHook.BEFORE_START, hook2)

        test_component = MockComponent()
        self.manager.emit_lifecycle_event(LifecycleHook.BEFORE_START, test_component)

        assert len(hook1_called) == 1
        assert len(hook2_called) == 1
        assert hook1_called[0] is test_component
        assert hook2_called[0] is test_component

    def test_lifecycle_hook_fallback_to_generic_event(self) -> None:
        """Test that lifecycle hooks without direct event mapping use generic event."""
        # This tests the fallback mechanism in the implementation
        # Most lifecycle hooks should map to LIFECYCLE_STAGE_CHANGED

        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        # Register hook for a lifecycle event that might not have direct EventHook mapping
        self.manager.register_lifecycle_hook(
            LifecycleHook.CLEANUP_ERROR, lifecycle_hook
        )

        test_component = MockComponent()
        self.manager.emit_lifecycle_event(LifecycleHook.CLEANUP_ERROR, test_component)

        # Should still work via fallback mechanism
        assert len(hook_called) == 1


class TestGlobalLifecycleHookFunctions:
    """Test global lifecycle hook convenience functions."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_get_lifecycle_hook_manager(self) -> None:
        """Test getting global lifecycle hook manager."""
        manager1 = get_lifecycle_hook_manager()
        manager2 = get_lifecycle_hook_manager()

        # Should return same instance
        assert manager1 is manager2
        assert isinstance(manager1, LifecycleHookManager)

    def test_register_lifecycle_hook_function(self) -> None:
        """Test global register_lifecycle_hook function."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        register_lifecycle_hook(LifecycleHook.BEFORE_INITIALIZATION, lifecycle_hook)

        # Verify hook was registered by emitting event
        test_component = MockComponent()
        emit_lifecycle_event(LifecycleHook.BEFORE_INITIALIZATION, test_component)

        assert len(hook_called) == 1
        assert hook_called[0][0] is test_component

    def test_emit_lifecycle_event_function(self) -> None:
        """Test global emit_lifecycle_event function."""
        hook_called = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_called.append((component, event_data))

        register_lifecycle_hook(LifecycleHook.AFTER_CLEANUP, lifecycle_hook)

        test_component = MockComponent()
        emit_lifecycle_event(
            LifecycleHook.AFTER_CLEANUP,
            test_component,
            stage=LifecycleStage.DISPOSED,
            cleanup_time=123,
        )

        assert len(hook_called) == 1
        component, event_data = hook_called[0]

        assert component is test_component
        assert event_data["lifecycle_stage"] == "disposed"
        assert event_data["cleanup_time"] == 123


class TestLifecycleHookIntegration:
    """Test lifecycle hook integration scenarios."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_complete_component_lifecycle(self) -> None:
        """Test hooks throughout complete component lifecycle."""
        lifecycle_events = []

        def lifecycle_hook(component: Any, event_data: dict[str, Any]) -> None:
            lifecycle_events.append(event_data["lifecycle_hook"])

        # Register hooks for all lifecycle stages
        hooks = [
            LifecycleHook.BEFORE_INITIALIZATION,
            LifecycleHook.AFTER_INITIALIZATION,
            LifecycleHook.BEFORE_START,
            LifecycleHook.AFTER_START,
            LifecycleHook.BEFORE_STOP,
            LifecycleHook.AFTER_STOP,
            LifecycleHook.BEFORE_CLEANUP,
            LifecycleHook.AFTER_CLEANUP,
        ]

        for hook in hooks:
            register_lifecycle_hook(hook, lifecycle_hook)

        # Simulate complete component lifecycle
        test_component = MockComponent()

        emit_lifecycle_event(LifecycleHook.BEFORE_INITIALIZATION, test_component)
        emit_lifecycle_event(LifecycleHook.AFTER_INITIALIZATION, test_component)
        emit_lifecycle_event(LifecycleHook.BEFORE_START, test_component)
        emit_lifecycle_event(LifecycleHook.AFTER_START, test_component)
        emit_lifecycle_event(LifecycleHook.BEFORE_STOP, test_component)
        emit_lifecycle_event(LifecycleHook.AFTER_STOP, test_component)
        emit_lifecycle_event(LifecycleHook.BEFORE_CLEANUP, test_component)
        emit_lifecycle_event(LifecycleHook.AFTER_CLEANUP, test_component)

        # Verify all lifecycle events were captured in order
        expected_events = [
            "before_initialization",
            "after_initialization",
            "before_start",
            "after_start",
            "before_stop",
            "after_stop",
            "before_cleanup",
            "after_cleanup",
        ]

        assert lifecycle_events == expected_events

    def test_error_handling_lifecycle(self) -> None:
        """Test lifecycle hooks for error scenarios."""
        error_events = []

        def error_hook(component: Any, event_data: dict[str, Any]) -> None:
            error_events.append(
                {
                    "hook": event_data["lifecycle_hook"],
                    "component": component,
                    "error": event_data.get("error_message"),
                }
            )

        error_hooks = [
            LifecycleHook.INITIALIZATION_ERROR,
            LifecycleHook.START_ERROR,
            LifecycleHook.STOP_ERROR,
            LifecycleHook.CLEANUP_ERROR,
        ]

        for hook in error_hooks:
            register_lifecycle_hook(hook, error_hook)

        test_component = MockComponent()

        # Simulate various error scenarios
        emit_lifecycle_event(
            LifecycleHook.INITIALIZATION_ERROR,
            test_component,
            error_message="Failed to initialize",
        )
        emit_lifecycle_event(
            LifecycleHook.START_ERROR, test_component, error_message="Failed to start"
        )
        emit_lifecycle_event(
            LifecycleHook.STOP_ERROR, test_component, error_message="Failed to stop"
        )
        emit_lifecycle_event(
            LifecycleHook.CLEANUP_ERROR,
            test_component,
            error_message="Failed to cleanup",
        )

        assert len(error_events) == 4
        assert error_events[0]["hook"] == "initialization_error"
        assert error_events[0]["error"] == "Failed to initialize"
        assert error_events[1]["hook"] == "start_error"
        assert error_events[2]["hook"] == "stop_error"
        assert error_events[3]["hook"] == "cleanup_error"

    def test_component_tracking_through_lifecycle(self) -> None:
        """Test tracking specific component through its lifecycle."""
        component_history = {}

        def tracking_hook(component: Any, event_data: dict[str, Any]) -> None:
            component_id = id(component)
            if component_id not in component_history:
                component_history[component_id] = []

            component_history[component_id].append(
                {
                    "hook": event_data["lifecycle_hook"],
                    "stage": event_data.get("lifecycle_stage"),
                    "timestamp": event_data.get("timestamp", "unknown"),
                }
            )

        # Register tracking hook for key lifecycle events
        for hook in [LifecycleHook.AFTER_INITIALIZATION, LifecycleHook.BEFORE_CLEANUP]:
            register_lifecycle_hook(hook, tracking_hook)

        # Create multiple components and track them
        component1 = MockComponent()
        component2 = MockComponent()

        emit_lifecycle_event(
            LifecycleHook.AFTER_INITIALIZATION,
            component1,
            stage=LifecycleStage.INITIALIZED,
            timestamp="2023-01-01T10:00:00",
        )
        emit_lifecycle_event(
            LifecycleHook.AFTER_INITIALIZATION,
            component2,
            stage=LifecycleStage.INITIALIZED,
            timestamp="2023-01-01T10:01:00",
        )
        emit_lifecycle_event(
            LifecycleHook.BEFORE_CLEANUP,
            component1,
            stage=LifecycleStage.STOPPING,
            timestamp="2023-01-01T11:00:00",
        )

        # Verify each component was tracked separately
        assert len(component_history) == 2

        comp1_history = component_history[id(component1)]
        comp2_history = component_history[id(component2)]

        assert len(comp1_history) == 2
        assert len(comp2_history) == 1

        assert comp1_history[0]["hook"] == "after_initialization"
        assert comp1_history[1]["hook"] == "before_cleanup"
        assert comp2_history[0]["hook"] == "after_initialization"

    def test_lifecycle_hook_with_custom_component(self) -> None:
        """Test lifecycle hooks with custom component types."""
        hook_calls = []

        def component_hook(component: Any, event_data: dict[str, Any]) -> None:
            hook_calls.append(
                {"component_type": event_data["component_type"], "component": component}
            )

        register_lifecycle_hook(LifecycleHook.BEFORE_START, component_hook)

        # Custom component class
        class CustomService(BaseComponent):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        custom_component = CustomService("test_service")

        emit_lifecycle_event(LifecycleHook.BEFORE_START, custom_component)

        assert len(hook_calls) == 1
        assert hook_calls[0]["component_type"] == "CustomService"
        assert hook_calls[0]["component"] is custom_component
        assert hook_calls[0]["component"].name == "test_service"
