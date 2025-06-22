"""Tests for provider configuration."""

from unittest.mock import patch

import pytest

from opusgenie_di import BaseComponent, ComponentScope
from opusgenie_di._modules.provider_config import (
    ProviderCollection,
    ProviderConfig,
    normalize_provider_list,
    normalize_provider_specification,
)
from opusgenie_di._testing import MockComponent


class TestComponent(BaseComponent):
    """Test component for provider config tests."""


class TestProviderConfig:
    """Test ProviderConfig class."""

    def test_provider_config_basic(self) -> None:
        """Test basic provider config creation."""
        config = ProviderConfig(interface=MockComponent)

        assert config.interface == MockComponent
        assert config.implementation is None
        assert config.scope == ComponentScope.SINGLETON
        assert config.name is None
        assert config.factory is None
        assert config.tags == {}
        assert config.conditional is None

    def test_provider_config_with_implementation(self) -> None:
        """Test provider config with explicit implementation."""
        config = ProviderConfig(
            interface=BaseComponent,
            implementation=MockComponent,
            scope=ComponentScope.TRANSIENT,
            name="test_provider",
        )

        assert config.interface == BaseComponent
        assert config.implementation == MockComponent
        assert config.scope == ComponentScope.TRANSIENT
        assert config.name == "test_provider"

    def test_provider_config_with_factory(self) -> None:
        """Test provider config with factory function."""

        def factory() -> MockComponent:
            return MockComponent()

        config = ProviderConfig(interface=MockComponent, factory=factory)

        assert config.interface == MockComponent
        assert config.factory == factory

    def test_provider_config_with_tags(self) -> None:
        """Test provider config with tags."""
        tags = {"environment": "test", "version": "1.0"}
        config = ProviderConfig(interface=MockComponent, tags=tags)

        assert config.tags == tags

    def test_provider_config_with_conditional(self) -> None:
        """Test provider config with conditional."""
        config = ProviderConfig(interface=MockComponent, conditional=True)

        assert config.conditional is True

    def test_get_implementation_default(self) -> None:
        """Test get_implementation returns interface when no implementation specified."""
        config = ProviderConfig(interface=MockComponent)

        assert config.get_implementation() == MockComponent

    def test_get_implementation_explicit(self) -> None:
        """Test get_implementation returns explicit implementation."""
        config = ProviderConfig(interface=BaseComponent, implementation=MockComponent)

        assert config.get_implementation() == MockComponent

    def test_get_provider_name_default(self) -> None:
        """Test get_provider_name returns interface name when no name specified."""
        config = ProviderConfig(interface=MockComponent)

        assert config.get_provider_name() == "MockComponent"

    def test_get_provider_name_explicit(self) -> None:
        """Test get_provider_name returns explicit name."""
        config = ProviderConfig(interface=MockComponent, name="test_provider")

        assert config.get_provider_name() == "test_provider"

    def test_to_registration_args(self) -> None:
        """Test converting to registration arguments."""
        config = ProviderConfig(
            interface=MockComponent,
            scope=ComponentScope.TRANSIENT,
            name="test_provider",
            tags={"env": "test"},
        )

        args = config.to_registration_args()

        expected = {
            "interface": MockComponent,
            "implementation": MockComponent,
            "scope": ComponentScope.TRANSIENT,
            "name": "test_provider",
            "tags": {"env": "test"},
            "factory": None,
        }

        assert args == expected

    def test_is_conditional_false(self) -> None:
        """Test is_conditional returns False when no condition."""
        config = ProviderConfig(interface=MockComponent)

        assert config.is_conditional() is False

    def test_is_conditional_true(self) -> None:
        """Test is_conditional returns True when condition present."""
        config = ProviderConfig(interface=MockComponent, conditional=True)

        assert config.is_conditional() is True

    def test_evaluate_condition_no_condition(self) -> None:
        """Test evaluate_condition returns True when no condition."""
        config = ProviderConfig(interface=MockComponent)

        assert config.evaluate_condition() is True

    def test_evaluate_condition_boolean_true(self) -> None:
        """Test evaluate_condition with boolean True."""
        config = ProviderConfig(interface=MockComponent, conditional=True)

        assert config.evaluate_condition() is True

    def test_evaluate_condition_boolean_false(self) -> None:
        """Test evaluate_condition with boolean False."""
        config = ProviderConfig(interface=MockComponent, conditional=False)

        assert config.evaluate_condition() is False

    def test_evaluate_condition_callable_true(self) -> None:
        """Test evaluate_condition with callable returning True."""
        config = ProviderConfig(interface=MockComponent, conditional=lambda: True)

        assert config.evaluate_condition() is True

    def test_evaluate_condition_callable_false(self) -> None:
        """Test evaluate_condition with callable returning False."""
        config = ProviderConfig(interface=MockComponent, conditional=lambda: False)

        assert config.evaluate_condition() is False

    def test_evaluate_condition_exception(self) -> None:
        """Test evaluate_condition with callable that raises exception."""

        def failing_condition() -> bool:
            raise ValueError("Condition failed")

        config = ProviderConfig(interface=MockComponent, conditional=failing_condition)

        assert config.evaluate_condition() is False

    def test_repr(self) -> None:
        """Test string representation."""
        config = ProviderConfig(
            interface=BaseComponent,
            implementation=MockComponent,
            scope=ComponentScope.TRANSIENT,
        )

        repr_str = repr(config)

        assert "ProviderConfig" in repr_str
        assert "BaseComponent" in repr_str
        assert "MockComponent" in repr_str
        assert "transient" in repr_str

    def test_model_post_init_validation(self) -> None:
        """Test validation during initialization."""
        with patch(
            "opusgenie_di._modules.provider_config.validate_component_registration"
        ) as mock_validate:
            ProviderConfig(interface=MockComponent)

            mock_validate.assert_called_once_with(
                MockComponent, MockComponent, "MockComponent"
            )


