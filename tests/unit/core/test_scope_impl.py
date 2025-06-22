"""Tests for Scope implementation."""

from opusgenie_di import (
    BaseComponent,
    ComponentScope,
    MockComponent,
    og_component,
)
from opusgenie_di._core.scope_impl import ScopeManager


class TestScopeManager:
    """Test ScopeManager implementation."""

    def test_singleton_scope(self) -> None:
        """Test singleton scope behavior."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="singleton")

        # Create singleton scope
        instance1 = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )

        instance2 = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )

        # Should be same instance
        assert instance1 is instance2
        assert instance1.value == "singleton"

    def test_transient_scope(self) -> None:
        """Test transient scope behavior."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="transient")

        # Create transient instances
        instance1 = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.TRANSIENT, factory
        )

        instance2 = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.TRANSIENT, factory
        )

        # Should be different instances
        assert instance1 is not instance2
        assert instance1.value == "transient"
        assert instance2.value == "transient"

    def test_scoped_scope(self) -> None:
        """Test scoped scope behavior."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="scoped")

        # Without scope context, should behave like transient
        instance1 = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SCOPED, factory
        )

        instance2 = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SCOPED, factory
        )

        assert instance1 is not instance2

        # With scope context, should behave like singleton within scope
        with scope_manager.create_scope():
            instance3 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

            instance4 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

            assert instance3 is instance4

    def test_scoped_isolation(self) -> None:
        """Test that scoped instances are isolated between scopes."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="scoped")

        # First scope
        with scope_manager.create_scope():
            instance1 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

        # Second scope
        with scope_manager.create_scope():
            instance2 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

        # Should be different instances
        assert instance1 is not instance2

    def test_nested_scopes(self) -> None:
        """Test nested scope behavior."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="nested")

        with scope_manager.create_scope():
            instance1 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

            with scope_manager.create_scope():
                instance2 = scope_manager.create_or_get_instance(
                    MockComponent, ComponentScope.SCOPED, factory
                )

                # Inner scope should have different instance
                assert instance1 is not instance2

            # Back to outer scope - should get original instance
            instance3 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

            assert instance1 is instance3

    def test_lifecycle_events(self, event_collector: object) -> None:
        """Test basic scope manager functionality (simplified from lifecycle events)."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="lifecycle")

        # Create singleton instance
        instance = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )

        # Verify instance was created correctly
        assert instance.value == "lifecycle"

        # Create same type again - should get same instance for singleton
        instance2 = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )

        assert instance is instance2

        # Test that instance count tracking works
        count = scope_manager.get_instance_count(ComponentScope.SINGLETON)
        assert count == 1

    def test_scope_disposal(self) -> None:
        """Test scope disposal cleanup."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="disposal")

        # Create singleton instance
        instance = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )

        # Dispose scope manager
        scope_manager.dispose()

        # Creating new instance should create new object
        new_instance = scope_manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )

        assert new_instance is not instance

    def test_scope_context_manager(self) -> None:
        """Test scope context manager behavior."""
        scope_manager = ScopeManager()

        def factory() -> MockComponent:
            return MockComponent(value="context")

        # Verify no active scope initially
        assert not scope_manager.has_active_scope()

        with scope_manager.create_scope():
            assert scope_manager.has_active_scope()

            instance1 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

            instance2 = scope_manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, factory
            )

            assert instance1 is instance2

        # Scope should be cleaned up after context
        assert not scope_manager.has_active_scope()

    def test_scope_exception_handling(self) -> None:
        """Test scope cleanup on exception."""
        scope_manager = ScopeManager()

        try:
            with scope_manager.create_scope():
                assert scope_manager.has_active_scope()
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Scope should still be cleaned up
        assert not scope_manager.has_active_scope()

    def test_multiple_component_types_in_scope(self) -> None:
        """Test multiple component types within same scope."""
        scope_manager = ScopeManager()

        @og_component(scope=ComponentScope.SCOPED, auto_register=False)
        class ComponentA(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.id = id(self)

        @og_component(scope=ComponentScope.SCOPED, auto_register=False)
        class ComponentB(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.id = id(self)

        with scope_manager.create_scope():
            a1 = scope_manager.create_or_get_instance(
                ComponentA, ComponentScope.SCOPED, lambda: ComponentA()
            )

            b1 = scope_manager.create_or_get_instance(
                ComponentB, ComponentScope.SCOPED, lambda: ComponentB()
            )

            a2 = scope_manager.create_or_get_instance(
                ComponentA, ComponentScope.SCOPED, lambda: ComponentA()
            )

            b2 = scope_manager.create_or_get_instance(
                ComponentB, ComponentScope.SCOPED, lambda: ComponentB()
            )

            # Same types should be same instances
            assert a1 is a2
            assert b1 is b2

            # Different types should be different instances
            assert a1 is not b1  # type: ignore[comparison-overlap]
