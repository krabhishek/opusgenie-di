"""Tests for base enums."""

import pytest

from opusgenie_di import (
    ComponentLayer,
    ComponentScope,
    LifecycleStage,
    RegistrationStrategy,
)


class TestComponentScope:
    """Test ComponentScope enum."""

    def test_component_scope_values(self) -> None:
        """Test ComponentScope enum values."""
        assert ComponentScope.SINGLETON.value == "singleton"
        assert ComponentScope.TRANSIENT.value == "transient"
        assert ComponentScope.SCOPED.value == "scoped"

    def test_component_scope_membership(self) -> None:
        """Test ComponentScope membership."""
        assert ComponentScope.SINGLETON in ComponentScope
        assert ComponentScope.TRANSIENT in ComponentScope
        assert ComponentScope.SCOPED in ComponentScope
        assert "invalid" not in ComponentScope

    def test_component_scope_comparison(self) -> None:
        """Test ComponentScope comparison."""
        assert ComponentScope.SINGLETON == ComponentScope.SINGLETON
        assert ComponentScope.SINGLETON != ComponentScope.TRANSIENT
        assert ComponentScope.TRANSIENT != ComponentScope.SCOPED

    def test_component_scope_string_representation(self) -> None:
        """Test ComponentScope string representation."""
        assert ComponentScope.SINGLETON.value == "singleton"
        assert ComponentScope.TRANSIENT.value == "transient"
        assert ComponentScope.SCOPED.value == "scoped"

    def test_component_scope_iteration(self) -> None:
        """Test ComponentScope iteration."""
        scopes = list(ComponentScope)
        assert len(scopes) == 5  # Updated to actual count
        assert ComponentScope.SINGLETON in scopes
        assert ComponentScope.TRANSIENT in scopes
        assert ComponentScope.SCOPED in scopes
        assert ComponentScope.FACTORY in scopes
        assert ComponentScope.CONDITIONAL in scopes

    def test_component_scope_from_string(self) -> None:
        """Test creating ComponentScope from string."""
        assert ComponentScope("singleton") == ComponentScope.SINGLETON
        assert ComponentScope("transient") == ComponentScope.TRANSIENT
        assert ComponentScope("scoped") == ComponentScope.SCOPED

        with pytest.raises(ValueError):
            ComponentScope("invalid_scope")


class TestComponentLayer:
    """Test ComponentLayer enum."""

    def test_component_layer_values(self) -> None:
        """Test ComponentLayer enum values."""
        assert ComponentLayer.INFRASTRUCTURE.value == "infrastructure"
        assert ComponentLayer.DOMAIN.value == "domain"
        assert ComponentLayer.APPLICATION.value == "application"
        assert ComponentLayer.PRESENTATION.value == "presentation"
        assert ComponentLayer.FRAMEWORK.value == "framework"

    def test_component_layer_membership(self) -> None:
        """Test ComponentLayer membership."""
        assert ComponentLayer.INFRASTRUCTURE in ComponentLayer
        assert ComponentLayer.DOMAIN in ComponentLayer
        assert ComponentLayer.APPLICATION in ComponentLayer
        assert ComponentLayer.PRESENTATION in ComponentLayer
        assert "invalid" not in ComponentLayer

    def test_component_layer_comparison(self) -> None:
        """Test ComponentLayer comparison."""
        assert ComponentLayer.INFRASTRUCTURE == ComponentLayer.INFRASTRUCTURE
        assert ComponentLayer.INFRASTRUCTURE != ComponentLayer.DOMAIN
        assert ComponentLayer.DOMAIN != ComponentLayer.APPLICATION

    def test_component_layer_string_representation(self) -> None:
        """Test ComponentLayer string representation."""
        assert ComponentLayer.INFRASTRUCTURE.value == "infrastructure"
        assert ComponentLayer.DOMAIN.value == "domain"
        assert ComponentLayer.APPLICATION.value == "application"
        assert ComponentLayer.PRESENTATION.value == "presentation"

    def test_component_layer_iteration(self) -> None:
        """Test ComponentLayer iteration."""
        layers = list(ComponentLayer)
        assert len(layers) == 5  # Updated to actual count
        assert ComponentLayer.INFRASTRUCTURE in layers
        assert ComponentLayer.DOMAIN in layers
        assert ComponentLayer.APPLICATION in layers
        assert ComponentLayer.PRESENTATION in layers
        assert ComponentLayer.FRAMEWORK in layers

    def test_component_layer_from_string(self) -> None:
        """Test creating ComponentLayer from string."""
        assert ComponentLayer("infrastructure") == ComponentLayer.INFRASTRUCTURE
        assert ComponentLayer("domain") == ComponentLayer.DOMAIN
        assert ComponentLayer("application") == ComponentLayer.APPLICATION
        assert ComponentLayer("presentation") == ComponentLayer.PRESENTATION

        with pytest.raises(ValueError):
            ComponentLayer("invalid_layer")


