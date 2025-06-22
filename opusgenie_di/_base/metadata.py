"""Component metadata classes and utilities."""

from datetime import UTC, datetime
from typing import Any
import uuid

from pydantic import BaseModel, Field

from .enums import ComponentLayer, ComponentScope, LifecycleStage


class ComponentMetadata(BaseModel):
    """
    Metadata for dependency injection components.

    Tracks comprehensive information about components for debugging,
    monitoring, and management purposes.
    """

    # Core identity
    component_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this component instance",
    )
    component_type: str = Field(description="The component type name")
    component_name: str | None = Field(
        default=None, description="Human-readable name for this component instance"
    )

    # Classification
    layer: ComponentLayer | None = Field(
        default=None, description="The architectural layer this component belongs to"
    )
    scope: ComponentScope = Field(
        default=ComponentScope.SINGLETON, description="Component lifecycle scope"
    )
    tags: dict[str, str] = Field(
        default_factory=dict,
        description="Flexible tagging system for component categorization",
    )

    # Lifecycle
    lifecycle_stage: LifecycleStage = Field(
        default=LifecycleStage.CREATED, description="Current lifecycle stage"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when this component was created",
    )
    updated_at: datetime | None = Field(
        default=None, description="UTC timestamp when this component was last modified"
    )

    # Dependencies
    dependencies: list[str] = Field(
        default_factory=list, description="List of dependency type names"
    )
    optional_dependencies: list[str] = Field(
        default_factory=list, description="List of optional dependency type names"
    )

    # Registration info
    context_name: str = Field(
        description="Name of the context where component is registered"
    )
    provider_name: str | None = Field(
        default=None, description="Name of the provider used to create this component"
    )

    # Configuration
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component-specific configuration parameters"
    )

    model_config = {"arbitrary_types_allowed": True}

    def update_lifecycle_stage(self, stage: LifecycleStage) -> None:
        """Update the lifecycle stage and timestamp."""
        self.lifecycle_stage = stage
        self.updated_at = datetime.now(UTC)

    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the component metadata."""
        self.tags[key] = value
        self.updated_at = datetime.now(UTC)

    def add_dependency(self, dependency_type: str, optional: bool = False) -> None:
        """Add a dependency to the metadata."""
        if optional:
            if dependency_type not in self.optional_dependencies:
                self.optional_dependencies.append(dependency_type)
        else:
            if dependency_type not in self.dependencies:
                self.dependencies.append(dependency_type)
        self.updated_at = datetime.now(UTC)

    def get_age_seconds(self) -> float:
        """Get the age of the component in seconds."""
        now = datetime.now(UTC)
        return (now - self.created_at).total_seconds()

    def is_lifecycle_stage(self, stage: LifecycleStage) -> bool:
        """Check if the component is in a specific lifecycle stage."""
        return self.lifecycle_stage == stage

    def is_active(self) -> bool:
        """Check if the component is in an active state."""
        return self.lifecycle_stage in {
            LifecycleStage.ACTIVE,
            LifecycleStage.RUNNING,
            LifecycleStage.STARTUP,
        }

    def is_stopped(self) -> bool:
        """Check if the component is stopped."""
        return self.lifecycle_stage in {
            LifecycleStage.STOPPED,
            LifecycleStage.POST_SHUTDOWN,
        }

    def is_error(self) -> bool:
        """Check if the component is in an error state."""
        return self.lifecycle_stage == LifecycleStage.ERROR
