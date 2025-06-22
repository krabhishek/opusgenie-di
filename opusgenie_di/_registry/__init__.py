"""Registry system for tracking modules and components."""

from .global_registry import (
    GlobalRegistry,
    clear_global_registry,
    get_all_modules,
    get_build_order,
    get_global_registry,
    get_module,
    register_module,
    validate_module_dependencies,
)
from .module_metadata import ModuleMetadata

__all__ = [
    # Registry
    "GlobalRegistry",
    "get_global_registry",
    "register_module",
    "get_module",
    "get_all_modules",
    "validate_module_dependencies",
    "get_build_order",
    "clear_global_registry",
    # Metadata
    "ModuleMetadata",
]
