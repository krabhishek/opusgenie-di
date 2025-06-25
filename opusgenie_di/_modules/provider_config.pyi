from .._base import ComponentScope as ComponentScope
from .._utils import get_logger as get_logger, validate_component_registration as validate_component_registration
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

logger: Incomplete

class ProviderConfig(BaseModel):
    """
    Configuration for a provider in a module.

    Defines how a component should be provided within a module context,
    including its interface, implementation, scope, and other metadata.
    """
    interface: type
    implementation: type | None
    scope: ComponentScope
    name: str | None
    factory: Any
    tags: dict[str, str]
    conditional: Any
    model_config: Incomplete
    def model_post_init(self, __context: Any, /) -> None:
        """Validate provider configuration after initialization."""
    def get_implementation(self) -> type:
        """Get the implementation type (defaults to interface if not specified)."""
    def get_provider_name(self) -> str:
        """Get the provider name (defaults to interface name if not specified)."""
    def to_registration_args(self) -> dict[str, Any]:
        """Convert to arguments suitable for context.register_component()."""
    def is_conditional(self) -> bool:
        """Check if this provider has a condition."""
    def evaluate_condition(self) -> bool:
        """
        Evaluate the provider condition.

        Returns:
            True if the provider should be registered
        """
    def __repr__(self) -> str: ...

class ProviderCollection(BaseModel):
    """Collection of provider configurations with validation and utilities."""
    providers: list[ProviderConfig]
    def add_provider(self, provider: ProviderConfig) -> None:
        """Add a provider configuration to the collection."""
    def get_provider_by_name(self, name: str) -> ProviderConfig | None:
        """Get a provider by name."""
    def get_provider_by_interface(self, interface: type) -> ProviderConfig | None:
        """Get a provider by interface type."""
    def get_providers_by_scope(self, scope: ComponentScope) -> list[ProviderConfig]:
        """Get all providers with a specific scope."""
    def get_conditional_providers(self) -> list[ProviderConfig]:
        """Get all conditional providers."""
    def get_active_providers(self) -> list[ProviderConfig]:
        """Get all providers that should be registered (conditions evaluated)."""
    def get_interfaces(self) -> list[type]:
        """Get all interface types provided by this collection."""
    def get_implementations(self) -> list[type]:
        """Get all implementation types in this collection."""
    def validate_providers(self) -> list[str]:
        """
        Validate all providers in the collection.

        Returns:
            List of validation error messages
        """
    def to_registration_dict(self) -> dict[type, dict[str, Any]]:
        """
        Convert to a dictionary suitable for bulk registration.

        Returns:
            Dictionary mapping interface types to registration arguments
        """
    def get_provider_count(self) -> int:
        """Get the number of providers."""
    def get_active_provider_count(self) -> int:
        """Get the number of active providers."""
    def clear(self) -> None:
        """Clear all providers."""
    def __len__(self) -> int: ...
    def __iter__(self): ...
    def __contains__(self, item: ProviderConfig | str | type) -> bool: ...

def normalize_provider_specification(spec: Any) -> ProviderConfig:
    """
    Normalize various provider specification formats to ProviderConfig.

    Args:
        spec: Provider specification in various formats

    Returns:
        Normalized ProviderConfig instance
    """
def normalize_provider_list(specs: list[Any]) -> list[ProviderConfig]:
    """
    Normalize a list of provider specifications.

    Args:
        specs: List of provider specifications

    Returns:
        List of normalized ProviderConfig instances
    """
