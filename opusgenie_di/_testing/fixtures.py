"""Test fixtures and utilities for dependency injection testing."""

from typing import Any

from .._base import BaseComponent, ComponentScope
from .._core import Context, reset_global_context
from .._decorators import og_component
from .._hooks import clear_all_hooks_global as clear_all_hooks
from .._hooks import set_hooks_enabled
from .._registry import clear_global_registry
from .._utils import get_logger

logger = get_logger(__name__)


class MockComponent(BaseComponent):
    """Mock component for testing purposes."""

    def __init__(self, value: str = "mock", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.value = value
        self.call_count = 0

    def mock_method(self) -> str:
        """Mock method for testing."""
        self.call_count += 1
        return f"{self.value}_{self.call_count}"

    def reset_call_count(self) -> None:
        """Reset the call count."""
        self.call_count = 0


@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class MockSingletonComponent(MockComponent):
    """Mock singleton component for testing."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(value="singleton", **kwargs)


@og_component(scope=ComponentScope.TRANSIENT, auto_register=False)
class MockTransientComponent(MockComponent):
    """Mock transient component for testing."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(value="transient", **kwargs)


class MockComponentWithDependency(BaseComponent):
    """Mock component with dependencies for testing injection."""

    def __init__(self, dependency: MockComponent | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.dependency = dependency

    def get_dependency_value(self) -> str:
        """Get value from dependency."""
        if self.dependency:
            return self.dependency.mock_method()
        return "no_dependency"


def create_test_context(name: str = "test") -> Context:
    """
    Create a test context with common test components.

    Args:
        name: Name for the test context

    Returns:
        Test context with mock components
    """
    context = Context(name=name)

    # Register mock components
    context.register_component(MockComponent, scope=ComponentScope.SINGLETON)
    context.register_component(MockSingletonComponent, scope=ComponentScope.SINGLETON)
    context.register_component(MockTransientComponent, scope=ComponentScope.TRANSIENT)
    context.register_component(
        MockComponentWithDependency, scope=ComponentScope.SINGLETON
    )

    logger.debug("Created test context", context_name=name)
    return context


def reset_global_state() -> None:
    """
    Reset all global state for testing.

    This function should be called between tests to ensure clean state.
    """
    # Reset global context
    reset_global_context()

    # Clear global registry
    clear_global_registry()

    # Clear hooks
    clear_all_hooks()

    # Ensure hooks are enabled
    set_hooks_enabled(True)

    logger.debug("Reset global DI state for testing")


def create_mock_factory(value: str) -> Any:
    """
    Create a mock factory function.

    Args:
        value: Value to return from created components

    Returns:
        Factory function
    """

    def factory() -> MockComponent:
        return MockComponent(value=value)

    return factory


def assert_component_registered(
    context: Context, component_type: type, name: str | None = None
) -> None:
    """
    Assert that a component is registered in a context.

    Args:
        context: Context to check
        component_type: Component type to check
        name: Optional component name

    Raises:
        AssertionError: If component is not registered
    """
    if not context.is_registered(component_type, name):
        component_name = name or component_type.__name__
        raise AssertionError(
            f"Component {component_name} is not registered in context {context.name}"
        )


def assert_component_not_registered(
    context: Context, component_type: type, name: str | None = None
) -> None:
    """
    Assert that a component is not registered in a context.

    Args:
        context: Context to check
        component_type: Component type to check
        name: Optional component name

    Raises:
        AssertionError: If component is registered
    """
    if context.is_registered(component_type, name):
        component_name = name or component_type.__name__
        raise AssertionError(
            f"Component {component_name} is registered in context {context.name} but should not be"
        )


def assert_components_equal(component1: Any, component2: Any) -> None:
    """
    Assert that two components are the same instance (for singleton testing).

    Args:
        component1: First component
        component2: Second component

    Raises:
        AssertionError: If components are not the same instance
    """
    if component1 is not component2:
        raise AssertionError(
            f"Components are not the same instance: {id(component1)} != {id(component2)}"
        )


def assert_components_different(component1: Any, component2: Any) -> None:
    """
    Assert that two components are different instances (for transient testing).

    Args:
        component1: First component
        component2: Second component

    Raises:
        AssertionError: If components are the same instance
    """
    if component1 is component2:
        raise AssertionError(
            f"Components are the same instance but should be different: {id(component1)}"
        )


def create_test_module_classes() -> dict[str, type]:
    """
    Create test module classes for testing module system.

    Returns:
        Dictionary mapping module names to module classes
    """
    from .._decorators import og_context
    from .._modules import ModuleContextImport

    @og_context(
        name="test_infrastructure",
        exports=[MockComponent],
        providers=[MockComponent],
    )
    class TestInfrastructureModule:
        pass

    @og_context(
        name="test_application",
        imports=[
            ModuleContextImport(
                component_type=MockComponent, from_context="test_infrastructure"
            )
        ],
        exports=[MockComponentWithDependency],
        providers=[MockComponentWithDependency],
    )
    class TestApplicationModule:
        pass

    return {
        "test_infrastructure": TestInfrastructureModule,
        "test_application": TestApplicationModule,
    }


class TestEventCollector:
    """Utility for collecting events during tests."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def collect_event(self, event_data: dict[str, Any]) -> None:
        """Collect an event."""
        self.events.append(event_data.copy())

    def get_events(self) -> list[dict[str, Any]]:
        """Get collected events."""
        return self.events.copy()

    def get_events_by_type(self, event_type: str) -> list[dict[str, Any]]:
        """Get events of a specific type."""
        return [event for event in self.events if event.get("event_type") == event_type]

    def clear_events(self) -> None:
        """Clear collected events."""
        self.events.clear()

    def get_event_count(self) -> int:
        """Get the number of collected events."""
        return len(self.events)

    def assert_event_count(self, expected_count: int) -> None:
        """Assert the number of collected events."""
        actual_count = len(self.events)
        if actual_count != expected_count:
            raise AssertionError(
                f"Expected {expected_count} events, but got {actual_count}"
            )

    def assert_has_event(self, **event_filters: Any) -> None:
        """Assert that an event with specific properties was collected."""
        for event in self.events:
            if all(event.get(key) == value for key, value in event_filters.items()):
                return
        raise AssertionError(f"No event found matching filters: {event_filters}")
