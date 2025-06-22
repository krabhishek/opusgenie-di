"""Module metadata for the dependency injection registry."""

from typing import Any

from pydantic import BaseModel, Field

from .._modules.import_declaration import ImportCollection
from .._modules.provider_config import ProviderCollection


class ModuleMetadata(BaseModel):
    """
    Metadata for a dependency injection module.

    Tracks comprehensive information about modules for registry management,
    dependency validation, and context building.
    """

    name: str = Field(description="Unique module name")
    module_class: type = Field(description="The module class")
    imports: ImportCollection = Field(description="Module imports")
    exports: list[type] = Field(default_factory=list, description="Module exports")
    providers: ProviderCollection = Field(description="Module providers")
    description: str | None = Field(default=None, description="Module description")
    version: str = Field(default="1.0.0", description="Module version")
    tags: dict[str, str] = Field(default_factory=dict, description="Module tags")

    model_config = {"arbitrary_types_allowed": True}

    def get_import_count(self) -> int:
        """Get the number of imports."""
        return self.imports.get_import_count()

    def get_export_count(self) -> int:
        """Get the number of exports."""
        return len(self.exports)

    def get_provider_count(self) -> int:
        """Get the number of providers."""
        return self.providers.get_provider_count()

    def get_dependencies(self) -> list[str]:
        """Get list of context names this module depends on."""
        return self.imports.get_source_contexts()

    def has_dependency_on(self, context_name: str) -> bool:
        """Check if this module depends on a specific context."""
        return context_name in self.get_dependencies()

    def exports_component(self, component_type: type) -> bool:
        """Check if this module exports a specific component type."""
        return component_type in self.exports

    def provides_component(self, component_type: type) -> bool:
        """Check if this module provides a specific component type."""
        return component_type in self.providers

    def imports_component(self, component_type: type) -> bool:
        """Check if this module imports a specific component type."""
        return component_type in [imp.component_type for imp in self.imports]

    def validate_module(self) -> list[str]:
        """
        Validate the module configuration.

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate imports
        import_errors = self.imports.validate_imports()
        errors.extend(import_errors)

        # Validate providers
        provider_errors = self.providers.validate_providers()
        errors.extend(provider_errors)

        # Check that all exports are also provided
        provided_types = self.providers.get_interfaces()
        for export_type in self.exports:
            if export_type not in provided_types:
                errors.append(
                    f"Module exports {export_type.__name__} but does not provide it"
                )

        return errors

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the module."""
        return {
            "name": self.name,
            "module_class": self.module_class.__name__,
            "description": self.description,
            "version": self.version,
            "import_count": self.get_import_count(),
            "export_count": self.get_export_count(),
            "provider_count": self.get_provider_count(),
            "dependencies": self.get_dependencies(),
            "exports": [t.__name__ for t in self.exports],
            "tags": self.tags,
        }

    def __repr__(self) -> str:
        return (
            f"ModuleMetadata(name='{self.name}', "
            f"imports={self.get_import_count()}, "
            f"exports={self.get_export_count()}, "
            f"providers={self.get_provider_count()})"
        )
