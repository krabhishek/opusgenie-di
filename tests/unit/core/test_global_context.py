"""Tests for GlobalContext functionality."""

from opusgenie_di import (
    BaseComponent,
    ComponentScope,
    get_global_context,
    get_global_context_summary,
    is_global_context_initialized,
    og_component,
    register_global_component,
    reset_global_context,
    resolve_global_component,
    resolve_global_component_async,
)


class TestGlobalContext:
    """Test GlobalContext functionality."""

    def test_global_context_singleton(self) -> None:
        """Test that global context is singleton."""
        context1 = get_global_context()
        context2 = get_global_context()

        assert context1 is context2
        assert context1.name == "global"

    def test_global_context_initialization_check(self) -> None:
        """Test global context initialization check."""
        # After reset, should not be initialized
        reset_global_context()
        assert not is_global_context_initialized()

        # After getting context, should be initialized
        get_global_context()
        assert is_global_context_initialized()

    def test_global_component_registration(self) -> None:
        """Test global component registration."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class GlobalTestService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "global_test"

        register_global_component(GlobalTestService, scope=ComponentScope.SINGLETON)

        context = get_global_context()
        assert context.is_registered(GlobalTestService)

    def test_global_component_resolution(self) -> None:
        """Test global component resolution."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class GlobalResolveService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "resolve_test"

        register_global_component(GlobalResolveService, scope=ComponentScope.SINGLETON)

        instance = resolve_global_component(GlobalResolveService)
        assert isinstance(instance, GlobalResolveService)
        assert instance.value == "resolve_test"

    async def test_global_component_async_resolution(self) -> None:
        """Test global component async resolution."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class GlobalAsyncService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "async_test"

        register_global_component(GlobalAsyncService, scope=ComponentScope.SINGLETON)

        instance = await resolve_global_component_async(GlobalAsyncService)
        assert isinstance(instance, GlobalAsyncService)
        assert instance.value == "async_test"

    def test_global_context_summary(self) -> None:
        """Test global context summary."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class SummaryTestService(BaseComponent):
            pass

        register_global_component(SummaryTestService, scope=ComponentScope.SINGLETON)

        summary = get_global_context_summary()
        assert summary["name"] == "global"
        assert summary["component_count"] >= 1
        assert SummaryTestService in summary["registered_types"]

    def test_global_context_auto_registration(self) -> None:
        """Test automatic registration to global context."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=True)
        class AutoRegisteredService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "auto_registered"

        context = get_global_context()
        assert context.is_registered(AutoRegisteredService)

        instance = resolve_global_component(AutoRegisteredService)
        assert instance.value == "auto_registered"

    def test_global_context_reset(self) -> None:
        """Test global context reset functionality."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class ResetTestService(BaseComponent):
            pass

        # Register component
        register_global_component(ResetTestService, scope=ComponentScope.SINGLETON)
        context = get_global_context()
        assert context.is_registered(ResetTestService)

        # Reset global context
        reset_global_context()

        # Should not be initialized
        assert not is_global_context_initialized()

        # New context should not have previous registrations
        new_context = get_global_context()
        assert not new_context.is_registered(ResetTestService)
        assert new_context is not context

    def test_global_context_with_dependencies(self) -> None:
        """Test global context with dependency injection."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class GlobalDependency(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "dependency"

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class GlobalService(BaseComponent):
            def __init__(self, dep: GlobalDependency) -> None:
                super().__init__()
                self.dep = dep

        register_global_component(GlobalDependency, scope=ComponentScope.SINGLETON)
        register_global_component(GlobalService, scope=ComponentScope.SINGLETON)

        context = get_global_context()
        context.enable_auto_wiring()

        service = resolve_global_component(GlobalService)
        assert isinstance(service.dep, GlobalDependency)
        assert service.dep.value == "dependency"

    def test_global_context_transient_components(self) -> None:
        """Test global context with transient components."""

        @og_component(scope=ComponentScope.TRANSIENT, auto_register=False)
        class GlobalTransientService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.instance_id = id(self)

        register_global_component(
            GlobalTransientService, scope=ComponentScope.TRANSIENT
        )

        instance1 = resolve_global_component(GlobalTransientService)
        instance2 = resolve_global_component(GlobalTransientService)

        assert instance1 is not instance2
        assert instance1.instance_id != instance2.instance_id

    def test_global_context_factory_registration(self) -> None:
        """Test global context factory registration."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class GlobalFactoryService(BaseComponent):
            def __init__(self, value: str) -> None:
                super().__init__()
                self.value = value

        def create_factory_service() -> GlobalFactoryService:
            return GlobalFactoryService(value="factory_created")

        context = get_global_context()
        context.register_component(
            GlobalFactoryService,
            scope=ComponentScope.SINGLETON,
            factory=create_factory_service,
        )

        instance = resolve_global_component(GlobalFactoryService)
        assert instance.value == "factory_created"

    def test_global_context_instance_registration(self) -> None:
        """Test global context instance registration."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class GlobalInstanceService(BaseComponent):
            def __init__(self, value: str) -> None:
                super().__init__()
                self.value = value

        instance = GlobalInstanceService(value="pre_created")

        context = get_global_context()
        context.register_component(
            GlobalInstanceService,
            scope=ComponentScope.SINGLETON,
            factory=lambda: instance,
        )

        resolved = resolve_global_component(GlobalInstanceService)
        assert resolved is instance
        assert resolved.value == "pre_created"

    def test_global_context_multiple_registrations(self) -> None:
        """Test multiple component registrations in global context."""

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class ServiceA(BaseComponent):
            pass

        @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
        class ServiceB(BaseComponent):
            pass

        @og_component(scope=ComponentScope.TRANSIENT, auto_register=False)
        class ServiceC(BaseComponent):
            pass

        register_global_component(ServiceA, scope=ComponentScope.SINGLETON)
        register_global_component(ServiceB, scope=ComponentScope.SINGLETON)
        register_global_component(ServiceC, scope=ComponentScope.TRANSIENT)

        summary = get_global_context_summary()
        assert summary["component_count"] >= 3

        # Verify all can be resolved
        a = resolve_global_component(ServiceA)
        b = resolve_global_component(ServiceB)
        c1 = resolve_global_component(ServiceC)
        c2 = resolve_global_component(ServiceC)

        assert isinstance(a, ServiceA)
        assert isinstance(b, ServiceB)
        assert isinstance(c1, ServiceC)
        assert isinstance(c2, ServiceC)
        assert c1 is not c2  # Transient should be different instances