class TestProviderCollection:
    """Test ProviderCollection class."""

    def test_provider_collection_empty(self) -> None:
        """Test empty provider collection."""
        collection = ProviderCollection()

        assert len(collection) == 0
        assert collection.get_provider_count() == 0
        assert collection.get_active_provider_count() == 0
        assert collection.get_interfaces() == []
        assert collection.get_implementations() == []

    def test_add_provider(self) -> None:
        """Test adding provider to collection."""
        collection = ProviderCollection()
        config = ProviderConfig(interface=MockComponent)

        collection.add_provider(config)

        assert len(collection) == 1
        assert config in collection.providers

    def test_add_provider_duplicate(self) -> None:
        """Test adding duplicate provider (by name)."""
        collection = ProviderCollection()
        config1 = ProviderConfig(interface=MockComponent, name="test")
        config2 = ProviderConfig(interface=TestComponent, name="test")

        collection.add_provider(config1)
        collection.add_provider(config2)  # Should be ignored

        assert len(collection) == 1
        assert collection.providers[0] == config1

    def test_get_provider_by_name_found(self) -> None:
        """Test getting provider by name when found."""
        collection = ProviderCollection()
        config = ProviderConfig(interface=MockComponent, name="test_provider")
        collection.add_provider(config)

        result = collection.get_provider_by_name("test_provider")

        assert result == config

    def test_get_provider_by_name_not_found(self) -> None:
        """Test getting provider by name when not found."""
        collection = ProviderCollection()

        result = collection.get_provider_by_name("nonexistent")

        assert result is None

    def test_get_provider_by_interface_found(self) -> None:
        """Test getting provider by interface when found."""
        collection = ProviderCollection()
        config = ProviderConfig(interface=MockComponent)
        collection.add_provider(config)

        result = collection.get_provider_by_interface(MockComponent)

        assert result == config

    def test_get_provider_by_interface_not_found(self) -> None:
        """Test getting provider by interface when not found."""
        collection = ProviderCollection()

        result = collection.get_provider_by_interface(MockComponent)

        assert result is None

    def test_get_providers_by_scope(self) -> None:
        """Test getting providers by scope."""
        collection = ProviderCollection()

        singleton_config = ProviderConfig(
            interface=MockComponent, scope=ComponentScope.SINGLETON
        )
        transient_config = ProviderConfig(
            interface=TestComponent, scope=ComponentScope.TRANSIENT
        )

        collection.add_provider(singleton_config)
        collection.add_provider(transient_config)

        singletons = collection.get_providers_by_scope(ComponentScope.SINGLETON)
        transients = collection.get_providers_by_scope(ComponentScope.TRANSIENT)

        assert len(singletons) == 1
        assert singleton_config in singletons
        assert len(transients) == 1
        assert transient_config in transients

    def test_get_conditional_providers(self) -> None:
        """Test getting conditional providers."""
        collection = ProviderCollection()

        regular_config = ProviderConfig(interface=MockComponent)
        conditional_config = ProviderConfig(interface=TestComponent, conditional=True)

        collection.add_provider(regular_config)
        collection.add_provider(conditional_config)

        conditionals = collection.get_conditional_providers()

        assert len(conditionals) == 1
        assert conditional_config in conditionals

    def test_get_active_providers_all_active(self) -> None:
        """Test getting active providers when all are active."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=MockComponent)
        config2 = ProviderConfig(interface=TestComponent, conditional=True)

        collection.add_provider(config1)
        collection.add_provider(config2)

        active = collection.get_active_providers()

        assert len(active) == 2
        assert config1 in active
        assert config2 in active

    def test_get_active_providers_some_inactive(self) -> None:
        """Test getting active providers when some are inactive."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=MockComponent)
        config2 = ProviderConfig(interface=TestComponent, conditional=False)

        collection.add_provider(config1)
        collection.add_provider(config2)

        active = collection.get_active_providers()

        assert len(active) == 1
        assert config1 in active
        assert config2 not in active

    def test_get_interfaces(self) -> None:
        """Test getting all interface types."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=MockComponent)
        config2 = ProviderConfig(interface=TestComponent)

        collection.add_provider(config1)
        collection.add_provider(config2)

        interfaces = collection.get_interfaces()

        assert len(interfaces) == 2
        assert MockComponent in interfaces
        assert TestComponent in interfaces

    def test_get_implementations(self) -> None:
        """Test getting all implementation types."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=BaseComponent, implementation=MockComponent)
        config2 = ProviderConfig(interface=TestComponent)

        collection.add_provider(config1)
        collection.add_provider(config2)

        implementations = collection.get_implementations()

        assert len(implementations) == 2
        assert MockComponent in implementations
        assert TestComponent in implementations

    def test_validate_providers_no_errors(self) -> None:
        """Test validating providers with no errors."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=MockComponent)
        config2 = ProviderConfig(interface=TestComponent)

        collection.add_provider(config1)
        collection.add_provider(config2)

        errors = collection.validate_providers()

        assert errors == []

    def test_validate_providers_duplicate_interface(self) -> None:
        """Test validating providers with duplicate interface."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=MockComponent, name="provider1")
        config2 = ProviderConfig(interface=MockComponent, name="provider2")

        collection.add_provider(config1)
        collection.add_provider(config2)

        errors = collection.validate_providers()

        assert len(errors) == 1
        assert "MockComponent provided by multiple providers" in errors[0]

    def test_to_registration_dict(self) -> None:
        """Test converting to registration dictionary."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=MockComponent)
        config2 = ProviderConfig(interface=TestComponent, conditional=False)  # Inactive

        collection.add_provider(config1)
        collection.add_provider(config2)

        reg_dict = collection.to_registration_dict()

        # Only active providers should be included
        assert len(reg_dict) == 1
        assert MockComponent in reg_dict
        assert TestComponent not in reg_dict

    def test_clear(self) -> None:
        """Test clearing all providers."""
        collection = ProviderCollection()
        config = ProviderConfig(interface=MockComponent)
        collection.add_provider(config)

        assert len(collection) == 1

        collection.clear()

        assert len(collection) == 0

    def test_iter(self) -> None:
        """Test iterating over providers."""
        collection = ProviderCollection()

        config1 = ProviderConfig(interface=MockComponent)
        config2 = ProviderConfig(interface=TestComponent)

        collection.add_provider(config1)
        collection.add_provider(config2)

        providers = list(collection)

        assert len(providers) == 2
        assert config1 in providers
        assert config2 in providers

    def test_contains_provider_config(self) -> None:
        """Test contains with ProviderConfig."""
        collection = ProviderCollection()
        config = ProviderConfig(interface=MockComponent)
        collection.add_provider(config)

        assert config in collection

        other_config = ProviderConfig(interface=TestComponent)
        assert other_config not in collection

    def test_contains_string(self) -> None:
        """Test contains with string (provider name)."""
        collection = ProviderCollection()
        config = ProviderConfig(interface=MockComponent, name="test_provider")
        collection.add_provider(config)

        assert "test_provider" in collection
        assert "nonexistent" not in collection

    def test_contains_type(self) -> None:
        """Test contains with type (interface)."""
        collection = ProviderCollection()
        config = ProviderConfig(interface=MockComponent)
        collection.add_provider(config)

        assert MockComponent in collection
        assert TestComponent not in collection

    def test_contains_invalid_type(self) -> None:
        """Test contains with invalid type."""
        collection = ProviderCollection()

        assert 42 not in collection
        assert None not in collection


class TestNormalizationFunctions:
    """Test provider specification normalization functions."""

    def test_normalize_provider_config(self) -> None:
        """Test normalizing existing ProviderConfig."""
        config = ProviderConfig(interface=MockComponent)

        result = normalize_provider_specification(config)

        assert result is config

    def test_normalize_dict_simple(self) -> None:
        """Test normalizing simple dictionary {interface: implementation}."""
        spec = {BaseComponent: MockComponent}

        result = normalize_provider_specification(spec)

        assert isinstance(result, ProviderConfig)
        assert result.interface == BaseComponent
        assert result.implementation == MockComponent

    def test_normalize_dict_expanded(self) -> None:
        """Test normalizing expanded dictionary format."""
        spec = {
            "interface": MockComponent,
            "scope": ComponentScope.TRANSIENT,
            "name": "test_provider",
        }

        result = normalize_provider_specification(spec)

        assert isinstance(result, ProviderConfig)
        assert result.interface == MockComponent
        assert result.scope == ComponentScope.TRANSIENT
        assert result.name == "test_provider"

    def test_normalize_type(self) -> None:
        """Test normalizing type (self-registration)."""
        result = normalize_provider_specification(MockComponent)

        assert isinstance(result, ProviderConfig)
        assert result.interface == MockComponent
        assert result.implementation == MockComponent

    def test_normalize_invalid_spec(self) -> None:
        """Test normalizing invalid specification."""
        with pytest.raises(ValueError, match="Invalid provider specification"):
            normalize_provider_specification("invalid")

    def test_normalize_provider_list(self) -> None:
        """Test normalizing list of provider specifications."""
        specs = [
            MockComponent,
            {BaseComponent: TestComponent},
            ProviderConfig(interface=TestComponent, name="test"),
        ]

        result = normalize_provider_list(specs)

        assert len(result) == 3
        assert all(isinstance(config, ProviderConfig) for config in result)
        assert result[0].interface == MockComponent
        assert result[1].interface == BaseComponent
        assert result[1].implementation == TestComponent
        assert result[2].name == "test"
