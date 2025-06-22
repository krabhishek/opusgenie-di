"""Base components and utilities for the dependency injection system."""

from .component import BaseComponent
from .enums import (
    ComponentLayer,
    ComponentScope,
    LifecycleStage,
    RegistrationStrategy,
)
from .metadata import ComponentMetadata
from .protocols import (
    ComponentMetadataProtocol,
    ComponentProtocol,
    ComponentProviderProtocol,
    InjectableProtocol,
    LifecycleProtocol,
    RegistrableProtocol,
)

__all__ = [
    # Core component class
    "BaseComponent",
    # Enumerations
    "ComponentScope",
    "ComponentLayer",
    "LifecycleStage",
    "RegistrationStrategy",
    # Metadata
    "ComponentMetadata",
    # Protocols
    "ComponentProtocol",
    "InjectableProtocol",
    "ComponentProviderProtocol",
    "LifecycleProtocol",
    "ComponentMetadataProtocol",
    "RegistrableProtocol",
]
