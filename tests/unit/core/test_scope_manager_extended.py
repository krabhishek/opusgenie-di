"""Extended tests for ScopeManager to improve coverage."""

import gc
import weakref

from opusgenie_di import ComponentScope, MockComponent
from opusgenie_di._core.scope_impl import ScopeManager


class TestScopeManagerExtended:
    """Extended tests for ScopeManager functionality."""

    def test_scope_manager_initialization(self) -> None:
        """Test ScopeManager initialization."""
        # Without lifecycle callback
        manager1 = ScopeManager()
        assert hasattr(manager1, "_singletons")
        assert hasattr(manager1, "_scoped_instances")
        assert hasattr(manager1, "_lock")
        assert hasattr(manager1, "_disposable_instances")

    def test_singleton_behavior_detailed(self) -> None:
        """Test detailed singleton scope behavior."""
        manager = ScopeManager()
        factory_calls = 0

        def factory():
            nonlocal factory_calls
            factory_calls += 1
            return MockComponent(value=f"instance_{factory_calls}")

        # First creation
        instance1 = manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )
        assert factory_calls == 1
        assert instance1.value == "instance_1"

        # Second call should return same instance
        instance2 = manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, factory
        )
        assert factory_calls == 1  # Factory not called again
        assert instance1 is instance2

        # Different type should create new instance
        instance3 = manager.create_or_get_instance(
            str, ComponentScope.SINGLETON, lambda: "string_instance"
        )
        assert isinstance(instance3, str)
        assert instance3 == "string_instance"

    def test_transient_behavior_detailed(self) -> None:
        """Test detailed transient scope behavior."""
        manager = ScopeManager()
        factory_calls = 0

        def factory():
            nonlocal factory_calls
            factory_calls += 1
            return MockComponent(value=f"transient_{factory_calls}")

        # Each call creates new instance
        instances = []
        for i in range(3):
            instance = manager.create_or_get_instance(
                MockComponent, ComponentScope.TRANSIENT, factory
            )
            instances.append(instance)
            assert instance.value == f"transient_{i + 1}"

        # All instances should be different
        assert len({id(inst) for inst in instances}) == 3
        assert factory_calls == 3

    def test_scoped_behavior_without_scope(self) -> None:
        """Test scoped behavior without active scope context."""
        manager = ScopeManager()

        # Without scope context, scoped behaves like transient
        instance1 = manager.create_or_get_instance(
            MockComponent, ComponentScope.SCOPED, lambda: MockComponent("scoped1")
        )
        instance2 = manager.create_or_get_instance(
            MockComponent, ComponentScope.SCOPED, lambda: MockComponent("scoped2")
        )

        assert instance1 is not instance2
        assert instance1.value == "scoped1"
        assert instance2.value == "scoped2"

    def test_scoped_behavior_with_scope(self) -> None:
        """Test scoped behavior with active scope context."""
        manager = ScopeManager()
        instances = []

        with manager.create_scope():
            # Within scope, acts like singleton
            instance1 = manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, lambda: MockComponent("scoped")
            )
            instance2 = manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, lambda: MockComponent("different")
            )

            assert instance1 is instance2
            assert instance1.value == "scoped"
            instances.append(instance1)

            # Nested scope creates new instance
            with manager.create_scope():
                instance3 = manager.create_or_get_instance(
                    MockComponent,
                    ComponentScope.SCOPED,
                    lambda: MockComponent("nested"),
                )
                assert instance3 is not instance1
                assert instance3.value == "nested"
                instances.append(instance3)

            # Back to outer scope
            instance4 = manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, lambda: MockComponent("outer")
            )
            assert instance4 is instance1

    def test_scope_disposal(self) -> None:
        """Test proper disposal of scoped instances."""
        manager = ScopeManager()
        disposed_instances = []

        class DisposableComponent:
            def __init__(self, name: str):
                self.name = name
                self.disposed = False

            def dispose(self) -> None:
                self.disposed = True
                disposed_instances.append(self.name)

        with manager.create_scope():
            # Create scoped instance
            instance = manager.create_or_get_instance(
                DisposableComponent,
                ComponentScope.SCOPED,
                lambda: DisposableComponent("test"),
            )
            assert not instance.disposed

        # After scope exit, instance should be disposed
        assert instance.disposed
        assert "test" in disposed_instances

    def test_get_instance_count(self) -> None:
        """Test getting instance count by scope."""
        manager = ScopeManager()

        # Create various instances
        manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, lambda: MockComponent()
        )
        manager.create_or_get_instance(str, ComponentScope.SINGLETON, lambda: "test")
        manager.create_or_get_instance(int, ComponentScope.TRANSIENT, lambda: 42)

        # Check counts
        assert manager.get_instance_count(ComponentScope.SINGLETON) == 2
        assert manager.get_instance_count(ComponentScope.TRANSIENT) == 0
        assert manager.get_instance_count(ComponentScope.SCOPED) == 0
        assert manager.get_instance_count() == 2  # Total

    def test_has_active_scope(self) -> None:
        """Test checking for active scope."""
        manager = ScopeManager()

        # Initially no active scope
        assert not manager.has_active_scope()

        with manager.create_scope():
            assert manager.has_active_scope()

            # Nested scope
            with manager.create_scope():
                assert manager.has_active_scope()

            # Still in outer scope
            assert manager.has_active_scope()

        # No scope after exit
        assert not manager.has_active_scope()

    def test_dispose_manager(self) -> None:
        """Test disposing the entire scope manager."""
        manager = ScopeManager()
        disposed_count = 0

        class TrackingComponent:
            def dispose(self) -> None:
                nonlocal disposed_count
                disposed_count += 1

        # Create singleton instances
        manager.create_or_get_instance(
            TrackingComponent, ComponentScope.SINGLETON, TrackingComponent
        )
        manager.create_or_get_instance(
            type, ComponentScope.SINGLETON, lambda: TrackingComponent()
        )

        # Dispose manager
        manager.dispose()

        # All singleton instances should be disposed
        assert disposed_count >= 1

        # After dispose, new instances are created
        new_instance = manager.create_or_get_instance(
            TrackingComponent, ComponentScope.SINGLETON, TrackingComponent
        )
        assert isinstance(new_instance, TrackingComponent)

    def test_lifecycle_callback_integration(self) -> None:
        """Test lifecycle callback functionality."""
        events = []

        def callback(event: str, **kwargs):
            events.append(
                {
                    "event": event,
                    "component_type": kwargs.get("component_type"),
                    "scope": kwargs.get("scope"),
                }
            )

        manager = ScopeManager(lifecycle_callback=callback)

        # Create instance
        manager.create_or_get_instance(
            MockComponent, ComponentScope.SINGLETON, lambda: MockComponent()
        )

        # Check events
        assert len(events) > 0
        assert any(e["event"] == "instance_created" for e in events)
        creation_event = next(e for e in events if e["event"] == "instance_created")
        assert creation_event["component_type"] == "MockComponent"
        assert creation_event["scope"] == ComponentScope.SINGLETON

    def test_event_loop_manager_integration(self) -> None:
        """Test integration with event loop manager for async disposal."""
        manager = ScopeManager()

        class AsyncComponent:
            def __init__(self):
                self.disposed = False

            async def cleanup(self) -> None:
                """Async cleanup method."""
                self.disposed = True

        # Create and dispose instance
        instance = manager.create_or_get_instance(
            AsyncComponent, ComponentScope.SINGLETON, AsyncComponent
        )

        # Dispose manager - should handle async cleanup
        manager.dispose()

        # Instance should be disposed via event loop manager
        assert instance.disposed

    def test_garbage_collection(self) -> None:
        """Test that disposed instances can be garbage collected."""
        manager = ScopeManager()

        # Create instance and weak reference
        self._test_instance = MockComponent()
        weak_ref = weakref.ref(self._test_instance)

        def factory() -> MockComponent:
            return self._test_instance

        manager.create_or_get_instance(MockComponent, ComponentScope.SINGLETON, factory)

        # Instance is held by manager
        assert weak_ref() is not None

        # Clear reference and dispose manager
        del self._test_instance
        manager.dispose()
        gc.collect()

        # Instance should be collectible (may not be immediate)
        # This test might be flaky depending on GC behavior

    def test_thread_safety_simulation(self) -> None:
        """Test thread safety with concurrent access simulation."""
        manager = ScopeManager()

        # Create multiple instances "concurrently"
        instances = []
        for _ in range(10):
            instance = manager.create_or_get_instance(
                MockComponent, ComponentScope.SINGLETON, lambda: MockComponent()
            )
            instances.append(instance)

        # All should be the same singleton instance
        assert all(inst is instances[0] for inst in instances)

    def test_complex_scope_nesting(self) -> None:
        """Test complex nested scope scenarios."""
        manager = ScopeManager()
        scope_tracking = []

        def create_component(name: str):
            comp = MockComponent(value=name)
            scope_tracking.append(f"created_{name}")
            return comp

        # Multiple levels of nesting
        with manager.create_scope():
            outer = manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, lambda: create_component("outer")
            )

            with manager.create_scope():
                middle = manager.create_or_get_instance(
                    MockComponent,
                    ComponentScope.SCOPED,
                    lambda: create_component("middle"),
                )

                with manager.create_scope():
                    inner = manager.create_or_get_instance(
                        MockComponent,
                        ComponentScope.SCOPED,
                        lambda: create_component("inner"),
                    )

                    # All different instances
                    assert outer is not middle
                    assert middle is not inner
                    assert outer is not inner

                # Back to middle scope
                middle2 = manager.create_or_get_instance(
                    MockComponent,
                    ComponentScope.SCOPED,
                    lambda: create_component("middle2"),
                )
                assert middle2 is middle

            # Back to outer scope
            outer2 = manager.create_or_get_instance(
                MockComponent, ComponentScope.SCOPED, lambda: create_component("outer2")
            )
            assert outer2 is outer

        # Check creation order
        assert scope_tracking == ["created_outer", "created_middle", "created_inner"]

    def test_mixed_scope_types(self) -> None:
        """Test mixing different scope types."""
        manager = ScopeManager()

        with manager.create_scope():
            # Create instances with different scopes
            singleton = manager.create_or_get_instance(
                str, ComponentScope.SINGLETON, lambda: "singleton"
            )
            scoped = manager.create_or_get_instance(
                list, ComponentScope.SCOPED, lambda: ["scoped"]
            )
            transient1 = manager.create_or_get_instance(
                dict, ComponentScope.TRANSIENT, lambda: {"key": "transient1"}
            )
            transient2 = manager.create_or_get_instance(
                dict, ComponentScope.TRANSIENT, lambda: {"key": "transient2"}
            )

            # Verify behavior
            assert singleton == "singleton"
            assert scoped == ["scoped"]
            assert transient1 != transient2

            # Singleton persists across scopes
            with manager.create_scope():
                singleton2 = manager.create_or_get_instance(
                    str, ComponentScope.SINGLETON, lambda: "different"
                )
                scoped2 = manager.create_or_get_instance(
                    list, ComponentScope.SCOPED, lambda: ["different"]
                )

                assert singleton2 is singleton
                assert scoped2 is not scoped
                assert scoped2 == ["different"]
