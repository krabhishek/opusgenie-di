from .._base import ComponentScope as ComponentScope
from .._utils import get_logger as get_logger
from .context_impl import Context as Context
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class GlobalContext(Context):
    """
    Global dependency injection context.

    The global context provides a singleton context that's always available
    for dependency injection. It serves as the default context for component
    registration and resolution, enabling simple DI scenarios while
    maintaining compatibility with multi-context applications.
    """
    _instance: GlobalContext | None
    _lock: Incomplete
    def __new__(cls) -> GlobalContext:
        """Ensure singleton behavior for global context."""
    _initialized: bool
    _framework_components_registered: bool
    def __init__(self) -> None:
        """Initialize global context (only once due to singleton)."""
    def register_framework_components(self) -> None:
        """
        Register core framework components in the global context.

        This method can be extended to register common framework
        components that should be available by default.
        """
    def reset(self) -> None:
        """
        Reset the global context to initial state.

        This is primarily useful for testing scenarios where you need
        to reset the global state between tests.
        """
    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of the global context state.

        Returns:
            Dictionary containing context summary information
        """

_global_context: GlobalContext | None
_global_context_lock: Incomplete

def get_global_context() -> GlobalContext:
    """
    Get the global dependency injection context.

    Returns:
        The singleton global context instance
    """
def register_global_component(interface: type, implementation: type | None = None, *, scope: ComponentScope = ..., name: str | None = None, tags: dict[str, Any] | None = None, factory: Any = None) -> None:
    """
    Register a component in the global context.

    Args:
        interface: Interface type to register
        implementation: Implementation type (defaults to interface)
        scope: Component lifecycle scope
        name: Optional component name
        tags: Optional component tags
        factory: Optional factory function for component instantiation
    """
def resolve_global_component[TInterface](interface: type[TInterface], name: str | None = None) -> TInterface:
    """
    Resolve a component from the global context.

    Args:
        interface: Interface type to resolve
        name: Optional component name

    Returns:
        Component instance implementing the interface
    """
async def resolve_global_component_async[TInterface](interface: type[TInterface], name: str | None = None) -> TInterface:
    """
    Asynchronously resolve a component from the global context.

    Args:
        interface: Interface type to resolve
        name: Optional component name

    Returns:
        Component instance implementing the interface
    """
def reset_global_context() -> None:
    """
    Reset the global context to initial state.

    This is primarily useful for testing scenarios where you need
    to reset the global state between tests.
    """
def get_global_context_summary() -> dict[str, Any]:
    """
    Get a summary of the global context state.

    Returns:
        Dictionary containing global context summary
    """
def is_global_context_initialized() -> bool:
    """
    Check if the global context has been initialized.

    Returns:
        True if the global context is initialized
    """
