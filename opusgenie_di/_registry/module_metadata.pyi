from .._modules.import_declaration import ImportCollection as ImportCollection
from .._modules.provider_config import ProviderCollection as ProviderCollection
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

class ModuleMetadata(BaseModel):
    """
    Metadata for a dependency injection module.

    Tracks comprehensive information about modules for registry management,
    dependency validation, and context building.
    """
    name: str
    module_class: type
    imports: ImportCollection
    exports: list[type]
    providers: ProviderCollection
    description: str | None
    version: str
    tags: dict[str, str]
    model_config: Incomplete
    def get_import_count(self) -> int:
        """Get the number of imports."""
    def get_export_count(self) -> int:
        """Get the number of exports."""
    def get_provider_count(self) -> int:
        """Get the number of providers."""
    def get_dependencies(self) -> list[str]:
        """Get list of context names this module depends on."""
    def has_dependency_on(self, context_name: str) -> bool:
        """Check if this module depends on a specific context."""
    def exports_component(self, component_type: type) -> bool:
        """Check if this module exports a specific component type."""
    def provides_component(self, component_type: type) -> bool:
        """Check if this module provides a specific component type."""
    def imports_component(self, component_type: type) -> bool:
        """Check if this module imports a specific component type."""
    def validate_module(self) -> list[str]:
        """
        Validate the module configuration.

        Returns:
            List of validation error messages
        """
    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the module."""
    def __repr__(self) -> str: ...
