"""Tests for ComponentMetadata."""

from datetime import UTC, datetime

import pytest

from opusgenie_di import (
    ComponentLayer,
    ComponentMetadata,
    ComponentScope,
    LifecycleStage,
)


class TestComponentMetadata:
    """Test ComponentMetadata functionality."""

    def test_component_metadata_creation(self) -> None:
        """Test basic ComponentMetadata creation."""
        metadata = ComponentMetadata(
            component_type="TestComponent", context_name="test_context"
        )

        assert metadata.component_type == "TestComponent"
        assert metadata.scope == ComponentScope.SINGLETON  # default
        assert metadata.component_name is None
        assert metadata.layer is None
        assert metadata.context_name == "test_context"

    def test_component_metadata_with_all_fields(self) -> None:
        """Test ComponentMetadata with all fields."""
        metadata = ComponentMetadata(
            component_type="TestComponent",
            component_name="test_component",
            scope=ComponentScope.TRANSIENT,
            layer=ComponentLayer.APPLICATION,
            lifecycle_stage=LifecycleStage.ACTIVE,
            tags={"key": "value"},
            context_name="test_context",
            provider_name="test_provider",
            dependencies=["dep1", "dep2"],
            optional_dependencies=["opt1"],
            config={"setting": "value"},
        )

        assert metadata.component_type == "TestComponent"
        assert metadata.component_name == "test_component"
        assert metadata.scope == ComponentScope.TRANSIENT
        assert metadata.layer == ComponentLayer.APPLICATION
        assert metadata.lifecycle_stage == LifecycleStage.ACTIVE
        assert metadata.tags == {"key": "value"}
        assert metadata.context_name == "test_context"
        assert metadata.provider_name == "test_provider"
        assert metadata.dependencies == ["dep1", "dep2"]
        assert metadata.optional_dependencies == ["opt1"]
        assert metadata.config == {"setting": "value"}

    def test_component_metadata_defaults(self) -> None:
        """Test ComponentMetadata default values."""
        metadata = ComponentMetadata(
            component_type="TestComponent", context_name="test_context"
        )

        assert metadata.scope == ComponentScope.SINGLETON
        assert metadata.component_name is None
        assert metadata.layer is None
        assert metadata.lifecycle_stage == LifecycleStage.CREATED
        assert metadata.tags == {}
        assert metadata.dependencies == []
        assert metadata.optional_dependencies == []
        assert metadata.config == {}
        assert metadata.provider_name is None
        assert metadata.created_at is not None
        assert metadata.updated_at is None
        assert isinstance(metadata.created_at, datetime)

    def test_component_metadata_tags_handling(self) -> None:
        """Test ComponentMetadata tags handling."""
        metadata = ComponentMetadata(
            component_type="TestComponent",
            context_name="test_context",
            tags={"env": "test", "version": "1.0"},
        )

        assert metadata.tags["env"] == "test"
        assert metadata.tags["version"] == "1.0"
        assert len(metadata.tags) == 2

    def test_component_metadata_unique_ids(self) -> None:
        """Test that ComponentMetadata generates unique IDs."""
        metadata1 = ComponentMetadata(
            component_type="TestComponent", context_name="test_context"
        )
        metadata2 = ComponentMetadata(
            component_type="TestComponent", context_name="test_context"
        )

        assert metadata1.component_id != metadata2.component_id
        assert len(metadata1.component_id) > 0
        assert len(metadata2.component_id) > 0

    def test_component_metadata_scope_variations(self) -> None:
        """Test ComponentMetadata with all scope variations."""
        scopes = [
            ComponentScope.SINGLETON,
            ComponentScope.TRANSIENT,
            ComponentScope.SCOPED,
            ComponentScope.FACTORY,
            ComponentScope.CONDITIONAL,
        ]

        for scope in scopes:
            metadata = ComponentMetadata(
                component_type="TestComponent", context_name="test_context", scope=scope
            )
            assert metadata.scope == scope

    def test_component_metadata_layer_variations(self) -> None:
        """Test ComponentMetadata with all layer variations."""
        layers = [
            ComponentLayer.INFRASTRUCTURE,
            ComponentLayer.DOMAIN,
            ComponentLayer.APPLICATION,
            ComponentLayer.PRESENTATION,
            ComponentLayer.FRAMEWORK,
        ]

        for layer in layers:
            metadata = ComponentMetadata(
                component_type="TestComponent", context_name="test_context", layer=layer
            )
            assert metadata.layer == layer

    def test_component_metadata_lifecycle_update(self) -> None:
        """Test ComponentMetadata lifecycle stage update."""
        metadata = ComponentMetadata(
            component_type="TestComponent", context_name="test_context"
        )

        assert metadata.lifecycle_stage == LifecycleStage.CREATED
        assert metadata.updated_at is None

        # Update lifecycle stage
        metadata.update_lifecycle_stage(LifecycleStage.ACTIVE)

        assert metadata.lifecycle_stage == LifecycleStage.ACTIVE
        assert metadata.updated_at is not None
        assert isinstance(metadata.updated_at, datetime)

    def test_component_metadata_created_at_timestamp(self) -> None:
        """Test that created_at timestamp is properly set."""
        before_creation = datetime.now(UTC)

        metadata = ComponentMetadata(
            component_type="TestComponent", context_name="test_context"
        )

        after_creation = datetime.now(UTC)

        assert before_creation <= metadata.created_at <= after_creation

    def test_component_metadata_validation(self) -> None:
        """Test ComponentMetadata field validation."""
        # Valid metadata should not raise
        metadata = ComponentMetadata(
            component_type="TestComponent", context_name="test_context"
        )
        assert metadata is not None

        # Missing required fields should raise
        with pytest.raises(Exception):  # Could be ValidationError or TypeError
            ComponentMetadata(component_type="TestComponent")  # missing context_name

        with pytest.raises(Exception):  # Could be ValidationError or TypeError
            ComponentMetadata(context_name="test_context")  # missing component_type

    def test_component_metadata_string_representation(self) -> None:
        """Test ComponentMetadata string representation."""
        metadata = ComponentMetadata(
            component_type="TestComponent",
            context_name="test_context",
            component_name="test_component",
        )

        str_repr = str(metadata)
        assert "TestComponent" in str_repr

    def test_component_metadata_dict_representation(self) -> None:
        """Test ComponentMetadata dictionary representation."""
        metadata = ComponentMetadata(
            component_type="TestComponent",
            context_name="test_context",
            component_name="test_component",
            scope=ComponentScope.SINGLETON,
        )

        # Should be serializable to dict
        metadata_dict = metadata.model_dump()
        assert metadata_dict["component_type"] == "TestComponent"
        assert metadata_dict["context_name"] == "test_context"
        assert metadata_dict["component_name"] == "test_component"
        assert (
            metadata_dict["scope"] == ComponentScope.SINGLETON
        )  # Pydantic preserves enum objects
