from .._utils import get_logger as get_logger, validate_context_name as validate_context_name
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

logger: Incomplete

class ModuleContextImport(BaseModel):
    """
    Declaration for importing a component from another context.

    This represents a cross-context dependency that needs to be resolved
    from a different context than the one making the request.
    """
    component_type: type
    from_context: str
    name: str | None
    alias: str | None
    required: bool
    model_config: Incomplete
    def model_post_init(self, __context: Any, /) -> None:
        """Validate import declaration after initialization."""
    def get_provider_name(self) -> str:
        """Get the provider name for this import."""
    def get_import_key(self) -> str:
        """Get a unique key for this import."""
    def get_local_name(self) -> str:
        """Get the local name to use in the importing context."""
    def to_core_import_declaration(self) -> Any:
        """Convert to core ImportDeclaration for context system."""
    def __repr__(self) -> str: ...

class ImportCollection(BaseModel):
    """Collection of module imports with validation and utilities."""
    imports: list[ModuleContextImport]
    def add_import(self, import_declaration: ModuleContextImport) -> None:
        """Add an import declaration to the collection."""
    def get_imports_by_context(self, context_name: str) -> list[ModuleContextImport]:
        """Get all imports from a specific context."""
    def get_required_imports(self) -> list[ModuleContextImport]:
        """Get all required imports."""
    def get_optional_imports(self) -> list[ModuleContextImport]:
        """Get all optional imports."""
    def get_component_types(self) -> list[type]:
        """Get all imported component types."""
    def get_source_contexts(self) -> list[str]:
        """Get all unique source context names."""
    def validate_imports(self) -> list[str]:
        """
        Validate all imports in the collection.

        Returns:
            List of validation error messages
        """
    def get_import_count(self) -> int:
        """Get the number of imports."""
    def clear(self) -> None:
        """Clear all imports."""
    def __len__(self) -> int: ...
    def __iter__(self): ...
    def __contains__(self, item: ModuleContextImport | str) -> bool: ...
