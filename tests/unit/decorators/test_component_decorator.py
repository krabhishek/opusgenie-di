"""Tests for @og_component decorator."""

import pytest

from opusgenie_di import (
    BaseComponent,
    ComponentLayer,
    ComponentOptions,
    ComponentScope,
    get_component_metadata,
    get_component_options,
    is_og_component,
    og_component,
    register_component_manually,
)


class TestComponentDecorator:
    """Test @og_component decorator functionality."""

    def test_basic_component_decoration(self) -> None:
        """Test basic component decoration."""

        @og_component(scope=ComponentScope.SINGLETON)
        class TestService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.value = "test"

        # Verify component is marked as og_component
        assert is_og_component(TestService)

        # Verify component options are stored
        options = get_component_options(TestService)
        assert options is not None
        assert options.scope == ComponentScope.SINGLETON

    def test_component_decoration_with_all_options(self) -> None:
        """Test component decoration with all available options."""

        @og_component(
            scope=ComponentScope.TRANSIENT,
            auto_register=False,
            layer=ComponentLayer.APPLICATION,
            tags={"env": "test"},
            component_name="custom_service",
        )
        class FullyConfiguredService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.configured = True

        assert is_og_component(FullyConfiguredService)

        options = get_component_options(FullyConfiguredService)
        assert options.scope == ComponentScope.TRANSIENT
        assert options.auto_register is False
        assert options.layer == ComponentLayer.APPLICATION
        assert options.tags["env"] == "test"
        assert options.component_name == "custom_service"

    def test_component_decoration_defaults(self) -> None:
        """Test component decoration with default options."""

        @og_component()
        class DefaultService(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.is_default = True

        assert is_og_component(DefaultService)

        options = get_component_options(DefaultService)
        assert options.scope == ComponentScope.SINGLETON  # Default scope
        assert options.auto_register is True  # Default auto-register
        assert (
            options.layer == ComponentLayer.APPLICATION
        )  # Auto-detected from class name
        assert options.tags == {}  # Default tags
        assert options.component_name is None  # Default name

    def test_component_decoration_scope_variations(self) -> None:
        """Test component decoration with different scopes."""

        @og_component(scope=ComponentScope.SINGLETON)
        class SingletonService(BaseComponent):
            pass

        @og_component(scope=ComponentScope.TRANSIENT)
        class TransientService(BaseComponent):
            pass

        @og_component(scope=ComponentScope.SCOPED)
        class ScopedService(BaseComponent):
            pass

        assert get_component_options(SingletonService).scope == ComponentScope.SINGLETON
        assert get_component_options(TransientService).scope == ComponentScope.TRANSIENT
        assert get_component_options(ScopedService).scope == ComponentScope.SCOPED

    def test_component_decoration_layer_variations(self) -> None:
        """Test component decoration with different layers."""

        @og_component(layer=ComponentLayer.INFRASTRUCTURE)
        class InfrastructureService(BaseComponent):
            pass

        @og_component(layer=ComponentLayer.DOMAIN)
        class DomainService(BaseComponent):
            pass

        @og_component(layer=ComponentLayer.APPLICATION)
        class ApplicationService(BaseComponent):
            pass

        @og_component(layer=ComponentLayer.PRESENTATION)
        class PresentationService(BaseComponent):
            pass

        assert (
            get_component_options(InfrastructureService).layer
            == ComponentLayer.INFRASTRUCTURE
        )
        assert get_component_options(DomainService).layer == ComponentLayer.DOMAIN
        assert (
            get_component_options(ApplicationService).layer
            == ComponentLayer.APPLICATION
        )
        assert (
            get_component_options(PresentationService).layer
            == ComponentLayer.PRESENTATION
        )

    def test_component_decoration_auto_register_variations(self) -> None:
        """Test component decoration with auto_register variations."""

        @og_component(auto_register=True)
        class AutoRegisterService(BaseComponent):
            pass

        @og_component(auto_register=False)
        class ManualRegisterService(BaseComponent):
            pass

        assert get_component_options(AutoRegisterService).auto_register is True
        assert get_component_options(ManualRegisterService).auto_register is False

    def test_component_decoration_with_tags(self) -> None:
        """Test component decoration with various tag configurations."""

        @og_component(tags={"version": "1.0", "env": "test"})
        class TaggedService(BaseComponent):
            pass

        @og_component(tags={"complex": "nested_value"})
        class ComplexTaggedService(BaseComponent):
            pass

        simple_options = get_component_options(TaggedService)
        assert simple_options.tags["version"] == "1.0"
        assert simple_options.tags["env"] == "test"

        complex_options = get_component_options(ComplexTaggedService)
        assert complex_options.tags["complex"] == "nested_value"

    def test_component_decoration_with_custom_name(self) -> None:
        """Test component decoration with custom component names."""

        @og_component(component_name="database_service")
        class DatabaseService(BaseComponent):
            pass

        @og_component(component_name="user_repository")
        class UserRepository(BaseComponent):
            pass

        assert (
            get_component_options(DatabaseService).component_name == "database_service"
        )
        assert get_component_options(UserRepository).component_name == "user_repository"

    def test_component_inheritance_preservation(self) -> None:
        """Test that component decoration preserves inheritance."""

        @og_component(scope=ComponentScope.SINGLETON)
        class BaseService(BaseComponent):
            def base_method(self) -> str:
                return "base"

        @og_component(scope=ComponentScope.TRANSIENT)
        class DerivedService(BaseService):
            def derived_method(self) -> str:
                return "derived"

        # Both should be og_components
        assert is_og_component(BaseService)
        assert is_og_component(DerivedService)

        # Both should preserve their own options
        assert get_component_options(BaseService).scope == ComponentScope.SINGLETON
        assert get_component_options(DerivedService).scope == ComponentScope.TRANSIENT

        # Inheritance should work
        derived = DerivedService()
        assert derived.base_method() == "base"
        assert derived.derived_method() == "derived"
        assert isinstance(derived, BaseService)

    def test_component_metadata_creation(self) -> None:
        """Test that component decoration creates proper metadata."""

        @og_component(
            scope=ComponentScope.SINGLETON,
            layer=ComponentLayer.DOMAIN,
            tags={"service": "core"},
        )
        class MetadataService(BaseComponent):
            pass

        metadata = get_component_metadata(MetadataService)
        assert metadata is not None
        assert metadata["component_type"] == "MetadataService"
        assert metadata["scope"] == "singleton"
        assert metadata["layer"] == "domain"
        # Tags are stored in enhanced_tags, not in metadata
        enhanced_tags = MetadataService._og_enhanced_tags
        assert enhanced_tags["service"] == "core"

    def test_non_component_class_detection(self) -> None:
        """Test detection of non-og_component classes."""

        class RegularClass:
            pass

        class NonDecoratedComponent(BaseComponent):
            pass

        assert not is_og_component(RegularClass)
        assert not is_og_component(NonDecoratedComponent)

        # Getting options from non-components should return None or raise
        assert get_component_options(RegularClass) is None
        assert get_component_options(NonDecoratedComponent) is None

    def test_component_decoration_method_preservation(self) -> None:
        """Test that component decoration preserves all class methods."""

        @og_component(scope=ComponentScope.SINGLETON)
        class MethodPreservationService(BaseComponent):
            def __init__(self, value: str = "default") -> None:
                super().__init__()
                self.value = value

            def public_method(self) -> str:
                return f"public_{self.value}"

            def _protected_method(self) -> str:
                return f"protected_{self.value}"

            def __private_method(self) -> str:
                return f"private_{self.value}"

            @property
            def value_property(self) -> str:
                return self.value

            @staticmethod
            def static_method() -> str:
                return "static"

            @classmethod
            def class_method(cls) -> str:
                return cls.__name__

        service = MethodPreservationService("test")

        # All methods should be preserved
        assert service.public_method() == "public_test"
        assert service._protected_method() == "protected_test"
        assert service._MethodPreservationService__private_method() == "private_test"
        assert service.value_property == "test"
        assert MethodPreservationService.static_method() == "static"
        assert MethodPreservationService.class_method() == "MethodPreservationService"

    def test_component_decoration_multiple_inheritance(self) -> None:
        """Test component decoration with multiple inheritance."""

        class MixinA:
            def method_a(self) -> str:
                return "a"

        class MixinB:
            def method_b(self) -> str:
                return "b"

        @og_component(scope=ComponentScope.SINGLETON)
        class MultiInheritanceService(BaseComponent, MixinA, MixinB):
            def service_method(self) -> str:
                return f"{self.method_a()}_{self.method_b()}_service"

        assert is_og_component(MultiInheritanceService)

        service = MultiInheritanceService()
        assert service.method_a() == "a"
        assert service.method_b() == "b"
        assert service.service_method() == "a_b_service"

    def test_manual_component_registration(self) -> None:
        """Test manual component registration functionality."""

        @og_component(auto_register=False)
        class ManualComponent(BaseComponent):
            def __init__(self) -> None:
                super().__init__()
                self.manually_registered = True

        # Component should be decorated but not auto-registered
        assert is_og_component(ManualComponent)

        # Manual registration with override options
        register_component_manually(
            ManualComponent,
            scope=ComponentScope.TRANSIENT,
            tags={"registration": "manual"},
        )

        options = get_component_options(ManualComponent)
        assert options.scope == ComponentScope.TRANSIENT
        assert options.tags["registration"] == "manual"

    def test_component_options_class(self) -> None:
        """Test ComponentOptions class functionality."""

        options = ComponentOptions(
            scope=ComponentScope.SCOPED,
            auto_register=False,
            layer=ComponentLayer.INFRASTRUCTURE,
            tags={"test": "value"},
            component_name="test_component",
        )

        assert options.scope == ComponentScope.SCOPED
        assert options.auto_register is False
        assert options.layer == ComponentLayer.INFRASTRUCTURE
        assert options.tags["test"] == "value"
        assert options.component_name == "test_component"

    def test_decorator_with_invalid_arguments(self) -> None:
        """Test decorator behavior with invalid arguments."""

        # These should raise appropriate errors
        with pytest.raises((TypeError, ValueError)):

            @og_component(scope="invalid_scope")  # type: ignore
            class InvalidScopeService(BaseComponent):
                pass

        with pytest.raises((TypeError, ValueError)):

            @og_component(layer="invalid_layer")  # type: ignore
            class InvalidLayerService(BaseComponent):
                pass
