"""Configuration options for dependency injection decorators."""

from typing import Any

from pydantic import BaseModel, Field

from .._base import ComponentLayer, ComponentScope


class ComponentOptions(BaseModel):
    """
    Configuration options for the @og_component decorator.

    Provides flexible configuration for component registration while
    maintaining defaults that follow best practices.
    """

    # Core registration options
    interface: type | None = Field(
        default=None,
        description="Interface this component implements (defaults to the class itself)",
    )
    scope: ComponentScope = Field(
        default=ComponentScope.SINGLETON, description="Component lifecycle scope"
    )
    layer: ComponentLayer | None = Field(
        default=None, description="Architectural layer (auto-detected if not provided)"
    )

    # Context and container options
    context_name: str = Field(
        default="global", description="Name of the context for registration"
    )
    provider_name: str | None = Field(
        default=None,
        description="Custom provider name (auto-generated if not provided)",
    )

    # Component metadata options
    component_name: str | None = Field(
        default=None, description="Human-readable component name"
    )
    tags: dict[str, str] = Field(
        default_factory=dict, description="Component tags for categorization"
    )

    # Registration behavior options
    auto_register: bool = Field(
        default=True, description="Whether to automatically register on decoration"
    )
    lazy_init: bool = Field(
        default=False, description="Whether to use lazy initialization"
    )

    # Factory options
    factory: Any = Field(
        default=None, description="Custom factory function for component creation"
    )

    model_config = {"arbitrary_types_allowed": True}

    def get_provider_name(self, class_name: str) -> str:
        """Get the provider name for registration."""
        return self.provider_name or class_name

    def get_component_name(self, class_name: str) -> str:
        """Get the component name for metadata."""
        return self.component_name or class_name

    def get_tags_dict(self) -> dict[str, str]:
        """Get tags as a dictionary with string values."""
        return {k: str(v) for k, v in self.tags.items()}


class ContextOptions(BaseModel):
    """
    Configuration options for the @og_context decorator.

    Provides comprehensive options for module definitions while
    maintaining type safety and validation capabilities.
    """

    name: str = Field(description="Unique name for this context module")
    imports: list[Any] = Field(
        default_factory=list, description="List of imports from other contexts"
    )
    exports: list[type] = Field(
        default_factory=list, description="List of component types this module exports"
    )
    providers: list[Any] = Field(
        default_factory=list, description="List of provider configurations"
    )
    description: str | None = Field(
        default=None, description="Optional description of this module"
    )
    version: str = Field(
        default="1.0.0", description="Module version for compatibility tracking"
    )
    tags: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata tags"
    )

    model_config = {"arbitrary_types_allowed": True}

    def get_tags_dict(self) -> dict[str, str]:
        """Get tags as a dictionary with string values."""
        return {k: str(v) for k, v in self.tags.items()}
