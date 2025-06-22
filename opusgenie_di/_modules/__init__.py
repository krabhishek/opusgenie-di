"""Module system for dependency injection contexts."""

from .builder import ContextModuleBuilder
from .import_declaration import ImportCollection, ModuleContextImport
from .provider_config import (
    ProviderCollection,
    ProviderConfig,
    normalize_provider_list,
    normalize_provider_specification,
)

__all__ = [
    # Builder
    "ContextModuleBuilder",
    # Imports
    "ModuleContextImport",
    "ImportCollection",
    # Providers
    "ProviderConfig",
    "ProviderCollection",
    "normalize_provider_specification",
    "normalize_provider_list",
]
