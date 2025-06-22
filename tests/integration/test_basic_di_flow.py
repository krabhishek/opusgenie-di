"""Test basic dependency injection flow."""

from opusgenie_di import (
    BaseComponent,
    ComponentScope,
    Context,
    get_global_context,
    og_component,
)


class TestBasicDIFlow:
    """Test basic dependency injection workflow."""

    def test_simple_dependency_injection(self) -> None:
        """Test simple dependency injection flow."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class DatabaseService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.connection = "connected"

            def get_data(self) -> str:
                return f"data from {self.connection} database"

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class UserService(BaseComponent):
            def __init__(self, db: DatabaseService) -> None:
                super().__init__()
                self.db = db

            def get_user(self, user_id: str) -> dict[str, str]:
                return {"id": user_id, "data": self.db.get_data()}

        # Create context and register components
        context = Context(name="test_context")
        context.register_component(DatabaseService, scope=ComponentScope.SINGLETON)
        context.register_component(UserService, scope=ComponentScope.SINGLETON)
        context.enable_auto_wiring()

        # Resolve and test
        user_service = context.resolve(UserService)
        user_data = user_service.get_user("123")

        assert user_data["id"] == "123"
        assert "data from connected database" in user_data["data"]
        assert isinstance(user_service.db, DatabaseService)

    def test_global_context_usage(self) -> None:
        """Test global context usage."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=True)
        class GlobalService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "global_service"

            def get_value(self) -> str:
                return self.value

        # Get global context and enable auto-wiring
        context = get_global_context()
        context.enable_auto_wiring()

        # Resolve component
        service = context.resolve(GlobalService)
        assert service.get_value() == "global_service"

        # Verify singleton behavior
        service2 = context.resolve(GlobalService)
        assert service is service2

    def test_transient_vs_singleton_behavior(self) -> None:
        """Test transient vs singleton component behavior."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class SingletonService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.instance_id = id(self)

        @og_component(scope=ComponentScope.TRANSIENT, auto_register=False)
        class TransientService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.instance_id = id(self)

        context = Context(name="scope_test")
        context.register_component(SingletonService, scope=ComponentScope.SINGLETON)
        context.register_component(TransientService, scope=ComponentScope.TRANSIENT)

        # Test singleton behavior
        singleton1 = context.resolve(SingletonService)
        singleton2 = context.resolve(SingletonService)
        assert singleton1 is singleton2
        assert singleton1.instance_id == singleton2.instance_id

        # Test transient behavior
        transient1 = context.resolve(TransientService)
        transient2 = context.resolve(TransientService)
        assert transient1 is not transient2
        assert transient1.instance_id != transient2.instance_id

    def test_context_isolation(self) -> None:
        """Test that contexts are properly isolated."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class IsolatedService(BaseComponent):
            def __init__(self, value: str = "default") -> None:
                super().__init__()
                self.value = value

        # Create two separate contexts
        context1 = Context(name="context1")
        context2 = Context(name="context2")

        # Register service with different factory in each context
        context1.register_component(
            IsolatedService,
            scope=ComponentScope.SINGLETON,
            factory=lambda: IsolatedService(value="context1_value"),
        )
        context2.register_component(
            IsolatedService,
            scope=ComponentScope.SINGLETON,
            factory=lambda: IsolatedService(value="context2_value"),
        )

        # Resolve from each context
        service1 = context1.resolve(IsolatedService)
        service2 = context2.resolve(IsolatedService)

        assert service1.value == "context1_value"
        assert service2.value == "context2_value"
        assert service1 is not service2

    def test_component_with_optional_dependencies(self) -> None:
        """Test component with optional dependencies."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class OptionalDependency(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.available = True

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class ServiceWithOptional(BaseComponent):
            def __init__(self, optional_dep: OptionalDependency | None = None) -> None:
                super().__init__()
                self.optional_dep = optional_dep

            def has_dependency(self) -> bool:
                return self.optional_dep is not None

        context = Context(name="optional_test")

        # Register only the main service, not the optional dependency
        context.register_component(ServiceWithOptional, scope=ComponentScope.SINGLETON)
        context.enable_auto_wiring()

        # Should work without the optional dependency
        service = context.resolve(ServiceWithOptional)
        assert not service.has_dependency()

        # Now register the optional dependency
        context.register_component(OptionalDependency, scope=ComponentScope.SINGLETON)

        # Create new service instance (for this test, we'll create manually)
        optional_dep = context.resolve(OptionalDependency)
        service_with_dep = ServiceWithOptional(optional_dep)
        assert service_with_dep.has_dependency()

    def test_factory_registration(self) -> None:
        """Test factory-based component registration."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class FactoryCreatedService(BaseComponent):
            def __init__(self, config: dict[str, str]) -> None:
                super().__init__()
                self.config = config

        def create_configured_service() -> FactoryCreatedService:
            return FactoryCreatedService(config={"env": "test", "db": "memory"})

        context = Context(name="factory_test")
        context.register_component(
            FactoryCreatedService,
            scope=ComponentScope.SINGLETON,
            factory=create_configured_service,
        )

        service = context.resolve(FactoryCreatedService)
        assert service.config["env"] == "test"
        assert service.config["db"] == "memory"

    def test_instance_registration(self) -> None:
        """Test instance-based component registration."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class PreCreatedService(BaseComponent):
            def __init__(self, value: str) -> None:
                super().__init__()
                self.value = value

        # Create instance ahead of time
        pre_created = PreCreatedService(value="pre_created")

        context = Context(name="instance_test")
        # Note: Direct instance registration might not be available, so we'll use a factory
        context.register_component(
            PreCreatedService,
            scope=ComponentScope.SINGLETON,
            factory=lambda: pre_created,
        )

        resolved = context.resolve(PreCreatedService)
        assert resolved is pre_created
        assert resolved.value == "pre_created"

    def test_context_summary(self) -> None:
        """Test context summary functionality."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class SummaryService1(BaseComponent):
            pass

        @og_component(scope=ComponentScope.TRANSIENT, auto_register=False)
        class SummaryService2(BaseComponent):
            pass

        context = Context(name="summary_test")
        context.register_component(SummaryService1, scope=ComponentScope.SINGLETON)
        context.register_component(SummaryService2, scope=ComponentScope.TRANSIENT)

        summary = context.get_summary()

        assert summary["name"] == "summary_test"
        assert summary["component_count"] == 2
        assert SummaryService1 in summary["registered_types"]
        assert SummaryService2 in summary["registered_types"]
