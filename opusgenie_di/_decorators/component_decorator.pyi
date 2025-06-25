from .._base import ComponentLayer as ComponentLayer, ComponentScope as ComponentScope
from .._core import get_global_context as get_global_context
from .._hooks import EventHook as EventHook, emit_event as emit_event
from .._utils import get_logger as get_logger, log_error as log_error
from .decorator_options import ComponentOptions as ComponentOptions
from .decorator_utils import create_metadata_dict as create_metadata_dict, detect_component_layer as detect_component_layer, enhance_component_tags as enhance_component_tags, get_decorator_signature as get_decorator_signature, validate_decorator_target as validate_decorator_target
from _typeshed import Incomplete
from collections.abc import Callable as Callable
from typing import Any, TypeVar

T = TypeVar('T')
logger: Incomplete

def og_component(interface: type | None = None, *, scope: ComponentScope = ..., layer: ComponentLayer | None = None, context_name: str = 'global', component_name: str | None = None, provider_name: str | None = None, tags: dict[str, Any] | None = None, auto_register: bool = True, lazy_init: bool = False, factory: Any = None) -> Callable[[type[T]], type[T]]:
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
def _register_component(cls, options: ComponentOptions, enhanced_tags: dict[str, str]) -> None:
    """
    Register a component in the appropriate context.

    Args:
        cls: The component class
        options: Component options
        enhanced_tags: Enhanced tags dictionary
    """
def get_component_options(cls) -> ComponentOptions | None:
    """
    Get component options from a decorated class.

    Args:
        cls: The decorated class

    Returns:
        Component options or None if not decorated
    """
def get_component_metadata(cls) -> dict[str, Any] | None:
    """
    Get component metadata from a decorated class.

    Args:
        cls: The decorated class

    Returns:
        Component metadata or None if not decorated
    """
def get_enhanced_tags(cls) -> dict[str, str] | None:
    """
    Get enhanced tags from a decorated class.

    Args:
        cls: The decorated class

    Returns:
        Enhanced tags or None if not decorated
    """
def is_og_component(cls) -> bool:
    """
    Check if a class is decorated with @og_component.

    Args:
        cls: The class to check

    Returns:
        True if the class is decorated with @og_component
    """
def register_component_manually(cls, context_name: str = 'global', **override_options: Any) -> None:
    """
    Manually register a component that was decorated but not auto-registered.

    Args:
        cls: The component class
        context_name: Context to register in
        **override_options: Options to override from the decorator
    """
