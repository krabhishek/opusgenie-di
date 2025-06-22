"""Global registry for tracking modules and components."""

from collections import defaultdict
from threading import RLock
from typing import Any

from .._utils import get_logger, log_module_registration
from .module_metadata import ModuleMetadata

logger = get_logger(__name__)


class GlobalRegistry:
    """
    Global registry for tracking modules and components in the DI system.

    Maintains metadata about all registered modules, validates dependencies,
    and provides querying capabilities for module discovery and management.
    """

    def __init__(self) -> None:
        """Initialize the global registry."""
        self._lock = RLock()
        self._modules: dict[str, ModuleMetadata] = {}
        self._modules_by_class: dict[type, ModuleMetadata] = {}
        self._dependency_graph: dict[str, list[str]] = defaultdict(list)

    def register_module(self, metadata: ModuleMetadata) -> None:
        """
        Register a module in the global registry.

        Args:
            metadata: Module metadata to register
        """
        with self._lock:
            # Check for duplicate registration
            if metadata.name in self._modules:
                old_metadata = self._modules[metadata.name]
                logger.warning(
                    "Module already registered, updating",
                    module_name=metadata.name,
                    module_class=metadata.module_class.__name__,
                )
                # Remove old module class reference
                if old_metadata.module_class in self._modules_by_class:
                    del self._modules_by_class[old_metadata.module_class]

            # Register the module
            self._modules[metadata.name] = metadata
            self._modules_by_class[metadata.module_class] = metadata

            # Update dependency graph
            self._update_dependency_graph(metadata)

            log_module_registration(
                metadata.name,
                metadata.get_import_count(),
                metadata.get_export_count(),
                metadata.get_provider_count(),
                module_class=metadata.module_class.__name__,
                version=metadata.version,
            )

    def unregister_module(self, module_name: str) -> bool:
        """
        Unregister a module from the registry.

        Args:
            module_name: Name of the module to unregister

        Returns:
            True if the module was unregistered, False if it wasn't registered
        """
        with self._lock:
            if module_name not in self._modules:
                return False

            metadata = self._modules[module_name]

            # Remove from registries
            del self._modules[module_name]
            if metadata.module_class in self._modules_by_class:
                del self._modules_by_class[metadata.module_class]

            # Remove from dependency graph
            if module_name in self._dependency_graph:
                del self._dependency_graph[module_name]

            # Remove references from other modules' dependencies
            for deps in self._dependency_graph.values():
                if module_name in deps:
                    deps.remove(module_name)

            logger.debug("Unregistered module", module_name=module_name)
            return True

    def get_module(self, module_name: str) -> ModuleMetadata | None:
        """
        Get module metadata by name.

        Args:
            module_name: Name of the module

        Returns:
            Module metadata or None if not found
        """
        with self._lock:
            return self._modules.get(module_name)

    def get_module_by_class(self, module_class: type) -> ModuleMetadata | None:
        """
        Get module metadata by module class.

        Args:
            module_class: The module class

        Returns:
            Module metadata or None if not found
        """
        with self._lock:
            return self._modules_by_class.get(module_class)

    def get_all_modules(self) -> list[ModuleMetadata]:
        """Get all registered modules."""
        with self._lock:
            return list(self._modules.values())

    def get_module_names(self) -> list[str]:
        """Get all registered module names."""
        with self._lock:
            return list(self._modules.keys())

    def is_module_registered(self, module_name: str) -> bool:
        """
        Check if a module is registered.

        Args:
            module_name: Name of the module to check

        Returns:
            True if the module is registered
        """
        with self._lock:
            return module_name in self._modules

    def find_modules_providing(self, component_type: type) -> list[ModuleMetadata]:
        """
        Find all modules that provide a specific component type.

        Args:
            component_type: The component type to search for

        Returns:
            List of modules that provide the component
        """
        with self._lock:
            providing_modules = []
            for metadata in self._modules.values():
                if metadata.provides_component(component_type):
                    providing_modules.append(metadata)
            return providing_modules

    def find_modules_exporting(self, component_type: type) -> list[ModuleMetadata]:
        """
        Find all modules that export a specific component type.

        Args:
            component_type: The component type to search for

        Returns:
            List of modules that export the component
        """
        with self._lock:
            exporting_modules = []
            for metadata in self._modules.values():
                if metadata.exports_component(component_type):
                    exporting_modules.append(metadata)
            return exporting_modules

    def find_modules_importing(self, component_type: type) -> list[ModuleMetadata]:
        """
        Find all modules that import a specific component type.

        Args:
            component_type: The component type to search for

        Returns:
            List of modules that import the component
        """
        with self._lock:
            importing_modules = []
            for metadata in self._modules.values():
                if metadata.imports_component(component_type):
                    importing_modules.append(metadata)
            return importing_modules

    def get_dependency_graph(self) -> dict[str, list[str]]:
        """
        Get the module dependency graph.

        Returns:
            Dictionary mapping module names to their dependencies
        """
        with self._lock:
            return dict(self._dependency_graph)

    def get_module_dependencies(self, module_name: str) -> list[str]:
        """
        Get dependencies for a specific module.

        Args:
            module_name: Name of the module

        Returns:
            List of module names this module depends on
        """
        with self._lock:
            return self._dependency_graph.get(module_name, []).copy()

    def get_modules_depending_on(self, module_name: str) -> list[str]:
        """
        Get modules that depend on a specific module.

        Args:
            module_name: Name of the module

        Returns:
            List of module names that depend on the given module
        """
        with self._lock:
            dependents = []
            for mod_name, deps in self._dependency_graph.items():
                if module_name in deps:
                    dependents.append(mod_name)
            return dependents

    def validate_module_dependencies(self) -> list[str]:
        """
        Validate dependencies across all registered modules.

        Returns:
            List of validation error messages
        """
        with self._lock:
            errors = []

            # Check that all dependencies are satisfied
            for module_name, deps in self._dependency_graph.items():
                for dep in deps:
                    if dep not in self._modules:
                        errors.append(
                            f"Module '{module_name}' depends on unregistered module '{dep}'"
                        )

            # Check for circular dependencies
            circular_deps = self._detect_circular_dependencies()
            for cycle in circular_deps:
                errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")

            # Validate individual modules
            for metadata in self._modules.values():
                module_errors = metadata.validate_module()
                for error in module_errors:
                    errors.append(f"Module '{metadata.name}': {error}")

            return errors

    def get_build_order(self) -> list[str]:
        """
        Get module build order based on dependencies (topological sort).

        Returns:
            List of module names in build order

        Raises:
            ValueError: If circular dependencies are detected
        """
        with self._lock:
            # Check for circular dependencies first
            circular_deps = self._detect_circular_dependencies()
            if circular_deps:
                raise ValueError(f"Circular dependencies detected: {circular_deps}")

            # Perform topological sort
            visited = set()
            temp_visited = set()
            result = []

            def visit(module_name: str) -> None:
                if module_name in temp_visited:
                    raise ValueError(f"Circular dependency involving {module_name}")
                if module_name in visited:
                    return

                temp_visited.add(module_name)

                # Visit dependencies first
                for dep in self._dependency_graph.get(module_name, []):
                    visit(dep)

                temp_visited.remove(module_name)
                visited.add(module_name)
                result.append(module_name)

            # Visit all modules
            for module_name in self._modules:
                if module_name not in visited:
                    visit(module_name)

            return result

    def clear_registry(self) -> None:
        """Clear all registered modules."""
        with self._lock:
            self._modules.clear()
            self._modules_by_class.clear()
            self._dependency_graph.clear()
            logger.debug("Cleared global registry")

    def get_registry_summary(self) -> dict[str, Any]:
        """
        Get a summary of the registry state.

        Returns:
            Dictionary containing registry summary
        """
        with self._lock:
            return {
                "module_count": len(self._modules),
                "modules": [
                    metadata.get_summary() for metadata in self._modules.values()
                ],
                "dependency_graph": dict(self._dependency_graph),
                "circular_dependencies": self._detect_circular_dependencies(),
            }

    def _update_dependency_graph(self, metadata: ModuleMetadata) -> None:
        """Update the dependency graph for a module."""
        dependencies = metadata.get_dependencies()
        self._dependency_graph[metadata.name] = dependencies

    def _detect_circular_dependencies(self) -> list[list[str]]:
        """
        Detect circular dependencies in the module graph.

        Returns:
            List of circular dependency chains
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(module: str, path: list[str]) -> None:
            if module in rec_stack:
                # Found a cycle
                cycle_start = path.index(module)
                cycle = path[cycle_start:] + [module]
                cycles.append(cycle)
                return

            if module in visited:
                return

            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for dep in self._dependency_graph.get(module, []):
                dfs(dep, path)

            path.pop()
            rec_stack.remove(module)

        for module_name in self._modules:
            if module_name not in visited:
                dfs(module_name, [])

        return cycles


# Global registry instance
_global_registry = GlobalRegistry()


def get_global_registry() -> GlobalRegistry:
    """Get the global registry instance."""
    return _global_registry


def register_module(metadata: ModuleMetadata) -> None:
    """Register a module in the global registry."""
    _global_registry.register_module(metadata)


def get_module(module_name: str) -> ModuleMetadata | None:
    """Get module metadata by name."""
    return _global_registry.get_module(module_name)


def get_all_modules() -> list[ModuleMetadata]:
    """Get all registered modules."""
    return _global_registry.get_all_modules()


def validate_module_dependencies() -> list[str]:
    """Validate dependencies across all registered modules."""
    return _global_registry.validate_module_dependencies()


def get_build_order() -> list[str]:
    """Get module build order based on dependencies."""
    return _global_registry.get_build_order()


def clear_global_registry() -> None:
    """Clear the global registry."""
    _global_registry.clear_registry()
