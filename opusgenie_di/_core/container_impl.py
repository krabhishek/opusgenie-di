"""Container implementation wrapping dependency-injector."""

import threading
from threading import RLock
import time
from typing import Any, TypeVar, cast

from dependency_injector import containers, providers

from .._base import ComponentMetadata, ComponentScope
from .._base.protocols import ComponentMetadataProtocol
from .._utils import (
    get_constructor_dependencies,
    get_logger,
    log_component_registration,
    log_component_resolution,
    log_error,
    validate_component_registration,
)
from .container_interface import ContainerInterface
from .exceptions import (
    CircularDependencyError,
    ComponentRegistrationError,
    ComponentResolutionError,
)
from .scope_impl import ScopeManager

T = TypeVar("T")
TInterface = TypeVar("TInterface")
TImplementation = TypeVar("TImplementation")

logger = get_logger(__name__)

# Thread-local storage for tracking resolution chains to detect circular dependencies
_resolution_chain = threading.local()


def _get_resolution_chain() -> list[str]:
    """Get the current resolution chain for this thread."""
    if not hasattr(_resolution_chain, "chain"):
        _resolution_chain.chain = []
    return _resolution_chain.chain  # type: ignore[no-any-return]


def _push_resolution(component_name: str) -> None:
    """Add a component to the resolution chain."""
    chain = _get_resolution_chain()
    chain.append(component_name)


def _pop_resolution() -> None:
    """Remove the last component from the resolution chain."""
    chain = _get_resolution_chain()
    if chain:
        chain.pop()


def _check_circular_dependency(component_name: str, context_name: str) -> None:
    """Check if adding this component would create a circular dependency."""
    chain = _get_resolution_chain()
    if component_name in chain:
        # Found circular dependency
        circular_chain = chain + [component_name]
        raise CircularDependencyError(
            f"Circular dependency detected for component '{component_name}'",
            dependency_chain=circular_chain,
            context_name=context_name,
        )


