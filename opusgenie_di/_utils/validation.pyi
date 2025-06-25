from .logging import get_logger as get_logger
from .type_helpers import is_concrete_type as is_concrete_type, validate_type_compatibility as validate_type_compatibility
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class ValidationError(Exception):
    """Base exception for validation errors."""
    message: Incomplete
    details: Incomplete
    def __init__(self, message: str, details: str | None = None) -> None: ...

class ComponentValidationError(ValidationError):
    """Exception for component validation errors."""
    component_type: Incomplete
    def __init__(self, message: str, component_type: str | None = None, details: str | None = None) -> None: ...

class ModuleValidationError(ValidationError):
    """Exception for module validation errors."""
    module_name: Incomplete
    def __init__(self, message: str, module_name: str | None = None, details: str | None = None) -> None: ...

def validate_component_registration(interface: type, implementation: type, component_name: str | None = None) -> None:
    """
    Validate a component registration.

    Args:
        interface: The interface type being registered
        implementation: The implementation type being registered
        component_name: Optional component name for error reporting

    Raises:
        ComponentValidationError: If validation fails
    """
def validate_context_name(context_name: str) -> None:
    """
    Validate a context name.

    Args:
        context_name: The context name to validate

    Raises:
        ValidationError: If the context name is invalid
    """
def validate_module_name(module_name: str) -> None:
    """
    Validate a module name.

    Args:
        module_name: The module name to validate

    Raises:
        ModuleValidationError: If the module name is invalid
    """
def validate_provider_name(provider_name: str) -> None:
    """
    Validate a provider name.

    Args:
        provider_name: The provider name to validate

    Raises:
        ValidationError: If the provider name is invalid
    """
def validate_tags(tags: dict[str, Any]) -> None:
    """
    Validate component tags.

    Args:
        tags: The tags dictionary to validate

    Raises:
        ValidationError: If tags are invalid
    """
def validate_exports(exports: list[type]) -> None:
    """
    Validate module exports.

    Args:
        exports: List of types to export

    Raises:
        ModuleValidationError: If exports are invalid
    """
def validate_component_dependencies(dependencies: list[str]) -> None:
    """
    Validate component dependencies list.

    Args:
        dependencies: List of dependency type names

    Raises:
        ComponentValidationError: If dependencies are invalid
    """
