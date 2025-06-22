"""Testing utilities for dependency injection."""

from .fixtures import (
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

__all__ = [
    # Mock components
    "MockComponent",
    "MockSingletonComponent",
    "MockTransientComponent",
    "MockComponentWithDependency",
    # Test utilities
    "create_test_context",
    "reset_global_state",
    "create_mock_factory",
    "create_test_module_classes",
    # Assertions
    "assert_component_registered",
    "assert_component_not_registered",
    "assert_components_equal",
    "assert_components_different",
    # Event testing
    "TestEventCollector",
]
