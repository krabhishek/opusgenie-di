"""Context decorator for declarative module definition."""

from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from .._hooks import EventHook, emit_event
from .._modules.import_declaration import ImportCollection, ModuleContextImport
from .._modules.provider_config import (
    ProviderCollection,
    ProviderConfig,
    normalize_provider_list,
)
from .._registry import ModuleMetadata, register_module
from .._utils import get_logger, log_error, validate_module_name
from .decorator_options import ContextOptions
from .decorator_utils import (
    get_decorator_signature,
    validate_decorator_target,
)

T = TypeVar("T")

logger = get_logger(__name__)


def og_context(
    name: str | None = None,
    imports: Sequence[ModuleContextImport] | None = None,
    exports: Sequence[type] | None = None,
    providers: Sequence[Any] | None = None,
    description: str | None = None,
    version: str = "1.0.0",
    tags: dict[str, Any] | None = None,
) -> Callable[[type[T]], type[T]]:
    """
    Decorator for declarative context module definition.

    Args:
        name: Unique name for this context module
        imports: List of imports from other contexts
        exports: List of component types this module exports
        providers: List of provider configurations
        description: Optional description of this module
        version: Module version for compatibility tracking
        tags: Additional metadata tags

    Returns:
        Decorator function that enhances the class with module metadata

    Example:
        @og_context(
            name="user_management",
            imports=[
                ModuleContextImport(DatabaseConnection, from_context="infrastructure"),
                ModuleContextImport(Logger, from_context="logging"),
            ],
            exports=[
                UserService,
                UserRepository,
            ],
            providers=[
                {UserRepositoryInterface: SQLUserRepository},
                UserService,
                UserValidator,
            ]
        )
        class UserManagementModule:
            pass
    """

    def decorator(cls: type[T]) -> type[T]:
        """Apply context module decoration to the class."""
        try:
            # Validate decorator target
            validate_decorator_target(cls, "og_context")

            # Use class name as module name if not provided
            module_name = name or cls.__name__
            validate_module_name(module_name)

            # Create context options
            options = ContextOptions(
                name=module_name,
                imports=list(imports or []),
                exports=list(exports or []),
                providers=list(providers or []),
                description=description,
                version=version,
                tags=tags or {},
            )

            # Create and validate import collection
            import_collection = ImportCollection(imports=options.imports)
            import_errors = import_collection.validate_imports()
            if import_errors:
                raise ValueError(
                    f"Invalid imports in module {module_name}: {'; '.join(import_errors)}"
                )

            # Create and validate provider collection
            normalized_providers = normalize_provider_list(options.providers)
            provider_collection = ProviderCollection(providers=normalized_providers)
            provider_errors = provider_collection.validate_providers()
            if provider_errors:
                raise ValueError(
                    f"Invalid providers in module {module_name}: {'; '.join(provider_errors)}"
                )

            # Create module metadata
            metadata = ModuleMetadata(
                name=options.name,
                module_class=cls,
                imports=import_collection,
                exports=options.exports,
                providers=provider_collection,
                description=options.description,
                version=options.version,
                tags=options.get_tags_dict(),
            )

            # Register module in global registry
            register_module(metadata)

            # Add module-specific attributes to the class
            cls._og_module_metadata = metadata  # type: ignore[attr-defined]
            cls._og_module_options = options  # type: ignore[attr-defined]
            cls._og_import_collection = import_collection  # type: ignore[attr-defined]
            cls._og_provider_collection = provider_collection  # type: ignore[attr-defined]

            # Add convenience methods to the class
            _add_module_methods(cls, metadata)

            # Log decorator application
            decorator_sig = get_decorator_signature(
                "og_context",
                name=options.name,
                imports=len(options.imports),
                exports=len(options.exports),
                providers=len(options.providers),
                version=options.version,
            )
            logger.debug(
                "Applied context decorator",
                class_name=cls.__name__,
                module=cls.__module__,
                decorator_signature=decorator_sig,
                module_name=options.name,
            )

            # Emit module registration event
            emit_event(
                EventHook.MODULE_REGISTERED,
                {
                    "class_name": cls.__name__,
                    "module": cls.__module__,
                    "module_name": options.name,
                    "description": options.description,
                    "version": options.version,
                    "import_count": len(options.imports),
                    "export_count": len(options.exports),
                    "provider_count": len(options.providers),
                    "tags": options.get_tags_dict(),
                    "decorated_with": "og_context",
                },
            )

            return cls

        except Exception as e:
            log_error(
                "og_context_decorator",
                e,
                component_type=cls,
            )
            # Re-raise to prevent silent failures
            raise

    return decorator


