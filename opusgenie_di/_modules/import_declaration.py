"""Import declarations for cross-context dependencies."""

from typing import Any

from pydantic import BaseModel, Field

from .._utils import get_logger, validate_context_name

logger = get_logger(__name__)


class ModuleContextImport(BaseModel):
    """
    Declaration for importing a component from another context.

    This represents a cross-context dependency that needs to be resolved
    from a different context than the one making the request.
    """

    component_type: type = Field(description="Type of component to import")
    from_context: str = Field(description="Name of the context to import from")
    name: str | None = Field(
        default=None, description="Optional specific name of the component"
    )
    alias: str | None = Field(
        default=None, description="Optional alias to use in the importing context"
    )
    required: bool = Field(
        default=True,
        description="Whether this import is required for module to function",
    )

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context: Any, /) -> None:
        """Validate import declaration after initialization."""
        # Validate context name
        validate_context_name(self.from_context)

        # Validate component type
        if not isinstance(self.component_type, type):
            raise ValueError(
                f"component_type must be a type, got {type(self.component_type)}"
            )

    def get_provider_name(self) -> str:
        """Get the provider name for this import."""
        return self.name or self.component_type.__name__

    def get_import_key(self) -> str:
        """Get a unique key for this import."""
        return f"{self.from_context}:{self.get_provider_name()}"

    def get_local_name(self) -> str:
        """Get the local name to use in the importing context."""
        return self.alias or self.get_provider_name()

    def to_core_import_declaration(self) -> Any:
        """Convert to core ImportDeclaration for context system."""
        from .._core.context_impl import ImportDeclaration

        return ImportDeclaration(
            component_type=self.component_type,
            source_context=self.from_context,
            name=self.name,
            alias=self.alias,
        )

    def __repr__(self) -> str:
        return (
            f"ModuleContextImport(type={self.component_type.__name__}, "
            f"from={self.from_context}, name={self.name}, alias={self.alias})"
        )


class ImportCollection(BaseModel):
    """Collection of module imports with validation and utilities."""

    imports: list[ModuleContextImport] = Field(
        default_factory=list, description="List of import declarations"
    )

    def add_import(self, import_declaration: ModuleContextImport) -> None:
        """Add an import declaration to the collection."""
        # Check for duplicates
        import_key = import_declaration.get_import_key()
        for existing in self.imports:
            if existing.get_import_key() == import_key:
                logger.warning(
                    "Duplicate import declaration",
                    import_key=import_key,
                    component=import_declaration.component_type.__name__,
                )
                return

        self.imports.append(import_declaration)
        logger.debug(
            "Added import declaration",
            import_key=import_key,
            component=import_declaration.component_type.__name__,
            from_context=import_declaration.from_context,
        )

    def get_imports_by_context(self, context_name: str) -> list[ModuleContextImport]:
        """Get all imports from a specific context."""
        return [imp for imp in self.imports if imp.from_context == context_name]

    def get_required_imports(self) -> list[ModuleContextImport]:
        """Get all required imports."""
        return [imp for imp in self.imports if imp.required]

    def get_optional_imports(self) -> list[ModuleContextImport]:
        """Get all optional imports."""
        return [imp for imp in self.imports if not imp.required]

    def get_component_types(self) -> list[type]:
        """Get all imported component types."""
        return [imp.component_type for imp in self.imports]

    def get_source_contexts(self) -> list[str]:
        """Get all unique source context names."""
        return list({imp.from_context for imp in self.imports})

    def validate_imports(self) -> list[str]:
        """
        Validate all imports in the collection.

        Returns:
            List of validation error messages
        """
        errors = []

        # Check for conflicts (same component type from different contexts)
        component_sources: dict[str, str] = {}
        for imp in self.imports:
            component_name = imp.component_type.__name__
            if component_name in component_sources:
                existing_context = component_sources[component_name]
                if existing_context != imp.from_context:
                    errors.append(
                        f"Component {component_name} imported from multiple contexts: "
                        f"{existing_context} and {imp.from_context}"
                    )
            else:
                component_sources[component_name] = imp.from_context

        # Check for circular dependencies (would need more context information)
        # This is a simplified check - a full implementation would need
        # access to the entire module dependency graph

        return errors

    def get_import_count(self) -> int:
        """Get the number of imports."""
        return len(self.imports)

    def clear(self) -> None:
        """Clear all imports."""
        self.imports.clear()

    def __len__(self) -> int:
        return len(self.imports)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self.imports)

    def __contains__(self, item: ModuleContextImport | str) -> bool:
        if isinstance(item, str):
            # Check by import key
            return any(imp.get_import_key() == item for imp in self.imports)
        if isinstance(item, ModuleContextImport):
            return item in self.imports
        return False
