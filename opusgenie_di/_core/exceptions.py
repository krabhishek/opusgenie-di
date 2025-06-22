"""Core exceptions for the dependency injection system."""

from typing import Any


class DIError(Exception):
    """
    Base exception for all dependency injection related errors.

    This serves as the root exception for all DI specific errors,
    providing a common base for exception handling and error categorization.
    """

    def __init__(
        self,
        message: str,
        details: str | None = None,
        context_name: str | None = None,
        operation: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        self.context_name = context_name
        self.operation = operation

    def __str__(self) -> str:
        # For simple cases, just return the message
        if not self.context_name and not self.operation and not self.details:
            return self.message

        parts = [self.message]
        if self.context_name:
            parts.append(f"Context: {self.context_name}")
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


class ContainerError(DIError):
    """Base exception for container-related errors."""

    def __init__(
        self,
        message: str,
        container_name: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
        operation: str | None = None,
    ) -> None:
        super().__init__(message, details, context_name, operation)
        self.container_name = container_name


class ContextError(DIError):
    """Base exception for context-related errors."""


class ComponentRegistrationError(ContextError):
    """Exception for component registration errors."""

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        interface_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None:
        super().__init__(message, details, context_name)
        self.component_type = component_type
        self.interface_type = interface_type


class ComponentResolutionError(ContextError):
    """Exception for component resolution errors."""

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
        resolution_chain: list[str] | None = None,
    ) -> None:
        super().__init__(message, details, context_name)
        self.component_type = component_type
        self.resolution_chain = resolution_chain or []


class CircularDependencyError(ComponentResolutionError):
    """Exception for circular dependency detection."""

    def __init__(
        self,
        message: str,
        dependency_chain: list[str] | None = None,
        context_name: str | None = None,
    ) -> None:
        dependency_chain = dependency_chain or []
        details = (
            f"Dependency chain: {' -> '.join(dependency_chain)}"
            if dependency_chain
            else None
        )
        super().__init__(
            message,
            details=details,
            context_name=context_name,
            resolution_chain=dependency_chain,
        )
        self.dependency_chain = dependency_chain


class ScopeError(DIError):
    """Exception for component scope management errors."""

    def __init__(
        self,
        message: str,
        scope: str | None = None,
        component_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None:
        super().__init__(message, details, context_name)
        self.scope = scope
        self.component_type = component_type


class ProviderError(ContainerError):
    """Exception for provider-related errors."""

    def __init__(
        self,
        message: str,
        provider_name: str | None = None,
        component_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None:
        super().__init__(message, details=details, context_name=context_name)
        self.provider_name = provider_name
        self.component_type = component_type


class ImportError(DIError):
    """Exception for cross-context import errors."""

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        source_context: str | None = None,
        target_context: str | None = None,
        details: str | None = None,
    ) -> None:
        super().__init__(message, details, target_context)
        self.component_type = component_type
        self.source_context = source_context
        self.target_context = target_context


class ModuleError(DIError):
    """Exception for module-related errors."""

    def __init__(
        self,
        message: str,
        module_name: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None:
        super().__init__(message, details, context_name)
        self.module_name = module_name


class LifecycleError(DIError):
    """Exception for component lifecycle management errors."""

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        lifecycle_stage: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None:
        super().__init__(message, details, context_name)
        self.component_type = component_type
        self.lifecycle_stage = lifecycle_stage


class ValidationError(DIError):
    """Exception for validation errors in the DI system."""

    def __init__(
        self,
        message: str,
        validation_rule: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None:
        super().__init__(message, details, context_name)
        self.validation_rule = validation_rule


class ConfigurationError(DIError):
    """Exception for configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_value: Any = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None:
        super().__init__(message, details, context_name)
        self.config_key = config_key
        self.config_value = config_value


# Convenience aliases for common exceptions
ContainerInitializationError = ContainerError
ContextCreationError = ContextError
DependencyResolutionError = ComponentResolutionError
