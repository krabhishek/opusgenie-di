from .._base import BaseComponent as BaseComponent, ComponentScope as ComponentScope
from .._core import Context as Context, reset_global_context as reset_global_context
from .._decorators import og_component as og_component
from .._hooks import set_hooks_enabled as set_hooks_enabled
from .._registry import clear_global_registry as clear_global_registry
from .._utils import get_logger as get_logger
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class MockComponent(BaseComponent):
    """Mock component for testing purposes."""
    value: Incomplete
    call_count: int
    def __init__(self, value: str = 'mock', **kwargs: Any) -> None: ...
    def mock_method(self) -> str:
        """Mock method for testing."""
    def reset_call_count(self) -> None:
        """Reset the call count."""

class MockSingletonComponent(MockComponent):
    """Mock singleton component for testing."""
    def __init__(self, **kwargs: Any) -> None: ...

class MockTransientComponent(MockComponent):
    """Mock transient component for testing."""
    def __init__(self, **kwargs: Any) -> None: ...

class MockComponentWithDependency(BaseComponent):
    """Mock component with dependencies for testing injection."""
    dependency: Incomplete
    def __init__(self, dependency: MockComponent | None = None, **kwargs: Any) -> None: ...
    def get_dependency_value(self) -> str:
        """Get value from dependency."""

def create_test_context(name: str = 'test') -> Context:
    """
    Create a test context with common test components.

    Args:
        name: Name for the test context

    Returns:
        Test context with mock components
    """
def reset_global_state() -> None:
    """
    Reset all global state for testing.

    This function should be called between tests to ensure clean state.
    """
def create_mock_factory(value: str) -> Any:
    """
    Create a mock factory function.

    Args:
        value: Value to return from created components

    Returns:
        Factory function
    """
def assert_component_registered(context: Context, component_type: type, name: str | None = None) -> None:
    """
    Assert that a component is registered in a context.

    Args:
        context: Context to check
        component_type: Component type to check
        name: Optional component name

    Raises:
        AssertionError: If component is not registered
    """
def assert_component_not_registered(context: Context, component_type: type, name: str | None = None) -> None:
    """
    Assert that a component is not registered in a context.

    Args:
        context: Context to check
        component_type: Component type to check
        name: Optional component name

    Raises:
        AssertionError: If component is registered
    """
def assert_components_equal(component1: Any, component2: Any) -> None:
    """
    Assert that two components are the same instance (for singleton testing).

    Args:
        component1: First component
        component2: Second component

    Raises:
        AssertionError: If components are not the same instance
    """
def assert_components_different(component1: Any, component2: Any) -> None:
    """
    Assert that two components are different instances (for transient testing).

    Args:
        component1: First component
        component2: Second component

    Raises:
        AssertionError: If components are the same instance
    """
def create_test_module_classes() -> dict[str, type]:
    """
    Create test module classes for testing module system.

    Returns:
        Dictionary mapping module names to module classes
    """

class TestEventCollector:
    """Utility for collecting events during tests."""
    events: list[dict[str, Any]]
    def __init__(self) -> None: ...
    def collect_event(self, event_data: dict[str, Any]) -> None:
        """Collect an event."""
    def get_events(self) -> list[dict[str, Any]]:
        """Get collected events."""
    def get_events_by_type(self, event_type: str) -> list[dict[str, Any]]:
        """Get events of a specific type."""
    def clear_events(self) -> None:
        """Clear collected events."""
    def get_event_count(self) -> int:
        """Get the number of collected events."""
    def assert_event_count(self, expected_count: int) -> None:
        """Assert the number of collected events."""
    def assert_has_event(self, **event_filters: Any) -> None:
        """Assert that an event with specific properties was collected."""
