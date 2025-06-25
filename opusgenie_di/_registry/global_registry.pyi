from .._utils import get_logger as get_logger, log_module_registration as log_module_registration
from .module_metadata import ModuleMetadata as ModuleMetadata
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class GlobalRegistry:
    """
    Global registry for tracking modules and components in the DI system.

    Maintains metadata about all registered modules, validates dependencies,
    and provides querying capabilities for module discovery and management.
    """
    _lock: Incomplete
    _modules: dict[str, ModuleMetadata]
    _modules_by_class: dict[type, ModuleMetadata]
    _dependency_graph: dict[str, list[str]]
    def __init__(self) -> None:
        """Initialize the global registry."""
    def register_module(self, metadata: ModuleMetadata) -> None:
        """
        Register a module in the global registry.

        Args:
            metadata: Module metadata to register
        """
    def unregister_module(self, module_name: str) -> bool:
        """
        Unregister a module from the registry.

        Args:
            module_name: Name of the module to unregister

        Returns:
            True if the module was unregistered, False if it wasn't registered
        """
    def get_module(self, module_name: str) -> ModuleMetadata | None:
        """
        Get module metadata by name.

        Args:
            module_name: Name of the module

        Returns:
            Module metadata or None if not found
        """
    def get_module_by_class(self, module_class: type) -> ModuleMetadata | None:
        """
        Get module metadata by module class.

        Args:
            module_class: The module class

        Returns:
            Module metadata or None if not found
        """
    def get_all_modules(self) -> list[ModuleMetadata]:
        """Get all registered modules."""
    def get_module_names(self) -> list[str]:
        """Get all registered module names."""
    def is_module_registered(self, module_name: str) -> bool:
        """
        Check if a module is registered.

        Args:
            module_name: Name of the module to check

        Returns:
            True if the module is registered
        """
    def find_modules_providing(self, component_type: type) -> list[ModuleMetadata]:
        """
        Find all modules that provide a specific component type.

        Args:
            component_type: The component type to search for

        Returns:
            List of modules that provide the component
        """
    def find_modules_exporting(self, component_type: type) -> list[ModuleMetadata]:
        """
        Find all modules that export a specific component type.

        Args:
            component_type: The component type to search for

        Returns:
            List of modules that export the component
        """
    def find_modules_importing(self, component_type: type) -> list[ModuleMetadata]:
        """
        Find all modules that import a specific component type.

        Args:
            component_type: The component type to search for

        Returns:
            List of modules that import the component
        """
    def get_dependency_graph(self) -> dict[str, list[str]]:
        """
        Get the module dependency graph.

        Returns:
            Dictionary mapping module names to their dependencies
        """
    def get_module_dependencies(self, module_name: str) -> list[str]:
        """
        Get dependencies for a specific module.

        Args:
            module_name: Name of the module

        Returns:
            List of module names this module depends on
        """
    def get_modules_depending_on(self, module_name: str) -> list[str]:
        """
        Get modules that depend on a specific module.

        Args:
            module_name: Name of the module

        Returns:
            List of module names that depend on the given module
        """
    def validate_module_dependencies(self) -> list[str]:
        """
        Validate dependencies across all registered modules.

        Returns:
            List of validation error messages
        """
    def get_build_order(self) -> list[str]:
        """
        Get module build order based on dependencies (topological sort).

        Returns:
            List of module names in build order

        Raises:
            ValueError: If circular dependencies are detected
        """
    def clear_registry(self) -> None:
        """Clear all registered modules."""
    def get_registry_summary(self) -> dict[str, Any]:
        """
        Get a summary of the registry state.

        Returns:
            Dictionary containing registry summary
        """
    def _update_dependency_graph(self, metadata: ModuleMetadata) -> None:
        """Update the dependency graph for a module."""
    def _detect_circular_dependencies(self) -> list[list[str]]:
        """
        Detect circular dependencies in the module graph.

        Returns:
            List of circular dependency chains
        """

_global_registry: Incomplete

def get_global_registry() -> GlobalRegistry:
    """Get the global registry instance."""
def register_module(metadata: ModuleMetadata) -> None:
    """Register a module in the global registry."""
def get_module(module_name: str) -> ModuleMetadata | None:
    """Get module metadata by name."""
def get_all_modules() -> list[ModuleMetadata]:
    """Get all registered modules."""
def validate_module_dependencies() -> list[str]:
    """Validate dependencies across all registered modules."""
def get_build_order() -> list[str]:
    """Get module build order based on dependencies."""
def clear_global_registry() -> None:
    """Clear the global registry."""
