from .logging import get_logger as get_logger
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

def is_union_type(type_hint: Any) -> bool:
    """Check if a type hint is a Union type (including | syntax)."""
def extract_non_none_types(type_hint: Any) -> list[type]:
    """Extract non-None types from a Union type hint."""
def get_primary_type(type_hint: Any) -> type | None:
    """
    Get the primary type from a type hint.

    For Union types, returns the first non-None type.
    For regular types, returns the type itself.
    """
def is_optional_type(type_hint: Any) -> bool:
    """Check if a type hint represents an optional type (Union with None)."""
def get_constructor_dependencies(cls) -> dict[str, tuple[type | None, bool]]:
    """
    Analyze a class constructor to extract dependency information.

    Returns:
        Dictionary mapping parameter names to (type, is_optional) tuples.
    """
def get_type_name(type_hint: Any) -> str:
    """Get a string representation of a type hint."""
def is_concrete_type(type_hint: Any) -> bool:
    """Check if a type hint represents a concrete (instantiable) type."""
def validate_type_compatibility(interface: type, implementation: type) -> bool:
    """
    Validate that an implementation is compatible with an interface.

    Returns True if the implementation can be used for the interface.
    """
