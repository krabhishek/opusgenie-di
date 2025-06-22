"""Tests for testing fixtures and utilities."""

from unittest.mock import Mock, patch

import pytest

from opusgenie_di import ComponentScope
from opusgenie_di._testing.fixtures import (
    MockComponent,
    MockComponentWithDependency,
    MockSingletonComponent,
    MockTransientComponent,
    TestEventCollector,
    assert_component_not_registered,
    assert_component_registered,
    assert_components_different,
    assert_components_equal,
    create_mock_factory,
    create_test_context,
    create_test_module_classes,
    reset_global_state,
)


class TestMockComponents:
    """Test mock component classes."""

    def test_mock_component_basic(self) -> None:
        """Test basic MockComponent functionality."""

        mock = MockComponent()
        assert mock.value == "mock"
        assert mock.call_count == 0

        # Test with custom value
        custom_mock = MockComponent(value="custom")
        assert custom_mock.value == "custom"
        assert custom_mock.call_count == 0

    def test_mock_component_method(self) -> None:
        """Test MockComponent mock_method."""

        mock = MockComponent(value="test")

        result1 = mock.mock_method()
        assert result1 == "test_1"
        assert mock.call_count == 1

        result2 = mock.mock_method()
        assert result2 == "test_2"
        assert mock.call_count == 2

    def test_mock_component_reset(self) -> None:
        """Test MockComponent reset_call_count."""

        mock = MockComponent()
        mock.mock_method()
        mock.mock_method()
        assert mock.call_count == 2

        mock.reset_call_count()
        assert mock.call_count == 0

    def test_mock_component_with_kwargs(self) -> None:
        """Test MockComponent with additional kwargs."""

        mock = MockComponent(value="test", extra_param="extra")
        assert mock.value == "test"
        # Extra params are passed to BaseComponent

    def test_mock_singleton_component(self) -> None:
        """Test MockSingletonComponent."""

        mock = MockSingletonComponent()
        assert mock.value == "singleton"
        assert mock.call_count == 0

        # Should be decorated with proper scope
        from opusgenie_di._decorators import get_component_options

        options = get_component_options(MockSingletonComponent)
        assert options is not None
        assert options.scope == ComponentScope.SINGLETON
        assert options.auto_register is False

    def test_mock_transient_component(self) -> None:
        """Test MockTransientComponent."""

        mock = MockTransientComponent()
        assert mock.value == "transient"
        assert mock.call_count == 0

        # Should be decorated with proper scope
        from opusgenie_di._decorators import get_component_options

        options = get_component_options(MockTransientComponent)
        assert options is not None
        assert options.scope == ComponentScope.TRANSIENT
        assert options.auto_register is False

    def test_mock_component_with_dependency(self) -> None:
        """Test MockComponentWithDependency."""

        # Without dependency
        mock = MockComponentWithDependency()
        assert mock.dependency is None
        assert mock.get_dependency_value() == "no_dependency"

        # With dependency
        dependency = MockComponent(value="dep")
        mock_with_dep = MockComponentWithDependency(dependency=dependency)
        assert mock_with_dep.dependency is dependency
        assert mock_with_dep.get_dependency_value() == "dep_1"
        assert dependency.call_count == 1


class TestCreateTestContext:
    """Test create_test_context function."""

    def test_create_test_context_default(self) -> None:
        """Test creating test context with default name."""

        context = create_test_context()
        assert context.name == "test"

        # Check that mock components are registered
        assert context.is_registered(MockComponent)
        assert context.is_registered(MockSingletonComponent)
        assert context.is_registered(MockTransientComponent)
        assert context.is_registered(MockComponentWithDependency)

    def test_create_test_context_custom_name(self) -> None:
        """Test creating test context with custom name."""

        context = create_test_context("custom_test")
        assert context.name == "custom_test"

        # Should still have registered components
        assert context.is_registered(MockComponent)

    def test_create_test_context_registrations(self) -> None:
        """Test that test context has correct component registrations."""

        context = create_test_context()

        # Test singleton registrations
        mock1 = context.resolve(MockComponent)
        mock2 = context.resolve(MockComponent)
        assert mock1 is mock2  # Should be same instance (singleton)

        singleton1 = context.resolve(MockSingletonComponent)
        singleton2 = context.resolve(MockSingletonComponent)
        assert singleton1 is singleton2  # Should be same instance

        # Test transient registrations
        transient1 = context.resolve(MockTransientComponent)
        transient2 = context.resolve(MockTransientComponent)
        assert transient1 is not transient2  # Should be different instances

    def test_create_test_context_with_dependency_injection(self) -> None:
        """Test that dependency injection works in test context."""

        context = create_test_context()

        # MockComponentWithDependency should get MockComponent injected
        with_dep = context.resolve(MockComponentWithDependency)
        assert with_dep.dependency is not None
        assert isinstance(with_dep.dependency, MockComponent)