class TestLifecycleStage:
    """Test LifecycleStage enum."""

    def test_lifecycle_stage_values(self) -> None:
        """Test LifecycleStage enum values."""
        assert LifecycleStage.CREATED.value == "created"
        assert LifecycleStage.INITIALIZING.value == "initializing"
        assert LifecycleStage.ACTIVE.value == "active"
        assert LifecycleStage.STOPPING.value == "stopping"
        assert LifecycleStage.STOPPED.value == "stopped"

    def test_lifecycle_stage_membership(self) -> None:
        """Test LifecycleStage membership."""
        assert LifecycleStage.CREATED in LifecycleStage
        assert LifecycleStage.INITIALIZING in LifecycleStage
        assert LifecycleStage.INITIALIZED in LifecycleStage
        assert LifecycleStage.DISPOSING in LifecycleStage
        assert LifecycleStage.DISPOSED in LifecycleStage
        assert "invalid" not in LifecycleStage

    def test_lifecycle_stage_comparison(self) -> None:
        """Test LifecycleStage comparison."""
        assert LifecycleStage.CREATED == LifecycleStage.CREATED
        assert LifecycleStage.CREATED != LifecycleStage.INITIALIZING
        assert LifecycleStage.INITIALIZING != LifecycleStage.INITIALIZED

    def test_lifecycle_stage_string_representation(self) -> None:
        """Test LifecycleStage string representation."""
        assert LifecycleStage.CREATED.value == "created"
        assert LifecycleStage.INITIALIZING.value == "initializing"
        assert LifecycleStage.INITIALIZED.value == "initialized"
        assert LifecycleStage.DISPOSING.value == "disposing"
        assert LifecycleStage.DISPOSED.value == "disposed"

    def test_lifecycle_stage_iteration(self) -> None:
        """Test LifecycleStage iteration."""
        stages = list(LifecycleStage)
        assert len(stages) == 15  # Updated to actual count
        assert LifecycleStage.CREATED in stages
        assert LifecycleStage.INITIALIZING in stages
        assert LifecycleStage.ACTIVE in stages
        assert LifecycleStage.STOPPING in stages
        assert LifecycleStage.STOPPED in stages

    def test_lifecycle_stage_from_string(self) -> None:
        """Test creating LifecycleStage from string."""
        assert LifecycleStage("created") == LifecycleStage.CREATED
        assert LifecycleStage("initializing") == LifecycleStage.INITIALIZING
        assert LifecycleStage("initialized") == LifecycleStage.INITIALIZED
        assert LifecycleStage("disposing") == LifecycleStage.DISPOSING
        assert LifecycleStage("disposed") == LifecycleStage.DISPOSED

        with pytest.raises(ValueError):
            LifecycleStage("invalid_stage")


