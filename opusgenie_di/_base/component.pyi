from .enums import ComponentLayer as ComponentLayer, LifecycleStage as LifecycleStage
from .metadata import ComponentMetadata as ComponentMetadata
from _typeshed import Incomplete
from abc import ABC
from datetime import datetime
from pydantic import BaseModel
from typing import Any

class BaseComponent(BaseModel, ABC):
    """
    Base class for all components in the dependency injection system.

    This class provides the fundamental interface and metadata that all components
    in the DI system must implement. It uses Pydantic for data validation and
    serialization while maintaining compatibility with dependency injection patterns.
    """
    model_config: Incomplete
    component_id: str
    component_type: str | None
    component_name: str | None
    layer: ComponentLayer | None
    created_at: datetime
    updated_at: datetime | None
    config: dict[str, Any]
    tags: dict[str, str]
    lifecycle_stage: LifecycleStage
    def __init__(self, **data: Any) -> None:
        """Initialize the component with automatic type detection."""
    def get_component_id(self) -> str:
        """Get the unique identifier for this component."""
    def get_component_name(self) -> str | None:
        """Get the human-readable name for this component."""
    def get_component_type(self) -> str:
        """Get the component type name."""
    def get_lifecycle_stage(self) -> LifecycleStage:
        """Get the current lifecycle stage of the component."""
    def set_lifecycle_stage(self, stage: LifecycleStage) -> None:
        """Set the lifecycle stage and update timestamp."""
    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the component."""
    def remove_tag(self, key: str) -> bool:
        """Remove a tag from the component. Returns True if tag existed."""
    def get_tag(self, key: str, default: str | None = None) -> str | None:
        """Get a tag value by key."""
    def update_config(self, **config_updates: Any) -> None:
        """Update component configuration."""
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
    def get_metadata(self) -> ComponentMetadata:
        """Get component metadata for DI system use."""
    def is_active(self) -> bool:
        """Check if the component is in an active state."""
    def is_stopped(self) -> bool:
        """Check if the component is stopped."""
    def is_error(self) -> bool:
        """Check if the component is in an error state."""
    def get_age_seconds(self) -> float:
        """Get the age of the component in seconds."""
    async def initialize(self) -> None:
        """Initialize the component async. Override in subclasses if needed."""
    async def start(self) -> None:
        """Start the component async. Override in subclasses if needed."""
    async def stop(self) -> None:
        """Stop the component async. Override in subclasses if needed."""
    async def cleanup(self) -> None:
        """Clean up component resources async. Override in subclasses if needed."""
    def initialize_sync(self) -> None:
        """Initialize the component sync. Override in subclasses if needed."""
    def start_sync(self) -> None:
        """Start the component sync. Override in subclasses if needed."""
    def stop_sync(self) -> None:
        """Stop the component sync. Override in subclasses if needed."""
    def cleanup_sync(self) -> None:
        """Clean up component resources sync. Override in subclasses if needed."""
    def dispose(self) -> None:
        """Dispose of component synchronously."""
    def __repr__(self) -> str:
        """Get string representation of the component."""