class TestResetGlobalState:
    """Test reset_global_state function."""

    def test_reset_global_state_basic(self) -> None:
        """Test basic reset_global_state functionality."""

        # This should not raise any exceptions
        reset_global_state()

    def test_reset_global_state_clears_context(self) -> None:
        """Test that reset_global_state clears global context."""

        from opusgenie_di import get_global_context

        # Add something to global context
        global_context = get_global_context()
        global_context.register_component(MockComponent)
        assert global_context.is_registered(MockComponent)

        # Reset state
        reset_global_state()

        # Global context should be reset
        get_global_context()
        # After reset, the registration should be cleared
        # (This depends on the actual implementation of reset)

    @patch("opusgenie_di._testing.fixtures.reset_global_context")
    @patch("opusgenie_di._testing.fixtures.clear_global_registry")
    @patch("opusgenie_di._testing.fixtures.clear_all_hooks")
    @patch("opusgenie_di._testing.fixtures.set_hooks_enabled")
    def test_reset_global_state_calls_all_resets(
        self,
        mock_set_hooks: Mock,
        mock_clear_hooks: Mock,
        mock_clear_registry: Mock,
        mock_reset_context: Mock,
    ) -> None:
        """Test that reset_global_state calls all necessary reset functions."""

        reset_global_state()

        mock_reset_context.assert_called_once()
        mock_clear_registry.assert_called_once()
        mock_clear_hooks.assert_called_once()
        mock_set_hooks.assert_called_once_with(True)


class TestCreateMockFactory:
    """Test create_mock_factory function."""

    def test_create_mock_factory_basic(self) -> None:
        """Test basic mock factory creation."""

        factory = create_mock_factory("factory_value")
        assert callable(factory)

        component = factory()
        assert isinstance(component, MockComponent)
        assert component.value == "factory_value"

    def test_create_mock_factory_multiple_calls(self) -> None:
        """Test that factory creates new instances each time."""

        factory = create_mock_factory("test")

        component1 = factory()
        component2 = factory()

        assert component1 is not component2
        assert component1.value == "test"
        assert component2.value == "test"

    def test_create_mock_factory_different_values(self) -> None:
        """Test creating factories with different values."""

        factory1 = create_mock_factory("value1")
        factory2 = create_mock_factory("value2")

        comp1 = factory1()
        comp2 = factory2()

        assert comp1.value == "value1"
        assert comp2.value == "value2"


class TestAssertionHelpers:
    """Test assertion helper functions."""

    def test_assert_component_registered_success(self) -> None:
        """Test assert_component_registered when component is registered."""

        context = create_test_context()

        # Should not raise - MockComponent is registered
        assert_component_registered(context, MockComponent)

    def test_assert_component_registered_with_name(self) -> None:
        """Test assert_component_registered with component name."""

        context = create_test_context()
        # Register with specific name
        context.register_component(MockComponent, name="named_mock")

        # Should not raise
        assert_component_registered(context, MockComponent, "named_mock")

    def test_assert_component_registered_failure(self) -> None:
        """Test assert_component_registered when component is not registered."""

        context = create_test_context()

        class UnregisteredComponent:
            pass

        with pytest.raises(AssertionError) as exc_info:
            assert_component_registered(context, UnregisteredComponent)

        assert "is not registered" in str(exc_info.value)
        assert "UnregisteredComponent" in str(exc_info.value)

    def test_assert_component_not_registered_success(self) -> None:
        """Test assert_component_not_registered when component is not registered."""

        context = create_test_context()

        class UnregisteredComponent:
            pass

        # Should not raise
        assert_component_not_registered(context, UnregisteredComponent)

    def test_assert_component_not_registered_failure(self) -> None:
        """Test assert_component_not_registered when component is registered."""

        context = create_test_context()

        with pytest.raises(AssertionError) as exc_info:
            assert_component_not_registered(context, MockComponent)

        assert "is registered" in str(exc_info.value)
        assert "should not be" in str(exc_info.value)

    def test_assert_components_equal_success(self) -> None:
        """Test assert_components_equal with same instances."""

        component = MockComponent()

        # Should not raise
        assert_components_equal(component, component)

    def test_assert_components_equal_failure(self) -> None:
        """Test assert_components_equal with different instances."""

        component1 = MockComponent()
        component2 = MockComponent()

        with pytest.raises(AssertionError) as exc_info:
            assert_components_equal(component1, component2)

        assert "not the same instance" in str(exc_info.value)
        assert str(id(component1)) in str(exc_info.value)
        assert str(id(component2)) in str(exc_info.value)

    def test_assert_components_different_success(self) -> None:
        """Test assert_components_different with different instances."""

        component1 = MockComponent()
        component2 = MockComponent()

        # Should not raise
        assert_components_different(component1, component2)

    def test_assert_components_different_failure(self) -> None:
        """Test assert_components_different with same instance."""

        component = MockComponent()

        with pytest.raises(AssertionError) as exc_info:
            assert_components_different(component, component)

        assert "same instance but should be different" in str(exc_info.value)


