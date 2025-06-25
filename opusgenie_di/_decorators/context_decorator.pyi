from .._hooks import EventHook as EventHook, emit_event as emit_event
from .._modules.import_declaration import ImportCollection as ImportCollection, ModuleContextImport as ModuleContextImport
from .._modules.provider_config import ProviderCollection as ProviderCollection, ProviderConfig as ProviderConfig, normalize_provider_list as normalize_provider_list
from .._registry import ModuleMetadata as ModuleMetadata, register_module as register_module
from .._utils import get_logger as get_logger, log_error as log_error, validate_module_name as validate_module_name
from .decorator_options import ContextOptions as ContextOptions
from .decorator_utils import get_decorator_signature as get_decorator_signature, validate_decorator_target as validate_decorator_target
from _typeshed import Incomplete
from collections.abc import Callable as Callable, Sequence
from typing import Any, TypeVar

T = TypeVar('T')
logger: Incomplete

def og_context(name: str | None = None, imports: Sequence[ModuleContextImport] | None = None, exports: Sequence[type] | None = None, providers: Sequence[Any] | None = None, description: str | None = None, version: str = '1.0.0', tags: dict[str, Any] | None = None) -> Callable[[type[T]], type[T]]:
    '''
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
    '''
def _add_module_methods(cls, metadata: ModuleMetadata) -> None:
    """
    Add convenience methods to the module class.

    Args:
        cls: The module class to enhance
        metadata: Module metadata
    """
def get_module_metadata(module_class: type) -> ModuleMetadata | None:
    """
    Get module metadata from a decorated module class.

    Args:
        module_class: The module class to get metadata from

    Returns:
        Module metadata or None if not a module class
    """
def get_module_options(module_class: type) -> ContextOptions | None:
    """
    Get module options from a decorated module class.

    Args:
        module_class: The module class to get options from

    Returns:
        Module options or None if not a module class
    """
def is_context_module(cls) -> bool:
    """
    Check if a class is a context module.

    Args:
        cls: The class to check

    Returns:
        True if the class is decorated with @og_context
    """
def get_all_context_modules() -> list[ModuleMetadata]:
    """
    Get all registered context modules.

    Returns:
        List of all module metadata instances
    """
def validate_all_module_dependencies() -> list[str]:
    """
    Validate dependencies across all registered modules.

    Returns:
        List of validation errors
    """
