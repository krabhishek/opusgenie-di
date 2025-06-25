from .._base import ComponentLayer as ComponentLayer, ComponentScope as ComponentScope
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

class ComponentOptions(BaseModel):
    """
    Configuration options for the @og_component decorator.

    Provides flexible configuration for component registration while
    maintaining defaults that follow best practices.
    """
    interface: type | None
    scope: ComponentScope
    layer: ComponentLayer | None
    context_name: str
    provider_name: str | None
    component_name: str | None
    tags: dict[str, str]
    auto_register: bool
    lazy_init: bool
    factory: Any
    model_config: Incomplete
    def get_provider_name(self, class_name: str) -> str:
        """Get the provider name for registration."""
    def get_component_name(self, class_name: str) -> str:
        """Get the component name for metadata."""
    def get_tags_dict(self) -> dict[str, str]:
        """Get tags as a dictionary with string values."""

class ContextOptions(BaseModel):
    """
    Configuration options for the @og_context decorator.

    Provides comprehensive options for module definitions while
    maintaining type safety and validation capabilities.
    """
    name: str
    imports: list[Any]
    exports: list[type]
    providers: list[Any]
    description: str | None
    version: str
    tags: dict[str, Any]
    model_config: Incomplete
    def get_tags_dict(self) -> dict[str, str]:
        """Get tags as a dictionary with string values."""
