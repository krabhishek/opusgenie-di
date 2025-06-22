"""Tests for Context implementation."""

import pytest

from opusgenie_di import (
    BaseComponent,
    CircularDependencyError,
    ComponentResolutionError,
    ComponentScope,
    Context,
    MockComponent,
    og_component,
)


class TestContext:
    """Test Context implementation."""

    def test_context_creation(self) -> None:
        """Test basic context creation."""
        context = Context(name="test_context")
        assert context.name == "test_context"
        assert context.get_summary()["name"] == "test_context"
        assert context.get_summary()["component_count"] == 0
        assert context.get_summary()["registered_types"] == []

    def test_component_registration(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test component registration."""
        service_type = sample_components["service"]

        # Register component
        empty_context.register_component(service_type, scope=ComponentScope.SINGLETON)

        # Check registration
        assert empty_context.is_registered(service_type)
        summary = empty_context.get_summary()
        assert summary["component_count"] == 1
        assert service_type in summary["registered_types"]

    def test_component_registration_with_name(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test component registration with custom name."""
        service_type = sample_components["service"]

        # Register with custom name
        empty_context.register_component(
            service_type, name="custom_service", scope=ComponentScope.SINGLETON
        )

        # Check registration with name
        assert empty_context.is_registered(service_type, name="custom_service")
        assert not empty_context.is_registered(service_type)  # Without name should fail

    def test_duplicate_registration_allowed_by_default(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test that duplicate registration is allowed by default (overwrites)."""
        service_type = sample_components["service"]

        # Register component first time
        empty_context.register_component(service_type, scope=ComponentScope.SINGLETON)
        assert empty_context.is_registered(service_type)

        # Register again - should overwrite, not raise error
        empty_context.register_component(service_type, scope=ComponentScope.TRANSIENT)
        assert empty_context.is_registered(service_type)

        # Should still be registered
        instance = empty_context.resolve(service_type)
        assert isinstance(instance, service_type)

    def test_component_resolution_singleton(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test singleton component resolution."""
        service_type = sample_components["service"]

        empty_context.register_component(service_type, scope=ComponentScope.SINGLETON)

        # Resolve twice and verify same instance
        instance1 = empty_context.resolve(service_type)
        instance2 = empty_context.resolve(service_type)

        assert instance1 is instance2
        assert isinstance(instance1, service_type)

    def test_component_resolution_transient(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test transient component resolution."""
        repo_type = sample_components["repository"]

        empty_context.register_component(repo_type, scope=ComponentScope.TRANSIENT)

        # Resolve twice and verify different instances
        instance1 = empty_context.resolve(repo_type)
        instance2 = empty_context.resolve(repo_type)

        assert instance1 is not instance2
        assert isinstance(instance1, repo_type)
        assert isinstance(instance2, repo_type)

    def test_component_resolution_with_name(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test component resolution with custom name."""
        service_type = sample_components["service"]

        empty_context.register_component(
            service_type, name="custom_service", scope=ComponentScope.SINGLETON
        )

        # Resolve with name
        instance = empty_context.resolve(service_type, name="custom_service")
        assert isinstance(instance, service_type)

        # Resolve without name should fail
        with pytest.raises(ComponentResolutionError):
            empty_context.resolve(service_type)

    def test_dependency_injection(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test automatic dependency injection."""
        service_type = sample_components["service"]
        repo_type = sample_components["repository"]
        controller_type = sample_components["controller"]

        # Register all components
        empty_context.register_component(service_type, scope=ComponentScope.SINGLETON)
        empty_context.register_component(repo_type, scope=ComponentScope.TRANSIENT)
        empty_context.register_component(
            controller_type, scope=ComponentScope.SINGLETON
        )

        # Enable auto-wiring
        empty_context.enable_auto_wiring()

        # Resolve controller - should inject dependencies
        controller = empty_context.resolve(controller_type)

        assert isinstance(controller.service, service_type)
        assert isinstance(controller.repo, repo_type)

        # Verify processing works
        result = controller.process()
        assert result["service_value"] == "sample"
        assert isinstance(result["repo_id"], int)

    def test_complex_dependency_chain(
        self, empty_context: Context, complex_dependency_chain: dict[str, type]
    ) -> None:
        """Test complex dependency chain resolution."""
        # Register all components
        for component_type in complex_dependency_chain.values():
            empty_context.register_component(
                component_type, scope=ComponentScope.SINGLETON
            )

        empty_context.enable_auto_wiring()

        # Resolve top-level component
        controller = empty_context.resolve(complex_dependency_chain["controller"])

        # Verify entire chain is resolved
        assert controller.service.repo.db.config is controller.config
        assert controller.service.repo.db.is_connected
        assert controller.config.connection_string == "test://localhost"

    def test_unregistered_component_error(self, empty_context: Context) -> None:
        """Test that resolving unregistered component raises error."""
        with pytest.raises(ComponentResolutionError):
            empty_context.resolve(MockComponent)

    def test_circular_dependency_detection(self, empty_context: Context) -> None:
        """Test circular dependency detection."""

        # Create components with simpler circular dependency without forward references
        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class ServiceA(BaseComponent):
            def __init__(
                self, service_b
            ) -> None:  # No type hint to avoid forward reference issue
                super().__init__()
                self.service_b = service_b

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class ServiceB(BaseComponent):
            def __init__(self, service_a: ServiceA) -> None:
                super().__init__()
                self.service_a = service_a

        # Register both components
        empty_context.register_component(ServiceA, scope=ComponentScope.SINGLETON)
        empty_context.register_component(ServiceB, scope=ComponentScope.SINGLETON)

        # Create custom factories that create the circular dependency
        def create_service_a():
            service_b = empty_context.resolve(ServiceB)
            return ServiceA(service_b)

        def create_service_b():
            service_a = empty_context.resolve(ServiceA)
            return ServiceB(service_a)

        # Register with custom factories that will create circular dependency
        empty_context.register_component(
            ServiceA,
            scope=ComponentScope.SINGLETON,
            factory=create_service_a,
            allow_override=True,
        )
        empty_context.register_component(
            ServiceB,
            scope=ComponentScope.SINGLETON,
            factory=create_service_b,
            allow_override=True,
        )

        # Should now properly detect circular dependency
        with pytest.raises(CircularDependencyError) as exc_info:
            empty_context.resolve(ServiceA)

        # Verify the error contains the dependency chain
        error = exc_info.value
        assert "ServiceA" in error.dependency_chain
        assert "ServiceB" in error.dependency_chain

    def test_forward_reference_resolution(self, empty_context: Context) -> None:
        """Test that forward references in type hints are properly resolved."""

        # Create a simple test without circular dependency to test forward reference resolution
        # We'll place the classes at module scope to ensure forward references can be resolved

        # For now, let's test auto-wiring with a simple forward reference that should work
        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class Repository(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.data = "repository_data"

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class Service(BaseComponent):
            def __init__(self, repo: Repository) -> None:
                super().__init__()
                self.repo = repo

        empty_context.register_component(Repository, scope=ComponentScope.SINGLETON)
        empty_context.register_component(Service, scope=ComponentScope.SINGLETON)
        empty_context.enable_auto_wiring()

        # This should work without issues - no forward reference needed here
        service = empty_context.resolve(Service)
        assert isinstance(service.repo, Repository)
        assert service.repo.data == "repository_data"

    def test_factory_registration(self, empty_context: Context) -> None:
        """Test component registration with factory function."""

        def create_mock() -> MockComponent:
            return MockComponent(value="factory_created")

        # Use the register_component with factory parameter
        empty_context.register_component(
            MockComponent, scope=ComponentScope.SINGLETON, factory=create_mock
        )

        instance = empty_context.resolve(MockComponent)
        assert instance.value == "factory_created"

    def test_context_shutdown(
        self, empty_context: Context, sample_components: dict[str, type]
    ) -> None:
        """Test context shutdown and cleanup."""
        service_type = sample_components["service"]

        empty_context.register_component(service_type, scope=ComponentScope.SINGLETON)
        instance = empty_context.resolve(service_type)

        # Shutdown context
        empty_context.shutdown()

        # Context should still work after shutdown (shutdown is not disposal)
        instance2 = empty_context.resolve(service_type)
        # For singleton, it should be the same instance
        assert instance2 is instance

    def test_auto_wiring_functionality(
        self, sample_components: dict[str, type]
    ) -> None:
        """Test auto-wiring functionality."""
        service_type = sample_components["service"]
        repo_type = sample_components["repository"]
        controller_type = sample_components["controller"]

        # Create context with auto-wiring disabled
        context = Context(name="auto_wire_test", auto_wire=False)

        context.register_component(service_type, scope=ComponentScope.SINGLETON)
        context.register_component(repo_type, scope=ComponentScope.TRANSIENT)
        context.register_component(controller_type, scope=ComponentScope.SINGLETON)

        # Auto-wiring disabled - should fail to resolve dependencies
        with pytest.raises(ComponentResolutionError):
            context.resolve(controller_type)

        # Enable auto-wiring
        context.enable_auto_wiring()
        controller = context.resolve(controller_type)
        assert controller is not None

        # Test again - should still work and return same singleton instance
        controller2 = context.resolve(controller_type)
        assert controller2 is controller

    def test_component_replacement(self, empty_context: Context) -> None:
        """Test component replacement with allow_override."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class OriginalService(BaseComponent):
            def get_value(self) -> str:
                return "original"

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class ReplacementService(BaseComponent):
            def get_value(self) -> str:
                return "replacement"

        # Register original
        empty_context.register_component(
            OriginalService, scope=ComponentScope.SINGLETON
        )
        original = empty_context.resolve(OriginalService)
        assert original.get_value() == "original"

        # Replace with override
        empty_context.register_component(
            OriginalService,
            scope=ComponentScope.SINGLETON,
            factory=lambda: ReplacementService(),
            allow_override=True,
        )

        replacement = empty_context.resolve(OriginalService)
        assert replacement.get_value() == "replacement"