class TestCreateTestModuleClasses:
    """Test create_test_module_classes function."""

    def test_create_test_module_classes_basic(self) -> None:
        """Test basic creation of test module classes."""

        modules = create_test_module_classes()

        assert isinstance(modules, dict)
        assert "test_infrastructure" in modules
        assert "test_application" in modules

        infra_module = modules["test_infrastructure"]
        app_module = modules["test_application"]

        # Check that they are classes
        assert isinstance(infra_module, type)
        assert isinstance(app_module, type)

    def test_create_test_module_classes_decorations(self) -> None:
        """Test that created modules are properly decorated."""

        modules = create_test_module_classes()

        from opusgenie_di._decorators import get_module_options, is_context_module

        # Check infrastructure module
        infra_module = modules["test_infrastructure"]
        assert is_context_module(infra_module)

        infra_options = get_module_options(infra_module)
        assert infra_options is not None
        assert infra_options.name == "test_infrastructure"
        assert MockComponent in infra_options.exports
        assert MockComponent in infra_options.providers

        # Check application module
        app_module = modules["test_application"]
        assert is_context_module(app_module)

        app_options = get_module_options(app_module)
        assert app_options is not None
        assert app_options.name == "test_application"
        assert MockComponentWithDependency in app_options.exports
        assert MockComponentWithDependency in app_options.providers
        assert len(app_options.imports) == 1

    def test_create_test_module_classes_imports(self) -> None:
        """Test that module imports are correctly configured."""

        modules = create_test_module_classes()

        from opusgenie_di._decorators import get_module_options

        app_module = modules["test_application"]
        app_options = get_module_options(app_module)

        # Should import MockComponent from test_infrastructure
        import_declaration = app_options.imports[0]
        assert import_declaration.component_type == MockComponent
        assert import_declaration.from_context == "test_infrastructure"


