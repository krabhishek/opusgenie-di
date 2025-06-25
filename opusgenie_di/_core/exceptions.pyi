from _typeshed import Incomplete
from typing import Any

class DIError(Exception):
    """
    Base exception for all dependency injection related errors.

    This serves as the root exception for all DI specific errors,
    providing a common base for exception handling and error categorization.
    """
    message: Incomplete
    details: Incomplete
    context_name: Incomplete
    operation: Incomplete
    def __init__(self, message: str, details: str | None = None, context_name: str | None = None, operation: str | None = None) -> None: ...
    def __str__(self) -> str: ...

class ContainerError(DIError):
    """Base exception for container-related errors."""
    container_name: Incomplete
    def __init__(self, message: str, container_name: str | None = None, details: str | None = None, context_name: str | None = None, operation: str | None = None) -> None: ...

class ContextError(DIError):
    """Base exception for context-related errors."""

class ComponentRegistrationError(ContextError):
    """Exception for component registration errors."""
    component_type: Incomplete
    interface_type: Incomplete
    def __init__(self, message: str, component_type: str | None = None, interface_type: str | None = None, details: str | None = None, context_name: str | None = None) -> None: ...

class ComponentResolutionError(ContextError):
    """Exception for component resolution errors."""
    component_type: Incomplete
    resolution_chain: Incomplete
    def __init__(self, message: str, component_type: str | None = None, details: str | None = None, context_name: str | None = None, resolution_chain: list[str] | None = None) -> None: ...

class CircularDependencyError(ComponentResolutionError):
    """Exception for circular dependency detection."""
    dependency_chain: Incomplete
    def __init__(self, message: str, dependency_chain: list[str] | None = None, context_name: str | None = None) -> None: ...

class ScopeError(DIError):
    """Exception for component scope management errors."""
    scope: Incomplete
    component_type: Incomplete
    def __init__(self, message: str, scope: str | None = None, component_type: str | None = None, details: str | None = None, context_name: str | None = None) -> None: ...

class ProviderError(ContainerError):
    """Exception for provider-related errors."""
    provider_name: Incomplete
    component_type: Incomplete
    def __init__(self, message: str, provider_name: str | None = None, component_type: str | None = None, details: str | None = None, context_name: str | None = None) -> None: ...

class ImportError(DIError):
    """Exception for cross-context import errors."""
    component_type: Incomplete
    source_context: Incomplete
    target_context: Incomplete
    def __init__(self, message: str, component_type: str | None = None, source_context: str | None = None, target_context: str | None = None, details: str | None = None) -> None: ...

class ModuleError(DIError):
    """Exception for module-related errors."""
    module_name: Incomplete
    def __init__(self, message: str, module_name: str | None = None, details: str | None = None, context_name: str | None = None) -> None: ...

class LifecycleError(DIError):
    """Exception for component lifecycle management errors."""
    component_type: Incomplete
    lifecycle_stage: Incomplete
    def __init__(self, message: str, component_type: str | None = None, lifecycle_stage: str | None = None, details: str | None = None, context_name: str | None = None) -> None: ...

class ValidationError(DIError):
    """Exception for validation errors in the DI system."""
    validation_rule: Incomplete
    def __init__(self, message: str, validation_rule: str | None = None, details: str | None = None, context_name: str | None = None) -> None: ...

class ConfigurationError(DIError):
    """Exception for configuration-related errors."""
    config_key: Incomplete
    config_value: Incomplete
    def __init__(self, message: str, config_key: str | None = None, config_value: Any = None, details: str | None = None, context_name: str | None = None) -> None: ...
ContainerInitializationError = ContainerError
ContextCreationError = ContextError
DependencyResolutionError = ComponentResolutionError
