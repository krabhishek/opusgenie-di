"""Provider configuration for module system."""

from typing import Any

from pydantic import BaseModel, Field

from .._base import ComponentScope
from .._utils import get_logger, validate_component_registration

logger = get_logger(__name__)


class ProviderConfig(BaseModel):
    """
    Configuration for a provider in a module.

    Defines how a component should be provided within a module context,
    including its interface, implementation, scope, and other metadata.
    """

    interface: type = Field(description="Interface type this provider implements")
    implementation: type | None = Field(
        default=None, description="Implementation type (defaults to interface)"
    )
    scope: ComponentScope = Field(
        default=ComponentScope.SINGLETON, description="Component lifecycle scope"
    )
    name: str | None = Field(default=None, description="Optional provider name")
    factory: Any = Field(default=None, description="Optional factory function")
    tags: dict[str, str] = Field(default_factory=dict, description="Provider tags")
    conditional: Any = Field(
        default=None, description="Optional condition for provider activation"
    )

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context: Any, /) -> None:
        """Validate provider configuration after initialization."""
        impl = self.implementation or self.interface

        # Validate the registration
        validate_component_registration(
            self.interface,
            impl,
            self.get_provider_name(),
        )

    def get_implementation(self) -> type:
        """Get the implementation type (defaults to interface if not specified)."""
        return self.implementation or self.interface

    def get_provider_name(self) -> str:
        """Get the provider name (defaults to interface name if not specified)."""
        return self.name or self.interface.__name__

    def to_registration_args(self) -> dict[str, Any]:
        """Convert to arguments suitable for context.register_component()."""
        return {
            "interface": self.interface,
            "implementation": self.get_implementation(),
            "scope": self.scope,
            "name": self.name,
            "tags": self.tags,
            "factory": self.factory,
        }

    def is_conditional(self) -> bool:
        """Check if this provider has a condition."""
        return self.conditional is not None

    def evaluate_condition(self) -> bool:
        """
        Evaluate the provider condition.

        Returns:
            True if the provider should be registered
        """
        if not self.is_conditional():
            return True

        try:
            if callable(self.conditional):
                return bool(self.conditional())
            return bool(self.conditional)
        except Exception as e:
            logger.warning(
                "Error evaluating provider condition",
                provider=self.get_provider_name(),
                error=str(e),
            )
            return False

    def __repr__(self) -> str:
        impl = self.get_implementation()
        return (
            f"ProviderConfig(interface={self.interface.__name__}, "
            f"implementation={impl.__name__}, scope={self.scope.value})"
        )


class ProviderCollection(BaseModel):
    """Collection of provider configurations with validation and utilities."""

    providers: list[ProviderConfig] = Field(
        default_factory=list, description="List of provider configurations"
    )

    def add_provider(self, provider: ProviderConfig) -> None:
        """Add a provider configuration to the collection."""
        # Check for duplicates by provider name
        provider_name = provider.get_provider_name()
        for existing in self.providers:
            if existing.get_provider_name() == provider_name:
                logger.warning(
                    "Duplicate provider configuration",
                    provider_name=provider_name,
                    interface=provider.interface.__name__,
                )
                return

        self.providers.append(provider)
        logger.debug(
            "Added provider configuration",
            provider_name=provider_name,
            interface=provider.interface.__name__,
            implementation=provider.get_implementation().__name__,
            scope=provider.scope.value,
        )

    def get_provider_by_name(self, name: str) -> ProviderConfig | None:
        """Get a provider by name."""
        for provider in self.providers:
            if provider.get_provider_name() == name:
                return provider
        return None

    def get_provider_by_interface(self, interface: type) -> ProviderConfig | None:
        """Get a provider by interface type."""
        for provider in self.providers:
            if provider.interface == interface:
                return provider
        return None

    def get_providers_by_scope(self, scope: ComponentScope) -> list[ProviderConfig]:
        """Get all providers with a specific scope."""
        return [p for p in self.providers if p.scope == scope]

    def get_conditional_providers(self) -> list[ProviderConfig]:
        """Get all conditional providers."""
        return [p for p in self.providers if p.is_conditional()]

    def get_active_providers(self) -> list[ProviderConfig]:
        """Get all providers that should be registered (conditions evaluated)."""
        active = []
        for provider in self.providers:
            if provider.evaluate_condition():
                active.append(provider)
            else:
                logger.debug(
                    "Provider condition not met, skipping registration",
                    provider=provider.get_provider_name(),
                )
        return active

    def get_interfaces(self) -> list[type]:
        """Get all interface types provided by this collection."""
        return [p.interface for p in self.providers]

    def get_implementations(self) -> list[type]:
        """Get all implementation types in this collection."""
        return [p.get_implementation() for p in self.providers]

    def validate_providers(self) -> list[str]:
        """
        Validate all providers in the collection.

        Returns:
            List of validation error messages
        """
        errors = []

        # Check for duplicate interface registrations
        interfaces: dict[str, str] = {}
        for provider in self.providers:
            interface_name = provider.interface.__name__
            provider_name = provider.get_provider_name()

            if interface_name in interfaces:
                existing_provider = interfaces[interface_name]
                if existing_provider != provider_name:
                    errors.append(
                        f"Interface {interface_name} provided by multiple providers: "
                        f"{existing_provider} and {provider_name}"
                    )
            else:
                interfaces[interface_name] = provider_name

        # Check for circular dependencies (would need dependency analysis)
        # This is left as a placeholder for more sophisticated validation

        return errors

    def to_registration_dict(self) -> dict[type, dict[str, Any]]:
        """
        Convert to a dictionary suitable for bulk registration.

        Returns:
            Dictionary mapping interface types to registration arguments
        """
        registration_dict = {}
        for provider in self.get_active_providers():
            registration_dict[provider.interface] = provider.to_registration_args()
        return registration_dict

    def get_provider_count(self) -> int:
        """Get the number of providers."""
        return len(self.providers)

    def get_active_provider_count(self) -> int:
        """Get the number of active providers."""
        return len(self.get_active_providers())

    def clear(self) -> None:
        """Clear all providers."""
        self.providers.clear()

    def __len__(self) -> int:
        return len(self.providers)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self.providers)

    def __contains__(self, item: ProviderConfig | str | type) -> bool:
        if isinstance(item, str):
            # Check by provider name
            return any(p.get_provider_name() == item for p in self.providers)
        if isinstance(item, type):
            # Check by interface type
            return any(p.interface == item for p in self.providers)
        if isinstance(item, ProviderConfig):
            return item in self.providers
        return False


def normalize_provider_specification(spec: Any) -> ProviderConfig:
    """
    Normalize various provider specification formats to ProviderConfig.

    Args:
        spec: Provider specification in various formats

    Returns:
        Normalized ProviderConfig instance
    """
    if isinstance(spec, ProviderConfig):
        return spec
    if isinstance(spec, dict):
        # Handle dictionary format: {interface: implementation}
        if len(spec) == 1:
            interface, implementation = next(iter(spec.items()))
            return ProviderConfig(interface=interface, implementation=implementation)
        # Handle expanded dictionary format
        return ProviderConfig(**spec)
    if isinstance(spec, type):
        # Handle class self-registration
        return ProviderConfig(interface=spec, implementation=spec)
    raise ValueError(f"Invalid provider specification: {spec}")


def normalize_provider_list(specs: list[Any]) -> list[ProviderConfig]:
    """
    Normalize a list of provider specifications.

    Args:
        specs: List of provider specifications

    Returns:
        List of normalized ProviderConfig instances
    """
    return [normalize_provider_specification(spec) for spec in specs]
