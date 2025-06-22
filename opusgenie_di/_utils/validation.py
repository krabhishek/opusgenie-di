"""Validation utilities for dependency injection components."""

from typing import Any

from .logging import get_logger
from .type_helpers import is_concrete_type, validate_type_compatibility

logger = get_logger(__name__)


class ValidationError(Exception):
    """Base exception for validation errors."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ComponentValidationError(ValidationError):
    """Exception for component validation errors."""

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        details: str | None = None,
    ) -> None:
        super().__init__(message, details)
        self.component_type = component_type


class ModuleValidationError(ValidationError):
    """Exception for module validation errors."""

    def __init__(
        self,
        message: str,
        module_name: str | None = None,
        details: str | None = None,
    ) -> None:
        super().__init__(message, details)
        self.module_name = module_name


def validate_component_registration(
    interface: type,
    implementation: type,
    component_name: str | None = None,
) -> None:
    """
    Validate a component registration.

    Args:
        interface: The interface type being registered
        implementation: The implementation type being registered
        component_name: Optional component name for error reporting

    Raises:
        ComponentValidationError: If validation fails
    """
    # Validate implementation is a type
    if not isinstance(implementation, type):
        raise ComponentValidationError(
            f"Implementation must be a type, got {type(implementation)}",
            component_type=component_name,
            details=f"Implementation {implementation} is not a type. Only types can be registered as implementations.",
        )

    # Set component name after type validation
    component_name = component_name or implementation.__name__

    # Validate implementation is concrete/instantiable
    if not is_concrete_type(implementation):
        raise ComponentValidationError(
            f"Implementation {implementation.__name__} is not instantiable",
            component_type=component_name,
            details="Implementation must be a concrete class with __init__ method",
        )

    # Validate interface/implementation compatibility
    if not validate_type_compatibility(interface, implementation):
        logger.warning(
            "Interface/implementation compatibility warning",
            interface=interface.__name__,
            implementation=implementation.__name__,
            component=component_name,
        )

    logger.debug(
        "Component registration validation passed",
        interface=interface.__name__,
        implementation=implementation.__name__,
        component=component_name,
    )


def validate_context_name(context_name: str) -> None:
    """
    Validate a context name.

    Args:
        context_name: The context name to validate

    Raises:
        ValidationError: If the context name is invalid
    """
    if not isinstance(context_name, str):
        raise ValidationError(
            f"Context name must be a string, got {type(context_name).__name__}",
            details=f"Expected string, got {type(context_name)}",
        )

    if not context_name or not context_name.strip():
        raise ValidationError(
            "Context name cannot be empty",
            details="Context names must be non-empty strings",
        )

    # Check for invalid characters (could be extended)
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for char in invalid_chars:
        if char in context_name:
            raise ValidationError(
                f"Context name contains invalid character '{char}'",
                details=f"Context names cannot contain: {', '.join(invalid_chars)}",
            )


def validate_module_name(module_name: str) -> None:
    """
    Validate a module name.

    Args:
        module_name: The module name to validate

    Raises:
        ModuleValidationError: If the module name is invalid
    """
    if not isinstance(module_name, str):
        raise ModuleValidationError(
            f"Module name must be a string, got {type(module_name).__name__}",
            details=f"Expected string, got {type(module_name)}",
        )

    if not module_name or not module_name.strip():
        raise ModuleValidationError(
            f"Module name must be a string, got {type(module_name)}",
            details=f"Module name {module_name} is not a string",
        )


def validate_provider_name(provider_name: str) -> None:
    """
    Validate a provider name.

    Args:
        provider_name: The provider name to validate

    Raises:
        ValidationError: If the provider name is invalid
    """
    if not isinstance(provider_name, str):
        raise ValidationError(
            f"Provider name must be a string, got {type(provider_name).__name__}",
            details=f"Expected string, got {type(provider_name)}",
        )

    if not provider_name or not provider_name.strip():
        raise ValidationError(
            f"Provider name must be a string, got {type(provider_name)}",
            details=f"Provider name {provider_name} is not a string",
        )


def validate_tags(tags: dict[str, Any]) -> None:
    """
    Validate component tags.

    Args:
        tags: The tags dictionary to validate

    Raises:
        ValidationError: If tags are invalid
    """
    if not isinstance(tags, dict):
        raise ValidationError(
            f"Tags must be a dictionary, got {type(tags)}",
            details=f"Tags {tags} is not a dictionary",
        )

    for key, value in tags.items():
        if not isinstance(key, str):
            raise ValidationError(
                f"Tag key must be a string, got {type(key)}",
                details=f"Tag key {key} is not a string",
            )

        # Convert values to strings if they aren't already
        if not isinstance(value, str):
            logger.debug(
                "Converting tag value to string",
                key=key,
                original_type=type(value).__name__,
                original_value=value,
            )


def validate_exports(exports: list[type]) -> None:
    """
    Validate module exports.

    Args:
        exports: List of types to export

    Raises:
        ModuleValidationError: If exports are invalid
    """
    if not isinstance(exports, list):
        raise ModuleValidationError(
            f"Exports must be a list, got {type(exports)}",
            details=f"Exports {exports} is not a list",
        )

    for export in exports:
        if not isinstance(export, type):
            raise ModuleValidationError(
                f"Export must be a type, got {type(export)}",
                details=f"Export {export} is not a type",
            )


def validate_component_dependencies(dependencies: list[str]) -> None:
    """
    Validate component dependencies list.

    Args:
        dependencies: List of dependency type names

    Raises:
        ComponentValidationError: If dependencies are invalid
    """
    if not isinstance(dependencies, list):
        raise ComponentValidationError(
            f"Dependencies must be a list, got {type(dependencies)}",
            details=f"Dependencies {dependencies} is not a list",
        )

    for dependency in dependencies:
        if not isinstance(dependency, str):
            raise ComponentValidationError(
                f"Dependency must be a string, got {type(dependency)}",
                details=f"Dependency {dependency} is not a string",
            )
