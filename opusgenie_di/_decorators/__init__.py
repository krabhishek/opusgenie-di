"""Decorators for dependency injection component and context management."""

from .component_decorator import (
    get_component_metadata,
    get_component_options,
    get_enhanced_tags,
    is_og_component,
    og_component,
    register_component_manually,
)
from .context_decorator import (
    get_all_context_modules,
    get_module_metadata,
    get_module_options,
    is_context_module,
    og_context,
    validate_all_module_dependencies,
)
from .decorator_options import ComponentOptions, ContextOptions
from .decorator_utils import (
    create_metadata_dict,
    detect_component_layer,
    enhance_component_tags,
    get_decorator_signature,
    validate_decorator_target,
)

__all__ = [
    # Component decorator
    "og_component",
    "get_component_options",
    "get_component_metadata",
    "get_enhanced_tags",
    "is_og_component",
    "register_component_manually",
    # Context decorator
    "og_context",
    "get_module_metadata",
    "get_module_options",
    "is_context_module",
    "get_all_context_modules",
    "validate_all_module_dependencies",
    # Options classes
    "ComponentOptions",
    "ContextOptions",
    # Utilities
    "detect_component_layer",
    "enhance_component_tags",
    "validate_decorator_target",
    "create_metadata_dict",
    "get_decorator_signature",
]