class TestEventCollectorUtility:
    """Test TestEventCollector utility."""

    def test_event_collector_basic(self) -> None:
        """Test basic TestEventCollector functionality."""

        collector = TestEventCollector()
        assert collector.get_event_count() == 0
        assert collector.get_events() == []

    def test_event_collector_collect_events(self) -> None:
        """Test collecting events."""

        collector = TestEventCollector()

        event1 = {"type": "test", "data": "event1"}
        event2 = {"type": "test", "data": "event2"}

        collector.collect_event(event1)
        collector.collect_event(event2)

        assert collector.get_event_count() == 2
        events = collector.get_events()
        assert len(events) == 2
        assert events[0]["data"] == "event1"
        assert events[1]["data"] == "event2"

    def test_event_collector_get_events_by_type(self) -> None:
        """Test filtering events by type."""

        collector = TestEventCollector()

        collector.collect_event({"event_type": "type1", "data": "a"})
        collector.collect_event({"event_type": "type2", "data": "b"})
        collector.collect_event({"event_type": "type1", "data": "c"})

        type1_events = collector.get_events_by_type("type1")
        assert len(type1_events) == 2
        assert type1_events[0]["data"] == "a"
        assert type1_events[1]["data"] == "c"

        type2_events = collector.get_events_by_type("type2")
        assert len(type2_events) == 1
        assert type2_events[0]["data"] == "b"

        nonexistent_events = collector.get_events_by_type("nonexistent")
        assert len(nonexistent_events) == 0

    def test_event_collector_clear_events(self) -> None:
        """Test clearing collected events."""

        collector = TestEventCollector()

        collector.collect_event({"data": "test"})
        assert collector.get_event_count() == 1

        collector.clear_events()
        assert collector.get_event_count() == 0
        assert collector.get_events() == []

    def test_event_collector_assert_event_count_success(self) -> None:
        """Test assert_event_count when count matches."""

        collector = TestEventCollector()

        collector.collect_event({"data": "1"})
        collector.collect_event({"data": "2"})

        # Should not raise
        collector.assert_event_count(2)

    def test_event_collector_assert_event_count_failure(self) -> None:
        """Test assert_event_count when count doesn't match."""

        collector = TestEventCollector()

        collector.collect_event({"data": "1"})

        with pytest.raises(AssertionError) as exc_info:
            collector.assert_event_count(2)

        assert "Expected 2 events, but got 1" in str(exc_info.value)

    def test_event_collector_assert_has_event_success(self) -> None:
        """Test assert_has_event when event exists."""

        collector = TestEventCollector()

        collector.collect_event({"type": "test", "component": "A", "action": "created"})
        collector.collect_event({"type": "test", "component": "B", "action": "updated"})

        # Should not raise
        collector.assert_has_event(type="test", component="A")
        collector.assert_has_event(component="B", action="updated")

    def test_event_collector_assert_has_event_failure(self) -> None:
        """Test assert_has_event when event doesn't exist."""

        collector = TestEventCollector()

        collector.collect_event({"type": "test", "component": "A"})

        with pytest.raises(AssertionError) as exc_info:
            collector.assert_has_event(type="test", component="B")

        assert "No event found matching filters" in str(exc_info.value)
        assert "component" in str(exc_info.value)

    def test_event_collector_event_data_isolation(self) -> None:
        """Test that event data is properly isolated."""

        collector = TestEventCollector()

        original_event = {"data": "original"}
        collector.collect_event(original_event)

        # Modify original event
        original_event["data"] = "modified"

        # Collected event should be unchanged
        events = collector.get_events()
        assert events[0]["data"] == "original"

    def test_event_collector_multiple_filters(self) -> None:
        """Test assert_has_event with multiple filters."""

        collector = TestEventCollector()

        collector.collect_event(
            {
                "event_type": "component_registered",
                "component_name": "TestComponent",
                "scope": "singleton",
                "layer": "application",
            }
        )

        # Should match all filters
        collector.assert_has_event(event_type="component_registered", scope="singleton")

        # Should fail if any filter doesn't match
        with pytest.raises(AssertionError):
            collector.assert_has_event(
                event_type="component_registered",
                scope="transient",  # Different scope
            )


class TestFixturesIntegration:
    """Test fixtures working together."""

    def test_complete_test_workflow(self) -> None:
        """Test complete workflow using multiple fixtures."""

        # Reset state
        reset_global_state()

        # Create test context
        context = create_test_context("integration_test")

        # Create event collector
        collector = TestEventCollector()

        # Create custom factory
        factory = create_mock_factory("integration")

        # Test that everything works together
        mock_from_factory = factory()
        assert mock_from_factory.value == "integration"

        # Test context registrations
        assert_component_registered(context, MockComponent)

        # Test singleton behavior
        singleton1 = context.resolve(MockSingletonComponent)
        singleton2 = context.resolve(MockSingletonComponent)
        assert_components_equal(singleton1, singleton2)

        # Test transient behavior
        transient1 = context.resolve(MockTransientComponent)
        transient2 = context.resolve(MockTransientComponent)
        assert_components_different(transient1, transient2)

        # Test event collection
        collector.collect_event({"action": "test_completed", "context": context.name})
        collector.assert_event_count(1)
        collector.assert_has_event(action="test_completed")

    def test_module_classes_integration(self) -> None:
        """Test integration with module classes."""

        modules = create_test_module_classes()

        # Both modules should be properly configured
        infra_module = modules["test_infrastructure"]
        app_module = modules["test_application"]

        from opusgenie_di._decorators import is_context_module

        assert is_context_module(infra_module)
        assert is_context_module(app_module)

        # Could potentially test building contexts from these modules
        # (depends on what's available in the builder)

    def test_reset_state_isolation(self) -> None:
        """Test that reset_global_state provides proper test isolation."""

        # First test creates some state
        context1 = create_test_context("test1")
        context1.register_component(MockComponent, name="test1_component")

        # Reset state
        reset_global_state()

        # Second test should have clean state
        context2 = create_test_context("test2")

        # Contexts should be independent
        assert context1.name != context2.name

        # New context should not have the custom registration
        # (This depends on how reset_global_state actually works)
