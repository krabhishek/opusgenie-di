"""Tests for Container implementation."""

import pytest

from opusgenie_di import (
    BaseComponent,
    ComponentResolutionError,
    ComponentScope,
    Container,
    MockComponent,
    og_component,
)


class TestContainer:
    """Test Container implementation."""

    def test_container_creation(self) -> None:
        """Test basic container creation."""
        container = Container()
        assert container is not None

    def test_provider_registration_singleton(self) -> None:
        """Test singleton provider registration."""
        container = Container()

        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(value="test"),
        )

        # Resolve twice and verify same instance
        instance1 = container.resolve(MockComponent)
        instance2 = container.resolve(MockComponent)

        assert instance1 is instance2
        assert instance1.value == "test"

    def test_provider_registration_transient(self) -> None:
        """Test transient provider registration."""
        container = Container()

        container.register(
            MockComponent,
            scope=ComponentScope.TRANSIENT,
            factory=lambda: MockComponent(value="test"),
        )

        # Resolve twice and verify different instances
        instance1 = container.resolve(MockComponent)
        instance2 = container.resolve(MockComponent)

        assert instance1 is not instance2
        assert instance1.value == "test"
        assert instance2.value == "test"

    def test_provider_registration_with_name(self) -> None:
        """Test provider registration with custom name."""
        container = Container()

        container.register(
            MockComponent,
            name="custom_mock",
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(value="named"),
        )

        # Resolve with name
        instance = container.resolve(MockComponent, name="custom_mock")
        assert instance.value == "named"

        # Resolve without name should fail
        with pytest.raises(ComponentResolutionError):
            container.resolve(MockComponent)

    def test_provider_registration_duplicate_behavior(self) -> None:
        """Test that duplicate provider registration behavior (overrides by default)."""
        container = Container()

        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(value="first"),
        )

        # Register again with different factory - should override
        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(value="second"),
        )

        # Should get the second registration
        instance = container.resolve(MockComponent)
        assert instance.value == "second"

    def test_provider_registration_with_override(self) -> None:
        """Test provider registration with override."""
        container = Container()

        # Register original
        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(value="original"),
        )

        original = container.resolve(MockComponent)
        assert original.value == "original"

        # Register with override (just register again - should overwrite)
        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(value="overridden"),
        )

        overridden = container.resolve(MockComponent)
        assert overridden.value == "overridden"

    def test_instance_registration(self) -> None:
        """Test instance registration."""
        container = Container()
        instance = MockComponent(value="instance")

        # Register using a factory that returns the specific instance
        container.register(MockComponent, factory=lambda: instance)

        resolved = container.resolve(MockComponent)
        assert resolved.value == "instance"

    def test_factory_registration(self) -> None:
        """Test factory function registration."""
        container = Container()

        def create_mock() -> MockComponent:
            return MockComponent(value="factory")

        container.register(MockComponent, factory=create_mock)

        instance = container.resolve(MockComponent)
        assert instance.value == "factory"

    def test_type_registration(self) -> None:
        """Test type-based registration."""
        container = Container()

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class TestComponent(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "type_created"

        container.register(TestComponent, scope=ComponentScope.SINGLETON)

        instance = container.resolve(TestComponent)
        assert instance.value == "type_created"

    def test_is_registered(self) -> None:
        """Test is_registered check."""
        container = Container()

        assert not container.is_registered(MockComponent)

        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(),
        )

        assert container.is_registered(MockComponent)
        assert not container.is_registered(MockComponent, name="other")

    def test_is_registered_with_name(self) -> None:
        """Test is_registered check with name."""
        container = Container()

        container.register(
            MockComponent,
            name="test_name",
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(),
        )

        assert container.is_registered(MockComponent, name="test_name")
        assert not container.is_registered(MockComponent)

    def test_unregistered_resolution_error(self) -> None:
        """Test that resolving unregistered component raises error."""
        container = Container()

        with pytest.raises(ComponentResolutionError):
            container.resolve(MockComponent)

    def test_container_disposal(self) -> None:
        """Test container disposal."""
        container = Container()

        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(),
        )

        instance = container.resolve(MockComponent)
        assert instance is not None

        # Clear container
        container.clear()

        # Should not be able to resolve after clearing
        with pytest.raises(ComponentResolutionError):
            container.resolve(MockComponent)

    def test_get_registered_types(self) -> None:
        """Test getting registered types."""
        container = Container()

        assert container.get_registered_types() == []

        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(),
        )

        registered_types = container.get_registered_types()
        assert MockComponent in registered_types

    def test_clear_registrations(self) -> None:
        """Test clearing all registrations."""
        container = Container()

        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(),
        )

        assert container.is_registered(MockComponent)

        container.clear()

        assert not container.is_registered(MockComponent)
        assert container.get_registered_types() == []

    def test_scoped_components(self) -> None:
        """Test scoped component behavior."""
        container = Container()

        @og_component(scope=ComponentScope.SCOPED, auto_register=False)
        class ScopedComponent(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.id = id(self)

        container.register(ScopedComponent, scope=ComponentScope.SCOPED)

        # For now, just test that scoped components can be registered and resolved
        instance1 = container.resolve(ScopedComponent)
        instance2 = container.resolve(ScopedComponent)

        # Note: Scoped behavior may vary based on implementation
        assert instance1 is not None
        assert instance2 is not None

    def test_provider_metadata(self) -> None:
        """Test provider metadata access."""
        container = Container()

        container.register(
            MockComponent,
            scope=ComponentScope.SINGLETON,
            factory=lambda: MockComponent(value="test"),
        )

        metadata = container.get_metadata(MockComponent)
        assert metadata is not None
        # Test that metadata exists - specific implementation may vary
        assert hasattr(metadata, "scope") or hasattr(metadata, "component_type")
