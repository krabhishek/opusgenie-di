"""Type checking and manipulation utilities."""

import inspect
import types
from typing import Any, Union, get_args, get_origin

from .logging import get_logger

logger = get_logger(__name__)


def is_union_type(type_hint: Any) -> bool:
    """Check if a type hint is a Union type (including | syntax)."""
    # Handle new Union syntax (X | Y)
    if isinstance(type_hint, types.UnionType):
        return True

    # Handle typing.Union
    origin = get_origin(type_hint)
    return origin is Union


def extract_non_none_types(type_hint: Any) -> list[type]:
    """Extract non-None types from a Union type hint."""
    if not is_union_type(type_hint):
        return [type_hint] if type_hint is not type(None) else []

    args = get_args(type_hint)
    return [arg for arg in args if arg is not type(None)]


def get_primary_type(type_hint: Any) -> type | None:
    """
    Get the primary type from a type hint.

    For Union types, returns the first non-None type.
    For regular types, returns the type itself.
    """
    if is_union_type(type_hint):
        non_none_types = extract_non_none_types(type_hint)
        return non_none_types[0] if non_none_types else None

    if type_hint is not type(None) and inspect.isclass(type_hint):
        return type_hint
    return None


def is_optional_type(type_hint: Any) -> bool:
    """Check if a type hint represents an optional type (Union with None)."""
    if not is_union_type(type_hint):
        return False

    args = get_args(type_hint)
    return type(None) in args


def get_constructor_dependencies(cls: type) -> dict[str, tuple[type | None, bool]]:
    """
    Analyze a class constructor to extract dependency information.

    Returns:
        Dictionary mapping parameter names to (type, is_optional) tuples.
    """
    try:
        signature = inspect.signature(cls)
        dependencies = {}

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            # Get the type annotation
            type_hint = param.annotation
            if type_hint == inspect.Parameter.empty:
                # No type annotation, skip
                logger.debug(
                    "Parameter without type annotation",
                    class_name=cls.__name__,
                    parameter=param_name,
                )
                continue

            # Check if it's optional (has default value or Union with None)
            has_default = param.default != inspect.Parameter.empty
            is_optional_union = is_optional_type(type_hint)
            is_optional = has_default or is_optional_union

            # Get the primary type
            primary_type = get_primary_type(type_hint)

            dependencies[param_name] = (primary_type, is_optional)

        return dependencies

    except Exception as e:
        logger.warning(
            "Failed to analyze constructor dependencies",
            class_name=cls.__name__,
            error=str(e),
        )
        return {}


def get_type_name(type_hint: Any) -> str:
    """Get a string representation of a type hint."""
    if hasattr(type_hint, "__name__"):
        return str(type_hint.__name__)
    return str(type_hint)


def is_concrete_type(type_hint: Any) -> bool:
    """Check if a type hint represents a concrete (instantiable) type."""
    try:
        if type_hint is None or type_hint is type(None):
            return False

        # Check if it's a class and has __init__
        return inspect.isclass(type_hint) and hasattr(type_hint, "__init__")
    except Exception:
        return False


def validate_type_compatibility(interface: type, implementation: type) -> bool:
    """
    Validate that an implementation is compatible with an interface.

    Returns True if the implementation can be used for the interface.
    """
    try:
        # Same type is always compatible
        if interface == implementation:
            return True

        # Check if implementation is a subclass of interface
        if inspect.isclass(interface) and inspect.isclass(implementation):
            return issubclass(implementation, interface)

        # For protocols and other complex types, assume compatible
        # This could be enhanced with more sophisticated protocol checking
        return True

    except TypeError:
        # Some types don't work with issubclass (like protocols)
        logger.debug(
            "Type compatibility check failed, assuming compatible",
            interface=get_type_name(interface),
            implementation=get_type_name(implementation),
        )
        return True
