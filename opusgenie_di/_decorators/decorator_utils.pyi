from .._base import ComponentLayer as ComponentLayer
from .._utils import get_class_name as get_class_name, get_logger as get_logger
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

def detect_component_layer(cls) -> ComponentLayer | None:
    """
    Auto-detect the architectural layer of a component based on naming conventions.

    Args:
        cls: The component class

    Returns:
        Detected layer or None if cannot be determined
    """
def enhance_component_tags(cls, existing_tags: dict[str, str]) -> dict[str, str]:
    """
    Enhance component tags with auto-detected information.

    Args:
        cls: The component class
        existing_tags: Existing tags from decorator options

    Returns:
        Enhanced tags dictionary
    """
def validate_decorator_target(cls, decorator_name: str) -> None:
    """
    Validate that a decorator is being applied to a valid target.

    Args:
        cls: The target class
        decorator_name: Name of the decorator for error messages

    Raises:
        ValueError: If the target is not valid
    """
def create_metadata_dict(**kwargs: Any) -> dict[str, Any]:
    """
    Create a metadata dictionary from keyword arguments.

    Filters out None values and converts non-string values to strings.

    Args:
        **kwargs: Metadata key-value pairs

    Returns:
        Cleaned metadata dictionary
    """
def get_decorator_signature(decorator_name: str, **options: Any) -> str:
    """
    Get a string representation of decorator usage for logging.

    Args:
        decorator_name: Name of the decorator
        **options: Decorator options

    Returns:
        String representation of decorator signature
    """
