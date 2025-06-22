"""Shared utilities for decorators."""

from typing import Any

from .._base import ComponentLayer
from .._utils import get_class_name, get_logger

logger = get_logger(__name__)


def detect_component_layer(cls: type) -> ComponentLayer | None:
    """
    Auto-detect the architectural layer of a component based on naming conventions.

    Args:
        cls: The component class

    Returns:
        Detected layer or None if cannot be determined
    """
    class_name = get_class_name(cls).lower()

    # Infrastructure layer indicators
    infrastructure_indicators = [
        "repository",
        "dao",
        "client",
        "adapter",
        "gateway",
        "connector",
        "driver",
        "database",
        "cache",
        "storage",
    ]

    # Application layer indicators
    application_indicators = [
        "service",
        "usecase",
        "application",
        "workflow",
        "orchestrator",
        "coordinator",
        "manager",
        "handler",
    ]

    # Domain layer indicators
    domain_indicators = [
        "entity",
        "aggregate",
        "valueobject",
        "domain",
        "model",
        "specification",
        "policy",
        "rule",
    ]

    # Framework layer indicators
    framework_indicators = [
        "framework",
        "component",
        "provider",
        "factory",
        "builder",
        "resolver",
        "interceptor",
        "filter",
        "middleware",
    ]

    # Presentation layer indicators
    presentation_indicators = [
        "controller",
        "endpoint",
        "resource",
        "presenter",
        "view",
        "api",
        "rest",
        "graphql",
        "web",
    ]

    # Check each layer
    for indicator in infrastructure_indicators:
        if indicator in class_name:
            logger.debug(
                "Detected infrastructure layer",
                class_name=cls.__name__,
                indicator=indicator,
            )
            return ComponentLayer.INFRASTRUCTURE

    for indicator in application_indicators:
        if indicator in class_name:
            logger.debug(
                "Detected application layer",
                class_name=cls.__name__,
                indicator=indicator,
            )
            return ComponentLayer.APPLICATION

    for indicator in domain_indicators:
        if indicator in class_name:
            logger.debug(
                "Detected domain layer",
                class_name=cls.__name__,
                indicator=indicator,
            )
            return ComponentLayer.DOMAIN

    for indicator in framework_indicators:
        if indicator in class_name:
            logger.debug(
                "Detected framework layer",
                class_name=cls.__name__,
                indicator=indicator,
            )
            return ComponentLayer.FRAMEWORK

    for indicator in presentation_indicators:
        if indicator in class_name:
            logger.debug(
                "Detected presentation layer",
                class_name=cls.__name__,
                indicator=indicator,
            )
            return ComponentLayer.PRESENTATION

    logger.debug(
        "Could not auto-detect component layer",
        class_name=cls.__name__,
    )
    return None


def enhance_component_tags(cls: type, existing_tags: dict[str, str]) -> dict[str, str]:
    """
    Enhance component tags with auto-detected information.

    Args:
        cls: The component class
        existing_tags: Existing tags from decorator options

    Returns:
        Enhanced tags dictionary
    """
    enhanced_tags = existing_tags.copy()

    # Add class information
    enhanced_tags["class_name"] = cls.__name__
    enhanced_tags["module"] = cls.__module__

    # Add layer if detected and not already set
    if "layer" not in enhanced_tags:
        detected_layer = detect_component_layer(cls)
        if detected_layer:
            enhanced_tags["layer"] = detected_layer.value

    # Add base classes information
    base_classes = [
        base.__name__ for base in cls.__bases__ if base.__name__ != "object"
    ]
    if base_classes:
        enhanced_tags["base_classes"] = ",".join(base_classes)

    # Add decorator marker
    enhanced_tags["decorated_with"] = "og_component"

    return enhanced_tags


def validate_decorator_target(cls: type, decorator_name: str) -> None:
    """
    Validate that a decorator is being applied to a valid target.

    Args:
        cls: The target class
        decorator_name: Name of the decorator for error messages

    Raises:
        ValueError: If the target is not valid
    """
    if not isinstance(cls, type):
        raise ValueError(
            f"@{decorator_name} can only be applied to classes, got {type(cls)}"
        )

    if not hasattr(cls, "__name__"):
        raise ValueError(f"@{decorator_name} target must have a __name__ attribute")

    logger.debug(
        "Validated decorator target",
        decorator=decorator_name,
        class_name=cls.__name__,
        module=cls.__module__,
    )


def create_metadata_dict(**kwargs: Any) -> dict[str, Any]:
    """
    Create a metadata dictionary from keyword arguments.

    Filters out None values and converts non-string values to strings.

    Args:
        **kwargs: Metadata key-value pairs

    Returns:
        Cleaned metadata dictionary
    """
    metadata = {}
    for key, value in kwargs.items():
        if value is not None:
            if isinstance(value, str | int | float | bool):
                metadata[key] = str(value)
            else:
                metadata[key] = str(value)
    return metadata


def get_decorator_signature(decorator_name: str, **options: Any) -> str:
    """
    Get a string representation of decorator usage for logging.

    Args:
        decorator_name: Name of the decorator
        **options: Decorator options

    Returns:
        String representation of decorator signature
    """
    option_strs = []
    for key, value in options.items():
        if value is not None:
            if isinstance(value, str):
                option_strs.append(f"{key}='{value}'")
            else:
                option_strs.append(f"{key}={value}")

    if option_strs:
        return f"@{decorator_name}({', '.join(option_strs)})"
    return f"@{decorator_name}"
