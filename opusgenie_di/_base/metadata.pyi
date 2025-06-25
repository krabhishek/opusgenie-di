from .enums import ComponentLayer as ComponentLayer, ComponentScope as ComponentScope, LifecycleStage as LifecycleStage
from _typeshed import Incomplete
from datetime import datetime
from pydantic import BaseModel
from typing import Any

class ComponentMetadata(BaseModel):
    """
    Metadata for dependency injection components.

    Tracks comprehensive information about components for debugging,
    monitoring, and management purposes.
    """
    component_id: str
    component_type: str
    component_name: str | None
    layer: ComponentLayer | None
    scope: ComponentScope
    tags: dict[str, str]
    lifecycle_stage: LifecycleStage
    created_at: datetime
    updated_at: datetime | None
    dependencies: list[str]
    optional_dependencies: list[str]
    context_name: str
    provider_name: str | None
    config: dict[str, Any]
    model_config: Incomplete
    def update_lifecycle_stage(self, stage: LifecycleStage) -> None:
        """Update the lifecycle stage and timestamp."""
    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the component metadata."""
    def add_dependency(self, dependency_type: str, optional: bool = False) -> None:
        """Add a dependency to the metadata."""
    def get_age_seconds(self) -> float:
        """Get the age of the component in seconds."""
    def is_lifecycle_stage(self, stage: LifecycleStage) -> bool:
        """Check if the component is in a specific lifecycle stage."""
    def is_active(self) -> bool:
        """Check if the component is in an active state."""
    def is_stopped(self) -> bool:
        """Check if the component is stopped."""
    def is_error(self) -> bool:
        """Check if the component is in an error state."""
