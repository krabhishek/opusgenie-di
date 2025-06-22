from typing import Any

class DIError(Exception):
    message: str
    details: str | None
    context_name: str | None
    operation: str | None

    def __init__(
        self,
        message: str,
        details: str | None = None,
        context_name: str | None = None,
        operation: str | None = None,
    ) -> None: ...

class ContainerError(DIError):
    container_name: str | None

    def __init__(
        self,
        message: str,
        container_name: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
        operation: str | None = None,
    ) -> None: ...

class ContextError(DIError): ...

class ComponentRegistrationError(ContextError):
    component_type: str | None
    interface_type: str | None

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        interface_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None: ...

class ComponentResolutionError(ContextError):
    component_type: str | None
    resolution_chain: list[str]

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
        resolution_chain: list[str] | None = None,
    ) -> None: ...

class CircularDependencyError(ComponentResolutionError):
    dependency_chain: list[str]

    def __init__(
        self,
        message: str,
        dependency_chain: list[str] | None = None,
        context_name: str | None = None,
    ) -> None: ...

class ScopeError(DIError):
    scope: str | None
    component_type: str | None

    def __init__(
        self,
        message: str,
        scope: str | None = None,
        component_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None: ...

class ProviderError(ContainerError):
    provider_name: str | None
    component_type: str | None

    def __init__(
        self,
        message: str,
        provider_name: str | None = None,
        component_type: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None: ...

class ImportError(DIError):
    component_type: str | None
    source_context: str | None
    target_context: str | None

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        source_context: str | None = None,
        target_context: str | None = None,
        details: str | None = None,
    ) -> None: ...

class ModuleError(DIError):
    module_name: str | None

    def __init__(
        self,
        message: str,
        module_name: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None: ...

class LifecycleError(DIError):
    component_type: str | None
    lifecycle_stage: str | None

    def __init__(
        self,
        message: str,
        component_type: str | None = None,
        lifecycle_stage: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None: ...

class ValidationError(DIError):
    validation_rule: str | None

    def __init__(
        self,
        message: str,
        validation_rule: str | None = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None: ...

class ConfigurationError(DIError):
    config_key: str | None
    config_value: Any

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_value: Any = None,
        details: str | None = None,
        context_name: str | None = None,
    ) -> None: ...

# Convenience aliases for common exceptions
ContainerInitializationError = ContainerError
ContextCreationError = ContextError
DependencyResolutionError = ComponentResolutionError
