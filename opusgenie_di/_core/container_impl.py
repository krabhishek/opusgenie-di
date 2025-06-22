"""Container implementation wrapping dependency-injector."""

import time
from threading import RLock
from typing import Any, TypeVar

from dependency_injector import containers, providers

from .._base import ComponentMetadata, ComponentScope
from .._utils import (
    get_constructor_dependencies,
    get_logger,
    log_component_registration,
    log_component_resolution,
    log_error,
    validate_component_registration,
)
from .container_interface import ContainerInterface
from .exceptions import ComponentRegistrationError, ComponentResolutionError
from .scope_impl import ScopeManager

T = TypeVar("T")
TInterface = TypeVar("TInterface")
TImplementation = TypeVar("TImplementation")

logger = get_logger(__name__)


class Container(ContainerInterface[T]):
    """
    Container implementation wrapping dependency-injector containers.

    Provides Angular-like DI functionality by wrapping dependency-injector
    containers with structured logging, metadata management, and
    multi-context support.
    """

    def __init__(self, name: str = "default") -> None:
        """
        Initialize the container.

        Args:
            name: Name of the container for identification
        """
        self._name = name
        self._lock = RLock()
        self._scope_manager = ScopeManager()

        # Create underlying dependency-injector container
        self._container = containers.DynamicContainer()

        # Track metadata for registered components
        self._component_metadata: dict[str, ComponentMetadata] = {}
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

                # Create appropriate dependency-injector provider based on scope
                provider: providers.Singleton | providers.Factory | providers.Resource

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
                di_provider = providers.Factory(provider.provide)
                self._container.set_provider(provider_name, di_provider)

                # Create metadata
                metadata = ComponentMetadata(
                    component_type=interface.__name__,
                    component_name=provider_name,
                    scope=provider.get_scope() if hasattr(provider, "get_scope") else ComponentScope.SINGLETON,
                    tags=tags or {},
                    context_name=self._name,
                    provider_name=provider_name,
                )

                self._component_metadata[provider_name] = metadata
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

                return instance

        except ComponentResolutionError:
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
    ) -> ComponentMetadata:
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
            return self._component_metadata[provider_name]

    def unregister(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool:
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

            # Remove metadata
            if provider_name in self._component_metadata:
                del self._component_metadata[provider_name]

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

            # Clear metadata
            self._component_metadata.clear()
            self._registration_count = 0

            # Clear scope manager
            self._scope_manager.clear_all()

            logger.debug("Cleared all registrations", container=self._name)

    def get_registered_types(self) -> list[type]:
        """Get a list of all registered interface types."""
        with self._lock:
            # This is a simplified implementation - in a real scenario,
            # we'd need to track the actual types
            return list(self._container.providers.keys())

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
                # Wire current module by default
                self._container.wire(modules=[__name__])

            logger.debug(
                "Wired container for automatic injection",
                container=self._name,
                modules=modules,
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

                # Clear metadata
                self._component_metadata.clear()
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

    def __repr__(self) -> str:
        """Get string representation of the container."""
        with self._lock:
            return (
                f"Container(name='{self._name}', "
                f"registrations={len(self._container.providers)})"
            )