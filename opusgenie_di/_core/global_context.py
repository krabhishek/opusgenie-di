"""Global context singleton for dependency injection."""

from threading import RLock
from typing import Any

from .._base import ComponentScope
from .._utils import get_logger
from .context_impl import Context

logger = get_logger(__name__)


class GlobalContext(Context):
    """
    Global dependency injection context.

    The global context provides a singleton context that's always available
    for dependency injection. It serves as the default context for component
    registration and resolution, enabling simple DI scenarios while
    maintaining compatibility with multi-context applications.
    """

    _instance: "GlobalContext | None" = None
    _lock = RLock()

    def __new__(cls) -> "GlobalContext":
        """Ensure singleton behavior for global context."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize global context (only once due to singleton)."""
        if hasattr(self, "_initialized"):
            return

        super().__init__(name="global", parent=None, auto_wire=True)

        self._initialized = True
        self._framework_components_registered = False

        logger.info(
            "Initialized global dependency injection context",
            context_name=self.name,
        )

    def register_framework_components(self) -> None:
        """
        Register core framework components in the global context.

        This method can be extended to register common framework
        components that should be available by default.
        """
        if self._framework_components_registered:
            return

        try:
            # Framework components can be registered here
            # For example, logging, configuration, etc.
            # This is left empty for now as the package is framework-agnostic

            self._framework_components_registered = True

            logger.info(
                "Registered framework components in global context",
                context_name=self.name,
                components=[],  # Will be populated when components are added
            )

        except Exception as e:
            logger.error(
                "Failed to register framework components",
                context_name=self.name,
                error=str(e),
            )
            raise

    def reset(self) -> None:
        """
        Reset the global context to initial state.

        This is primarily useful for testing scenarios where you need
        to reset the global state between tests.
        """
        with self._lock:
            # Clear the underlying container
            self._container.clear()

            # Clear import manager
            self._import_manager.clear_imports()

            # Reset framework registration flag
            self._framework_components_registered = False

            logger.info(
                "Reset global context to initial state",
                context_name=self.name,
            )

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of the global context state.

        Returns:
            Dictionary containing context summary information
        """
        summary = super().get_summary()
        summary.update(
            {
                "framework_components_registered": self._framework_components_registered,
                "is_global": True,
            }
        )
        return summary


# Global context instance management
_global_context: "GlobalContext | None" = None
_global_context_lock = RLock()


def get_global_context() -> GlobalContext:
    """
    Get the global dependency injection context.

    Returns:
        The singleton global context instance
    """
    global _global_context

    if _global_context is None:
        with _global_context_lock:
            if _global_context is None:
                _global_context = GlobalContext()
                _global_context.register_framework_components()

    return _global_context


def register_global_component(
    interface: type,
    implementation: type | None = None,
    *,
    scope: ComponentScope = ComponentScope.SINGLETON,
    name: str | None = None,
    tags: dict[str, Any] | None = None,
) -> None:
    """
    Register a component in the global context.

    Args:
        interface: Interface type to register
        implementation: Implementation type (defaults to interface)
        scope: Component lifecycle scope
        name: Optional component name
        tags: Optional component tags
    """
    context = get_global_context()
    context.register_component(
        interface=interface,
        implementation=implementation,
        scope=scope,
        name=name,
        tags=tags,
    )

    logger.debug(
        "Registered component in global context",
        interface=interface.__name__,
        implementation=(implementation or interface).__name__,
        scope=scope.value,
        name=name,
    )


def resolve_global_component[TInterface](
    interface: type[TInterface], name: str | None = None
) -> TInterface:
    """
    Resolve a component from the global context.

    Args:
        interface: Interface type to resolve
        name: Optional component name

    Returns:
        Component instance implementing the interface
    """
    context = get_global_context()
    instance: TInterface = context.resolve(interface, name)

    logger.debug(
        "Resolved component from global context",
        interface=interface.__name__,
        name=name,
        instance_type=type(instance).__name__,
    )

    return instance


async def resolve_global_component_async[TInterface](
    interface: type[TInterface], name: str | None = None
) -> TInterface:
    """
    Asynchronously resolve a component from the global context.

    Args:
        interface: Interface type to resolve
        name: Optional component name

    Returns:
        Component instance implementing the interface
    """
    context = get_global_context()
    instance: TInterface = await context.resolve_async(interface, name)

    logger.debug(
        "Resolved component asynchronously from global context",
        interface=interface.__name__,
        name=name,
        instance_type=type(instance).__name__,
    )

    return instance


def reset_global_context() -> None:
    """
    Reset the global context to initial state.

    This is primarily useful for testing scenarios where you need
    to reset the global state between tests.
    """
    global _global_context

    with _global_context_lock:
        if _global_context is not None:
            _global_context.reset()
            # Set to None to mark as uninitialized
            _global_context = None
            # Also reset the class-level singleton instance
            GlobalContext._instance = None
            logger.info("Reset global dependency injection context")


def get_global_context_summary() -> dict[str, Any]:
    """
    Get a summary of the global context state.

    Returns:
        Dictionary containing global context summary
    """
    if _global_context is None:
        return {"initialized": False}

    summary = _global_context.get_summary()
    summary["initialized"] = True
    return summary


def is_global_context_initialized() -> bool:
    """
    Check if the global context has been initialized.

    Returns:
        True if the global context is initialized
    """
    return _global_context is not None
