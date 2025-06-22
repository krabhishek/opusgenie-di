"""Component decorator for automatic registration in the dependency injection system."""

from collections.abc import Callable
from typing import Any, TypeVar

from .._base import ComponentLayer, ComponentScope
from .._core import get_global_context
from .._hooks import EventHook, emit_event
from .._utils import get_logger, log_error
from .decorator_options import ComponentOptions
from .decorator_utils import (
    create_metadata_dict,
    detect_component_layer,
    enhance_component_tags,
    get_decorator_signature,
    validate_decorator_target,
)

T = TypeVar("T")

logger = get_logger(__name__)


def og_component(
    interface: type | None = None,
    *,
    scope: ComponentScope = ComponentScope.SINGLETON,
    layer: ComponentLayer | None = None,
    context_name: str = "global",
    component_name: str | None = None,
    provider_name: str | None = None,
    tags: dict[str, Any] | None = None,
    auto_register: bool = True,
    lazy_init: bool = False,
    factory: Any = None,
) -> Callable[[type[T]], type[T]]:
    """
    Decorator for automatic component registration in the dependency injection system.

    Args:
        interface: Interface this component implements (defaults to the class itself)
        scope: Component lifecycle scope
        layer: Architectural layer (auto-detected if not provided)
        context_name: Name of the context for registration
        component_name: Human-readable component name
        provider_name: Custom provider name (auto-generated if not provided)
        tags: Component tags for categorization
        auto_register: Whether to automatically register on decoration
        lazy_init: Whether to use lazy initialization
        factory: Custom factory function for component creation

    Returns:
        Decorator function that enhances the class with DI metadata

    Example:
        @og_component(scope=ComponentScope.SINGLETON, layer=ComponentLayer.APPLICATION)
        class UserService(BaseComponent):
            def __init__(self, repo: UserRepository):
                super().__init__()
                self.repo = repo
    """

    def decorator(cls: type[T]) -> type[T]:
        """Apply component decoration to the class."""
        try:
            # Validate decorator target
            validate_decorator_target(cls, "og_component")

            # Create component options
            options = ComponentOptions(
                interface=interface,
                scope=scope,
                layer=layer or detect_component_layer(cls),
                context_name=context_name,
                component_name=component_name,
                provider_name=provider_name,
                tags=tags or {},
                auto_register=auto_register,
                lazy_init=lazy_init,
                factory=factory,
            )

            # Enhance tags with auto-detected information
            enhanced_tags = enhance_component_tags(cls, options.get_tags_dict())

            # Add component metadata to the class
            cls._og_component_options = options  # type: ignore[attr-defined]
            cls._og_component_metadata = create_metadata_dict(  # type: ignore[attr-defined]
                component_type=cls.__name__,
                scope=options.scope.value,
                layer=options.layer.value if options.layer else None,
                context_name=options.context_name,
                auto_register=options.auto_register,
                lazy_init=options.lazy_init,
                decorated_at=__name__,
            )
            cls._og_enhanced_tags = enhanced_tags  # type: ignore[attr-defined]

            # Log decorator application
            decorator_sig = get_decorator_signature(
                "og_component",
                scope=options.scope.value,
                layer=options.layer.value if options.layer else None,
                context=options.context_name,
                auto_register=options.auto_register,
            )
            logger.debug(
                "Applied component decorator",
                class_name=cls.__name__,
                module=cls.__module__,
                decorator_signature=decorator_sig,
            )

            # Auto-register if enabled
            if options.auto_register:
                _register_component(cls, options, enhanced_tags)

            # Emit component decoration event
            emit_event(
                EventHook.COMPONENT_REGISTERED,
                {
                    "class_name": cls.__name__,
                    "module": cls.__module__,
                    "scope": options.scope.value,
                    "layer": options.layer.value if options.layer else None,
                    "context_name": options.context_name,
                    "auto_register": options.auto_register,
                    "tags": enhanced_tags,
                    "decorated_with": "og_component",
                },
            )

            return cls

        except Exception as e:
            log_error(
                "og_component_decorator",
                e,
                component_type=cls,
            )
            # Re-raise to prevent silent failures
            raise

    return decorator


def _register_component(
    cls: type,
    options: ComponentOptions,
    enhanced_tags: dict[str, str],
) -> None:
    """
    Register a component in the appropriate context.

    Args:
        cls: The component class
        options: Component options
        enhanced_tags: Enhanced tags dictionary
    """
    try:
        # For now, only support global context registration
        # This can be extended to support named contexts
        if options.context_name != "global":
            logger.warning(
                "Non-global context registration not yet implemented",
                class_name=cls.__name__,
                context_name=options.context_name,
            )
            return

        # Get the global context
        context = get_global_context()

        # Determine interface and implementation
        interface = options.interface or cls
        implementation = cls

        # Register the component
        context.register_component(
            interface=interface,
            implementation=implementation,
            scope=options.scope,
            name=options.get_provider_name(cls.__name__),
            tags=enhanced_tags,
            factory=options.factory,
        )

        logger.debug(
            "Auto-registered component",
            class_name=cls.__name__,
            interface=interface.__name__,
            scope=options.scope.value,
            context=options.context_name,
            provider_name=options.get_provider_name(cls.__name__),
        )

    except Exception as e:
        log_error(
            "auto_register_component",
            e,
            context_name=options.context_name,
            component_type=cls,
        )
        # Log the error but don't fail the decoration
        logger.warning(
            "Failed to auto-register component, continuing with decoration",
            class_name=cls.__name__,
            error=str(e),
        )


def get_component_options(cls: type) -> ComponentOptions | None:
    """
    Get component options from a decorated class.

    Args:
        cls: The decorated class

    Returns:
        Component options or None if not decorated
    """
    return getattr(cls, "_og_component_options", None)


def get_component_metadata(cls: type) -> dict[str, Any] | None:
    """
    Get component metadata from a decorated class.

    Args:
        cls: The decorated class

    Returns:
        Component metadata or None if not decorated
    """
    return getattr(cls, "_og_component_metadata", None)


def get_enhanced_tags(cls: type) -> dict[str, str] | None:
    """
    Get enhanced tags from a decorated class.

    Args:
        cls: The decorated class

    Returns:
        Enhanced tags or None if not decorated
    """
    return getattr(cls, "_og_enhanced_tags", None)


def is_og_component(cls: type) -> bool:
    """
    Check if a class is decorated with @og_component.

    Args:
        cls: The class to check

    Returns:
        True if the class is decorated with @og_component
    """
    return hasattr(cls, "_og_component_options")


def register_component_manually(
    cls: type,
    context_name: str = "global",
    **override_options: Any,
) -> None:
    """
    Manually register a component that was decorated but not auto-registered.

    Args:
        cls: The component class
        context_name: Context to register in
        **override_options: Options to override from the decorator
    """
    if not is_og_component(cls):
        raise ValueError(f"Class {cls.__name__} is not decorated with @og_component")

    options = get_component_options(cls)
    if not options:
        raise ValueError(f"No component options found for {cls.__name__}")

    # Override options with provided values
    for key, value in override_options.items():
        if hasattr(options, key):
            setattr(options, key, value)

    # Override context name
    options.context_name = context_name

    # Get enhanced tags
    enhanced_tags = get_enhanced_tags(cls) or {}

    # Register the component
    _register_component(cls, options, enhanced_tags)