class TestRegistrationStrategy:
    """Test RegistrationStrategy enum."""

    def test_registration_strategy_values(self) -> None:
        """Test RegistrationStrategy enum values."""
        assert RegistrationStrategy.AUTO.value == "auto"
        assert RegistrationStrategy.MANUAL.value == "manual"
        assert RegistrationStrategy.LAZY.value == "lazy"

    def test_registration_strategy_membership(self) -> None:
        """Test RegistrationStrategy membership."""
        assert RegistrationStrategy.AUTO in RegistrationStrategy
        assert RegistrationStrategy.MANUAL in RegistrationStrategy
        assert RegistrationStrategy.LAZY in RegistrationStrategy
        assert "invalid" not in RegistrationStrategy

    def test_registration_strategy_comparison(self) -> None:
        """Test RegistrationStrategy comparison."""
        assert RegistrationStrategy.AUTO == RegistrationStrategy.AUTO
        assert RegistrationStrategy.AUTO != RegistrationStrategy.MANUAL
        assert RegistrationStrategy.MANUAL != RegistrationStrategy.LAZY

    def test_registration_strategy_string_representation(self) -> None:
        """Test RegistrationStrategy string representation."""
        assert RegistrationStrategy.AUTO.value == "auto"
        assert RegistrationStrategy.MANUAL.value == "manual"
        assert RegistrationStrategy.LAZY.value == "lazy"

    def test_registration_strategy_iteration(self) -> None:
        """Test RegistrationStrategy iteration."""
        strategies = list(RegistrationStrategy)
        assert len(strategies) == 3
        assert RegistrationStrategy.AUTO in strategies
        assert RegistrationStrategy.MANUAL in strategies
        assert RegistrationStrategy.LAZY in strategies

    def test_registration_strategy_from_string(self) -> None:
        """Test creating RegistrationStrategy from string."""
        assert RegistrationStrategy("auto") == RegistrationStrategy.AUTO
        assert RegistrationStrategy("manual") == RegistrationStrategy.MANUAL
        assert RegistrationStrategy("lazy") == RegistrationStrategy.LAZY

        with pytest.raises(ValueError):
            RegistrationStrategy("invalid_strategy")


class TestEnumInteractions:
    """Test interactions between different enums."""

    def test_enum_combinations(self) -> None:
        """Test various enum combinations that might be used together."""
        # Test common combinations
        combinations = [
            (ComponentScope.SINGLETON, ComponentLayer.INFRASTRUCTURE),
            (ComponentScope.TRANSIENT, ComponentLayer.PRESENTATION),
            (ComponentScope.SCOPED, ComponentLayer.APPLICATION),
        ]

        for scope, layer in combinations:
            assert scope in ComponentScope
            assert layer in ComponentLayer
            # Verify they can be used together without conflict
            config = {"scope": scope, "layer": layer}
            assert config["scope"] == scope
            assert config["layer"] == layer

    def test_lifecycle_with_scope(self) -> None:
        """Test lifecycle stages with different scopes."""
        lifecycle_scope_combinations = [
            (LifecycleStage.CREATED, ComponentScope.SINGLETON),
            (LifecycleStage.INITIALIZED, ComponentScope.TRANSIENT),
            (LifecycleStage.DISPOSED, ComponentScope.SCOPED),
        ]

        for stage, scope in lifecycle_scope_combinations:
            assert stage in LifecycleStage
            assert scope in ComponentScope
            # Verify they can be used in component metadata
            metadata = {"lifecycle_stage": stage, "scope": scope}
            assert metadata["lifecycle_stage"] == stage
            assert metadata["scope"] == scope

    def test_registration_strategy_with_scope(self) -> None:
        """Test registration strategies with different scopes."""
        strategy_scope_combinations = [
            (RegistrationStrategy.AUTO, ComponentScope.SINGLETON),
            (RegistrationStrategy.MANUAL, ComponentScope.TRANSIENT),
            (RegistrationStrategy.LAZY, ComponentScope.SCOPED),
        ]

        for strategy, scope in strategy_scope_combinations:
            assert strategy in RegistrationStrategy
            assert scope in ComponentScope
            # Verify they work together in configuration
            config = {"strategy": strategy, "scope": scope}
            assert config["strategy"] == strategy
            assert config["scope"] == scope

    def test_enum_serialization(self) -> None:
        """Test enum serialization to string values."""
        enum_values = {
            "scope": ComponentScope.SINGLETON.value,
            "layer": ComponentLayer.DOMAIN.value,
            "stage": LifecycleStage.INITIALIZED.value,
            "strategy": RegistrationStrategy.AUTO.value,
        }

        assert enum_values["scope"] == "singleton"
        assert enum_values["layer"] == "domain"
        assert enum_values["stage"] == "initialized"
        assert enum_values["strategy"] == "auto"

    def test_enum_deserialization(self) -> None:
        """Test enum deserialization from string values."""
        string_values = {
            "scope": "transient",
            "layer": "application",
            "stage": "disposing",
            "strategy": "manual",
        }

        assert ComponentScope(string_values["scope"]) == ComponentScope.TRANSIENT
        assert ComponentLayer(string_values["layer"]) == ComponentLayer.APPLICATION
        assert LifecycleStage(string_values["stage"]) == LifecycleStage.DISPOSING
        assert (
            RegistrationStrategy(string_values["strategy"])
            == RegistrationStrategy.MANUAL
        )
