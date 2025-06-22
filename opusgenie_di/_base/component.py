"""Base component class for dependency injection."""

from abc import ABC
from datetime import UTC, datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field

from .enums import ComponentLayer, LifecycleStage
from .metadata import ComponentMetadata


class BaseComponent(BaseModel, ABC):
    """
    Base class for all components in the dependency injection system.

    This class provides the fundamental interface and metadata that all components
    in the DI system must implement. It uses Pydantic for data validation and
    serialization while maintaining compatibility with dependency injection patterns.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=False,
        use_enum_values=True,
        extra="allow",  # Allow extra fields for dependency injection
        validate_default=True,
    )

    # ==========================================
    # Core Identity & Metadata
    # ==========================================
    component_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this component instance",
    )

    component_type: str | None = Field(
        default=None,
        description="The specific component type (auto-set to class name)",
    )

    component_name: str | None = Field(
        default=None, description="Human-readable name for this component instance"
    )

    layer: ComponentLayer | None = Field(
        default=None, description="The architectural layer this component belongs to"
    )

    # ==========================================
    # Timestamps
    # ==========================================
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when this component was created",
    )

    updated_at: datetime | None = Field(
        default=None, description="UTC timestamp when this component was last modified"
    )

    # ==========================================
    # Configuration & Tags
    # ==========================================
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component-specific configuration parameters"
    )

    tags: dict[str, str] = Field(
        default_factory=dict,
        description="Flexible tagging system for component categorization",
    )

    # ==========================================
    # Lifecycle Management
    # ==========================================
    lifecycle_stage: LifecycleStage = Field(
        default=LifecycleStage.CREATED, description="Current lifecycle stage"
    )

    def __init__(self, **data: Any) -> None:
        """Initialize the component with automatic type detection."""
        # Auto-set component_type if not provided
        if "component_type" not in data:
            data["component_type"] = self.__class__.__name__

        super().__init__(**data)

    def get_component_id(self) -> str:
        """Get the unique identifier for this component."""
        return self.component_id

    def get_component_name(self) -> str | None:
        """Get the human-readable name for this component."""
        return self.component_name

    def get_component_type(self) -> str:
        """Get the component type name."""
        return self.component_type or self.__class__.__name__

    def get_lifecycle_stage(self) -> LifecycleStage:
        """Get the current lifecycle stage of the component."""
        return self.lifecycle_stage

    def set_lifecycle_stage(self, stage: LifecycleStage) -> None:
        """Set the lifecycle stage and update timestamp."""
        self.lifecycle_stage = stage
        self.updated_at = datetime.now(UTC)

    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the component."""
        self.tags[key] = value
        self.updated_at = datetime.now(UTC)

    def remove_tag(self, key: str) -> bool:
        """Remove a tag from the component. Returns True if tag existed."""
        if key in self.tags:
            del self.tags[key]
            self.updated_at = datetime.now(UTC)
            return True
        return False

    def get_tag(self, key: str, default: str | None = None) -> str | None:
        """Get a tag value by key."""
        return self.tags.get(key, default)

    def update_config(self, **config_updates: Any) -> None:
        """Update component configuration."""
        self.config.update(config_updates)
        self.updated_at = datetime.now(UTC)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self.config.get(key, default)

    def get_metadata(self) -> ComponentMetadata:
        """Get component metadata for DI system use."""
        return ComponentMetadata(
            component_id=self.component_id,
            component_type=self.get_component_type(),
            component_name=self.component_name,
            layer=self.layer,
            lifecycle_stage=self.lifecycle_stage,
            created_at=self.created_at,
            updated_at=self.updated_at,
            tags=self.tags.copy(),
            config=self.config.copy(),
            context_name="",  # Will be set by DI system
        )

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

    def get_age_seconds(self) -> float:
        """Get the age of the component in seconds."""
        now = datetime.now(UTC)
        return (now - self.created_at).total_seconds()

    # ==========================================
    # Lifecycle Methods (Optional Override)
    # ==========================================

    # Async lifecycle methods (preferred for async components)
    async def initialize(self) -> None:
        """Initialize the component async. Override in subclasses if needed."""
        self.set_lifecycle_stage(LifecycleStage.INITIALIZING)
        # Call sync variant for backward compatibility
        self.initialize_sync()
        self.set_lifecycle_stage(LifecycleStage.ACTIVE)

    async def start(self) -> None:
        """Start the component async. Override in subclasses if needed."""
        self.set_lifecycle_stage(LifecycleStage.STARTUP)
        # Call sync variant for backward compatibility
        self.start_sync()
        self.set_lifecycle_stage(LifecycleStage.RUNNING)

    async def stop(self) -> None:
        """Stop the component async. Override in subclasses if needed."""
        self.set_lifecycle_stage(LifecycleStage.STOPPING)
        # Call sync variant for backward compatibility
        self.stop_sync()
        self.set_lifecycle_stage(LifecycleStage.STOPPED)

    async def cleanup(self) -> None:
        """Clean up component resources async. Override in subclasses if needed."""
        # Call sync variant for backward compatibility
        self.cleanup_sync()
        self.set_lifecycle_stage(LifecycleStage.POST_SHUTDOWN)

    # Sync lifecycle methods (for sync components or mixed scenarios)
    def initialize_sync(self) -> None:
        """Initialize the component sync. Override in subclasses if needed."""
        # Default implementation does nothing
        # Subclasses can override for custom sync initialization

    def start_sync(self) -> None:
        """Start the component sync. Override in subclasses if needed."""
        # Default implementation does nothing
        # Subclasses can override for custom sync startup logic

    def stop_sync(self) -> None:
        """Stop the component sync. Override in subclasses if needed."""
        # Default implementation does nothing
        # Subclasses can override for custom sync shutdown logic

    def cleanup_sync(self) -> None:
        """Clean up component resources sync. Override in subclasses if needed."""
        # Default implementation does nothing
        # Subclasses can override for custom sync cleanup logic

    # Convenience method for sync-only disposal
    def dispose(self) -> None:
        """Dispose of component synchronously."""
        self.cleanup_sync()
        self.set_lifecycle_stage(LifecycleStage.POST_SHUTDOWN)

    def __repr__(self) -> str:
        """Get string representation of the component."""
        return (
            f"{self.__class__.__name__}("
            f"id='{self.component_id[:8]}...', "
            f"name='{self.component_name}', "
            f"stage={self.lifecycle_stage.value})"
        )