def _add_module_methods(cls: type[Any], metadata: ModuleMetadata) -> None:
    """
    Add convenience methods to the module class.

    Args:
        cls: The module class to enhance
        metadata: Module metadata
    """

    def get_module_name(self: Any) -> str:
        """Get the module name."""
        return metadata.name

    def get_module_version(self: Any) -> str:
        """Get the module version."""
        return metadata.version

    def get_module_description(self: Any) -> str | None:
        """Get the module description."""
        return metadata.description

    def get_imports(self: Any) -> list[ModuleContextImport]:
        """Get the list of module imports."""
        return metadata.imports.imports

    def get_exports(self: Any) -> list[type]:
        """Get the list of module exports."""
        return metadata.exports

    def get_providers(self: Any) -> list[ProviderConfig]:
        """Get the list of provider configurations."""
        return metadata.providers.providers

    def get_module_metadata(self: Any) -> ModuleMetadata:
        """Get the complete module metadata."""
        return metadata

    def has_export(self: Any, component_type: type) -> bool:
        """Check if the module exports a specific component type."""
        return metadata.exports_component(component_type)

    def has_import(self: Any, component_type: type) -> bool:
        """Check if the module imports a specific component type."""
        return metadata.imports_component(component_type)

    def has_provider(self: Any, component_type: type) -> bool:
        """Check if the module provides a specific component type."""
        return metadata.provides_component(component_type)

    def get_dependencies(self: Any) -> list[str]:
        """Get the list of context dependencies."""
        return metadata.get_dependencies()

    def validate_module(self: Any) -> list[str]:
        """Validate the module configuration."""
        return metadata.validate_module()

    def get_summary(self: Any) -> dict[str, Any]:
        """Get a summary of the module."""
        return metadata.get_summary()

    # Add methods to the class
    cls.get_module_name = get_module_name
    cls.get_module_version = get_module_version
    cls.get_module_description = get_module_description
    cls.get_imports = get_imports
    cls.get_exports = get_exports
    cls.get_providers = get_providers
    cls.get_module_metadata = get_module_metadata
    cls.has_export = has_export
    cls.has_import = has_import
    cls.has_provider = has_provider
    cls.get_dependencies = get_dependencies
    cls.validate_module = validate_module
    cls.get_summary = get_summary


def get_module_metadata(module_class: type) -> ModuleMetadata | None:
    """
    Get module metadata from a decorated module class.

    Args:
        module_class: The module class to get metadata from

    Returns:
        Module metadata or None if not a module class
    """
    return getattr(module_class, "_og_module_metadata", None)


def get_module_options(module_class: type) -> ContextOptions | None:
    """
    Get module options from a decorated module class.

    Args:
        module_class: The module class to get options from

    Returns:
        Module options or None if not a module class
    """
    return getattr(module_class, "_og_module_options", None)


def is_context_module(cls: type) -> bool:
    """
    Check if a class is a context module.

    Args:
        cls: The class to check

    Returns:
        True if the class is decorated with @og_context
    """
    return hasattr(cls, "_og_module_metadata")


def get_all_context_modules() -> list[ModuleMetadata]:
    """
    Get all registered context modules.

    Returns:
        List of all module metadata instances
    """
    from .._registry import get_all_modules

    return get_all_modules()


def validate_all_module_dependencies() -> list[str]:
    """
    Validate dependencies across all registered modules.

    Returns:
        List of validation errors
    """
    from .._registry import validate_module_dependencies

    return validate_module_dependencies()