class Container(ContainerInterface[T]):
    """
    Container implementation wrapping dependency-injector containers.

    Provides Angular-like DI functionality by wrapping dependency-injector
    containers with structured logging, metadata management, and
    multi-context support.
    """

    def __init__(self, name: str = "default", context_ref: Any = None) -> None:
        """
        Initialize the container.

        Args:
            name: Name of the container for identification
            context_ref: Optional reference to the parent context for cross-context resolution
        """
        self._name = name
        self._context_ref = context_ref  # Weak reference to avoid circular dependencies
        self._lock = RLock()
        self._scope_manager = ScopeManager()

        # Create underlying dependency-injector container
        self._container = containers.DynamicContainer()

        # Track metadata for registered components
        self._component_metadata: dict[str, ComponentMetadata] = {}
        self._registered_types: dict[str, type] = {}  # Track actual type objects
        self._registration_count = 0

        logger.debug("Created container", container_name=name)

    @property
    def name(self) -> str:
        """Get the container name."""
        return self._name

    def register(
        self,
        interface: type[TInterface],
        implementation: type[TImplementation] | None = None,
        *,
        scope: ComponentScope = ComponentScope.SINGLETON,
        name: str | None = None,
        tags: dict[str, Any] | None = None,
        factory: Any = None,
    ) -> None:
        """
        Register a component implementation for an interface.

        Args:
            interface: Interface type to register
            implementation: Implementation type (defaults to interface)
            scope: Component lifecycle scope
            name: Optional component name
            tags: Optional component tags
            factory: Optional factory function for creating instances
        """
        try:
            with self._lock:
                impl_class = implementation or interface
                provider_name = name or interface.__name__

                # Validate registration
                validate_component_registration(interface, impl_class, provider_name)

                # Create a factory function for auto-wiring if needed
                if not factory:
                    dependencies = get_constructor_dependencies(impl_class)
                    if dependencies and self._context_ref:
                        # Create a factory function that resolves dependencies
                        factory = self._create_auto_wiring_factory(
                            impl_class, dependencies
                        )

                # Create appropriate dependency-injector provider based on scope
                provider: (
                    providers.Singleton[Any]
                    | providers.Factory[Any]
                    | providers.Resource[Any]
                )

                if scope == ComponentScope.SINGLETON:
                    if factory:
                        provider = providers.Singleton(factory)
                    else:
                        provider = providers.Singleton(impl_class)
                elif scope == ComponentScope.TRANSIENT:
                    if factory:
                        provider = providers.Factory(factory)
                    else:
                        provider = providers.Factory(impl_class)
                elif scope == ComponentScope.SCOPED:
                    if factory:
                        provider = providers.Resource(factory)
                    else:
                        provider = providers.Resource(impl_class)
                elif scope == ComponentScope.FACTORY:
                    if not factory:
                        factory = impl_class
                    provider = providers.Factory(factory)
                else:
                    raise ComponentRegistrationError(
                        f"Unsupported scope: {scope}",
                        component_type=impl_class.__name__,
                        interface_type=interface.__name__,
                        details=f"Scope {scope.value} is not supported",
                    )

                # Register in dependency-injector container
                self._container.set_provider(provider_name, provider)

                # Create and store metadata
                dependencies = get_constructor_dependencies(impl_class)
                metadata = ComponentMetadata(
                    component_type=impl_class.__name__,
                    component_name=provider_name,
                    scope=scope,
                    tags=tags or {},
                    dependencies=list(dependencies.keys()),
                    context_name=self._name,
                    provider_name=provider_name,
                )

                self._component_metadata[provider_name] = metadata
                self._registered_types[provider_name] = (
                    interface  # Track the actual type
                )
                self._registration_count += 1

                log_component_registration(
                    impl_class,
                    self._name,
                    scope.value,
                    provider_name,
                    interface=interface.__name__,
                    registration_id=self._registration_count,
                )

        except Exception as e:
            log_error(
                "register_component",
                e,
                context_name=self._name,
                component_type=implementation or interface,
            )
            if isinstance(e, ComponentRegistrationError):
                raise
            raise ComponentRegistrationError(
                f"Failed to register component {interface.__name__}",
                component_type=(implementation or interface).__name__,
                interface_type=interface.__name__,
                details=str(e),
            ) from e

    def register_provider(
        self,
        interface: type[TInterface],
        provider: Any,  # ComponentProviderProtocol[TInterface]
        *,
        name: str | None = None,
        tags: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a component provider for an interface.

        Args:
            interface: Interface type to register
            provider: Provider instance for the interface
            name: Optional component name
            tags: Optional component tags
        """
        try:
            with self._lock:
                provider_name = name or interface.__name__

                # Wrap the provider in a dependency-injector factory
                di_provider: providers.Factory[Any] = providers.Factory(
                    provider.provide
                )
                self._container.set_provider(provider_name, di_provider)

                # Create metadata
                metadata = ComponentMetadata(
                    component_type=interface.__name__,
                    component_name=provider_name,
                    scope=provider.get_scope()
                    if hasattr(provider, "get_scope")
                    else ComponentScope.SINGLETON,
                    tags=tags or {},
                    context_name=self._name,
                    provider_name=provider_name,
                )

                self._component_metadata[provider_name] = metadata
                self._registered_types[provider_name] = (
                    interface  # Track the actual type
                )
                self._registration_count += 1

                log_component_registration(
                    interface,
                    self._name,
                    metadata.scope.value,
                    provider_name,
                    provider_type="custom",
                )

        except Exception as e:
            log_error(
                "register_provider",
                e,
                context_name=self._name,
                component_type=interface,
            )
            raise ComponentRegistrationError(
                f"Failed to register provider for {interface.__name__}",
                component_type=interface.__name__,
                interface_type=interface.__name__,
                details=str(e),
            ) from e

    def resolve(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface:
        """
        Resolve a component instance for an interface.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance implementing the interface
        """
        start_time = time.time()
        provider_name = name or interface.__name__

        # Check for circular dependencies before starting resolution
        _check_circular_dependency(provider_name, self._name)

        # Add to resolution chain
        _push_resolution(provider_name)

        try:
            with self._lock:
                # Check if provider exists
                if provider_name not in self._container.providers:
                    raise ComponentResolutionError(
                        f"No registration found for interface '{interface.__name__}'",
                        component_type=interface.__name__,
                        details=f"Component '{provider_name}' not registered in container '{self._name}'",
                    )

                # Resolve from dependency-injector container
                instance = self._container.providers[provider_name]()

                resolution_time_ms = (time.time() - start_time) * 1000

                log_component_resolution(
                    interface,
                    self._name,
                    resolution_time_ms,
                    resolution_source="direct",
                    provider_name=provider_name,
                    instance_id=getattr(instance, "component_id", None),
                )

                return instance  # type: ignore[no-any-return]

        except (ComponentResolutionError, CircularDependencyError):
            raise
        except Exception as e:
            log_error(
                "resolve_component",
                e,
                context_name=self._name,
                component_type=interface,
            )
            raise ComponentResolutionError(
                f"Failed to resolve component {interface.__name__}",
                component_type=interface.__name__,
                details=str(e),
            ) from e
        finally:
            # Always remove from resolution chain when done
            _pop_resolution()

    async def resolve_async(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface:
        """
        Asynchronously resolve a component instance for an interface.

        Args:
            interface: Interface type to resolve
            name: Optional component name

        Returns:
            Component instance implementing the interface
        """
        # For now, delegate to sync resolution
        # Could be enhanced to support actual async providers
        return self.resolve(interface, name)

    def is_registered(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool:
        """
        Check if an interface is registered in the container.

        Args:
            interface: Interface type to check
            name: Optional component name

        Returns:
            True if the interface is registered
        """
        provider_name = name or interface.__name__
        with self._lock:
            return provider_name in self._container.providers

    def get_metadata(
        self, interface: type[TInterface], name: str | None = None
    ) -> ComponentMetadataProtocol:
        """
        Get metadata for a registered component.

        Args:
            interface: Interface type
            name: Optional component name

        Returns:
            ComponentMetadata for the component
        """
        provider_name = name or interface.__name__
        with self._lock:
            if provider_name not in self._component_metadata:
                raise ComponentResolutionError(
                    f"No metadata found for component '{interface.__name__}'",
                    component_type=interface.__name__,
                    details=f"Component '{provider_name}' not registered",
                )
            return cast(
                ComponentMetadataProtocol, self._component_metadata[provider_name]
            )

    def unregister(self, interface: type[TInterface], name: str | None = None) -> bool:
        """
        Unregister a component from the container.

        Args:
            interface: Interface type to unregister
            name: Optional component name

        Returns:
            True if the component was unregistered, False if it wasn't registered
        """
        provider_name = name or interface.__name__
        with self._lock:
            if provider_name not in self._container.providers:
                return False

            # Remove from dependency-injector container
            del self._container.providers[provider_name]

            # Remove metadata and registered type
            if provider_name in self._component_metadata:
                del self._component_metadata[provider_name]
            if provider_name in self._registered_types:
                del self._registered_types[provider_name]

            logger.debug(
                "Unregistered component",
                component=interface.__name__,
                container=self._name,
                provider_name=provider_name,
            )
            return True

    def clear(self) -> None:
        """Clear all registrations from the container."""
        with self._lock:
            # Clear dependency-injector container
            self._container.reset_singletons()
            self._container.providers.clear()

            # Clear metadata and registered types
            self._component_metadata.clear()
            self._registered_types.clear()
            self._registration_count = 0

            # Clear scope manager
            self._scope_manager.clear_all()

            logger.debug("Cleared all registrations", container=self._name)

    def get_registered_types(self) -> list[type]:
        """Get a list of all registered interface types."""
        with self._lock:
            return list(self._registered_types.values())

    def get_registration_count(self) -> int:
        """Get the number of registered components."""
        with self._lock:
            return len(self._container.providers)

    def wire_modules(self, modules: list[str] | None = None) -> None:
        """
        Wire the container for automatic dependency injection.

        Args:
            modules: Optional list of module names to wire
        """
        try:
            if modules:
                self._container.wire(modules=modules)
            else:
                # Enable automatic dependency injection by calling wire without modules
                # This allows the dependency resolution we configured during registration to work
                pass  # The providers are already configured with dependencies

            logger.debug(
                "Wired container for automatic injection",
                container=self._name,
                modules=modules,
                auto_wired=not modules,
            )

        except Exception as e:
            log_error(
                "wire_container",
                e,
                context_name=self._name,
            )
            raise ComponentRegistrationError(
                f"Failed to wire container '{self._name}'",
                details=str(e),
            ) from e

    def shutdown(self) -> None:
        """Shutdown the container and cleanup resources."""
        with self._lock:
            try:
                # Shutdown resources using dependency-injector capabilities
                if hasattr(self._container, "shutdown_resources"):
                    self._container.shutdown_resources()

                # Clear scope manager
                self._scope_manager.clear_all()

                # Clear metadata and registered types
                self._component_metadata.clear()
                self._registered_types.clear()
                self._registration_count = 0

                logger.debug("Shutdown container", container=self._name)

            except Exception as e:
                log_error(
                    "shutdown_container",
                    e,
                    context_name=self._name,
                )
                raise ComponentRegistrationError(
                    f"Failed to shutdown container '{self._name}'",
                    details=str(e),
                ) from e

    def enable_auto_wiring(self) -> None:
        """
        Enable automatic dependency injection for this container.

        This method should be called after all components are registered
        to enable automatic dependency resolution.
        """
        try:
            with self._lock:
                # The providers are already configured with Dependency() providers
                # during registration, so they will automatically resolve dependencies
                # when components are instantiated
                logger.debug(
                    "Enabled automatic dependency injection",
                    container=self._name,
                    provider_count=len(self._container.providers),
                )

        except Exception as e:
            log_error(
                "enable_auto_wiring",
                e,
                context_name=self._name,
            )
            raise ComponentRegistrationError(
                f"Failed to enable auto-wiring for container '{self._name}'",
                details=str(e),
            ) from e

    def _should_inject_dependency(self, dependency_type: type) -> bool:
        """
        Determine if a dependency should be auto-injected.

        Args:
            dependency_type: The type of the dependency

        Returns:
            True if the dependency should be auto-injected
        """
        # Don't inject primitive types or built-in types
        if dependency_type in (str, int, float, bool, bytes, type(None)):
            return False

        # Don't inject standard library types that are typically not DI components
        module_name = getattr(dependency_type, "__module__", "")
        if module_name in ("builtins", "typing", "collections", "datetime", "pathlib"):
            return False

        # Check if the dependency is registered in this container
        provider_name = dependency_type.__name__
        if provider_name in self._container.providers:
            return True

        # Check if the dependency can be resolved through imports (if context is available)
        if self._context_ref:
            try:
                # Check if the dependency can be resolved through imports
                for import_decl in self._context_ref._import_manager.get_imports():
                    if import_decl.component_type == dependency_type:
                        return True
            except Exception:
                # If there's any issue checking imports, don't inject
                pass

        return False

    def _create_dependency_provider(self, dependency_type: type) -> Any:
        """
        Create a provider for automatic dependency injection.

        Args:
            dependency_type: The type of dependency to inject

        Returns:
            A provider that can resolve the dependency
        """
        provider_name = dependency_type.__name__

        # If it's registered locally, use a direct Dependency provider
        if provider_name in self._container.providers:
            return providers.Dependency()

        # If it can be resolved through context imports, create a custom provider
        if self._context_ref:

            def resolve_from_context() -> Any:
                try:
                    return self._context_ref.resolve(dependency_type)
                except Exception as e:
                    logger.warning(
                        "Failed to resolve dependency from context",
                        dependency_type=dependency_type.__name__,
                        context=self._name,
                        error=str(e),
                    )
                    raise

            return providers.Callable(resolve_from_context)

        return None

    def _create_auto_wiring_factory(
        self, impl_class: type, dependencies: dict[str, tuple[type | None, bool]]
    ) -> Any:
        """
        Create a factory function that automatically resolves and injects dependencies.

        Args:
            impl_class: The implementation class to create instances of
            dependencies: Dictionary of dependencies (param_name -> (type, is_optional))

        Returns:
            Factory function that creates instances with auto-injected dependencies
        """

        def create_instance_with_dependencies() -> Any:
            kwargs = {}

            # Check if auto-wiring is enabled in the context
            auto_wire_enabled = (
                getattr(self._context_ref, "_auto_wire", True)
                if self._context_ref
                else True
            )

            if auto_wire_enabled:
                for param_name, (param_type, is_optional) in dependencies.items():
                    if param_type and self._should_inject_dependency(param_type):
                        try:
                            # Resolve dependency from context (includes imports)
                            # The context's resolve method will handle circular dependency detection
                            kwargs[param_name] = self._context_ref.resolve(param_type)
                            logger.debug(
                                "Auto-injected dependency",
                                component=impl_class.__name__,
                                parameter=param_name,
                                dependency_type=param_type.__name__,
                            )
                        except (CircularDependencyError, ComponentResolutionError):
                            # Re-raise DI-specific exceptions without modification
                            raise
                        except Exception as e:
                            if not is_optional:
                                logger.error(
                                    "Failed to resolve required dependency",
                                    component=impl_class.__name__,
                                    dependency=param_type.__name__,
                                    error=str(e),
                                )
                                raise
                            logger.debug(
                                "Failed to resolve optional dependency, skipping",
                                component=impl_class.__name__,
                                dependency=param_type.__name__,
                                error=str(e),
                            )

            logger.debug(
                "Creating instance with auto-injected dependencies",
                component=impl_class.__name__,
                injected_dependencies=list(kwargs.keys()),
                auto_wire_enabled=auto_wire_enabled,
            )
            return impl_class(**kwargs)

        return create_instance_with_dependencies

    def __repr__(self) -> str:
        """Get string representation of the container."""
        with self._lock:
            return (
                f"Container(name='{self._name}', "
                f"registrations={len(self._container.providers)})"
            )
