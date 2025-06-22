"""Tests for global registry."""

import pytest

from opusgenie_di._modules.import_declaration import (
    ImportCollection,
    ModuleContextImport,
)
from opusgenie_di._modules.provider_config import ProviderCollection, ProviderConfig
from opusgenie_di._registry.global_registry import (
    GlobalRegistry,
    clear_global_registry,
    get_all_modules,
    get_build_order,
    get_global_registry,
    get_module,
    register_module,
)
from opusgenie_di._registry.module_metadata import ModuleMetadata
from opusgenie_di._testing import MockComponent, reset_global_state


class TestComponent:
    """Test component for registry tests."""


class AnotherComponent:
    """Another test component for registry tests."""


class TestGlobalRegistry:
    """Test GlobalRegistry class."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()
        self.registry = GlobalRegistry()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_init(self) -> None:
        """Test registry initialization."""
        registry = GlobalRegistry()

        assert len(registry._modules) == 0
        assert len(registry._modules_by_class) == 0
        assert len(registry._dependency_graph) == 0

    def test_register_module(self) -> None:
        """Test registering a module."""
        providers = ProviderCollection()
        providers.add_provider(ProviderConfig(interface=MockComponent))

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[MockComponent],
        )

        self.registry.register_module(metadata)

        assert "test_module" in self.registry._modules
        assert self.registry._modules["test_module"] == metadata
        assert metadata.module_class in self.registry._modules_by_class

    def test_register_module_duplicate(self) -> None:
        """Test registering duplicate module updates existing."""
        providers = ProviderCollection()

        metadata1 = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule2", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        # Should be updated to metadata2
        assert self.registry._modules["test_module"] == metadata2
        assert metadata2.module_class in self.registry._modules_by_class
        assert metadata1.module_class not in self.registry._modules_by_class

    def test_unregister_module_success(self) -> None:
        """Test successful module unregistration."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata)
        assert "test_module" in self.registry._modules

        result = self.registry.unregister_module("test_module")

        assert result is True
        assert "test_module" not in self.registry._modules
        assert metadata.module_class not in self.registry._modules_by_class

    def test_unregister_module_not_found(self) -> None:
        """Test unregistering non-existent module."""
        result = self.registry.unregister_module("nonexistent")

        assert result is False

    def test_unregister_module_removes_dependencies(self) -> None:
        """Test unregistering module removes it from dependency graph."""
        providers = ProviderCollection()

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(component_type=MockComponent, from_context="module1")
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        # module2 should depend on module1
        assert "module1" in self.registry._dependency_graph["module2"]

        # Unregister module1
        self.registry.unregister_module("module1")

        # Dependency should be removed
        assert "module1" not in self.registry._dependency_graph.get("module2", [])

    def test_get_module_found(self) -> None:
        """Test getting module that exists."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata)

        result = self.registry.get_module("test_module")

        assert result == metadata

    def test_get_module_not_found(self) -> None:
        """Test getting module that doesn't exist."""
        result = self.registry.get_module("nonexistent")

        assert result is None

    def test_get_module_by_class_found(self) -> None:
        """Test getting module by class that exists."""
        providers = ProviderCollection()
        module_class = type("TestModule", (), {})

        metadata = ModuleMetadata(
            name="test_module",
            module_class=module_class,
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata)

        result = self.registry.get_module_by_class(module_class)

        assert result == metadata

    def test_get_module_by_class_not_found(self) -> None:
        """Test getting module by class that doesn't exist."""
        result = self.registry.get_module_by_class(type("NonExistent", (), {}))

        assert result is None

    def test_get_all_modules(self) -> None:
        """Test getting all registered modules."""
        providers = ProviderCollection()

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        modules = self.registry.get_all_modules()

        assert len(modules) == 2
        assert metadata1 in modules
        assert metadata2 in modules

    def test_get_module_names(self) -> None:
        """Test getting all module names."""
        providers = ProviderCollection()

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        names = self.registry.get_module_names()

        assert len(names) == 2
        assert "module1" in names
        assert "module2" in names

    def test_is_module_registered_true(self) -> None:
        """Test checking if module is registered (exists)."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata)

        assert self.registry.is_module_registered("test_module") is True

    def test_is_module_registered_false(self) -> None:
        """Test checking if module is registered (doesn't exist)."""
        assert self.registry.is_module_registered("nonexistent") is False

    def test_find_modules_providing(self) -> None:
        """Test finding modules that provide a specific component."""
        providers1 = ProviderCollection()
        providers1.add_provider(ProviderConfig(interface=MockComponent))

        providers2 = ProviderCollection()
        providers2.add_provider(ProviderConfig(interface=TestComponent))

        providers3 = ProviderCollection()
        providers3.add_provider(ProviderConfig(interface=MockComponent))

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers1,
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers2,
            imports=ImportCollection(),
            exports=[],
        )

        metadata3 = ModuleMetadata(
            name="module3",
            module_class=type("Module3", (), {}),
            providers=providers3,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)
        self.registry.register_module(metadata3)

        providing_mock = self.registry.find_modules_providing(MockComponent)
        providing_test = self.registry.find_modules_providing(TestComponent)

        assert len(providing_mock) == 2
        assert metadata1 in providing_mock
        assert metadata3 in providing_mock

        assert len(providing_test) == 1
        assert metadata2 in providing_test

    def test_find_modules_exporting(self) -> None:
        """Test finding modules that export a specific component."""
        providers = ProviderCollection()

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[MockComponent],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[TestComponent],
        )

        metadata3 = ModuleMetadata(
            name="module3",
            module_class=type("Module3", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[MockComponent, TestComponent],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)
        self.registry.register_module(metadata3)

        exporting_mock = self.registry.find_modules_exporting(MockComponent)
        exporting_test = self.registry.find_modules_exporting(TestComponent)

        assert len(exporting_mock) == 2
        assert metadata1 in exporting_mock
        assert metadata3 in exporting_mock

        assert len(exporting_test) == 2
        assert metadata2 in exporting_test
        assert metadata3 in exporting_test

    def test_find_modules_importing(self) -> None:
        """Test finding modules that import a specific component."""
        providers = ProviderCollection()

        imports1 = ImportCollection()
        imports1.add_import(
            ModuleContextImport(
                component_type=MockComponent, from_context="other_module"
            )
        )

        imports2 = ImportCollection()
        imports2.add_import(
            ModuleContextImport(
                component_type=TestComponent, from_context="other_module"
            )
        )

        imports3 = ImportCollection()
        imports3.add_import(
            ModuleContextImport(
                component_type=MockComponent, from_context="other_module"
            )
        )
        imports3.add_import(
            ModuleContextImport(
                component_type=AnotherComponent, from_context="other_module"
            )
        )

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=imports1,
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports2,
            exports=[],
        )

        metadata3 = ModuleMetadata(
            name="module3",
            module_class=type("Module3", (), {}),
            providers=providers,
            imports=imports3,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)
        self.registry.register_module(metadata3)

        importing_mock = self.registry.find_modules_importing(MockComponent)
        importing_test = self.registry.find_modules_importing(TestComponent)

        assert len(importing_mock) == 2
        assert metadata1 in importing_mock
        assert metadata3 in importing_mock

        assert len(importing_test) == 1
        assert metadata2 in importing_test

    def test_get_dependency_graph(self) -> None:
        """Test getting dependency graph."""
        providers = ProviderCollection()

        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(component_type=MockComponent, from_context="module1")
        )

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        graph = self.registry.get_dependency_graph()

        assert "module1" in graph
        assert "module2" in graph
        assert "module1" in graph["module2"]

    def test_get_module_dependencies(self) -> None:
        """Test getting dependencies for specific module."""
        providers = ProviderCollection()

        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(component_type=MockComponent, from_context="module1")
        )
        imports.add_import(
            ModuleContextImport(component_type=TestComponent, from_context="module3")
        )

        metadata = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports,
            exports=[],
        )

        self.registry.register_module(metadata)

        deps = self.registry.get_module_dependencies("module2")

        assert len(deps) == 2
        assert "module1" in deps
        assert "module3" in deps

    def test_get_module_dependencies_nonexistent(self) -> None:
        """Test getting dependencies for non-existent module."""
        deps = self.registry.get_module_dependencies("nonexistent")

        assert deps == []

    def test_get_modules_depending_on(self) -> None:
        """Test getting modules that depend on a specific module."""
        providers = ProviderCollection()

        imports1 = ImportCollection()
        imports1.add_import(
            ModuleContextImport(
                component_type=MockComponent, from_context="target_module"
            )
        )

        imports2 = ImportCollection()
        imports2.add_import(
            ModuleContextImport(
                component_type=TestComponent, from_context="other_module"
            )
        )

        imports3 = ImportCollection()
        imports3.add_import(
            ModuleContextImport(
                component_type=MockComponent, from_context="target_module"
            )
        )

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=imports1,
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports2,
            exports=[],
        )

        metadata3 = ModuleMetadata(
            name="module3",
            module_class=type("Module3", (), {}),
            providers=providers,
            imports=imports3,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)
        self.registry.register_module(metadata3)

        dependents = self.registry.get_modules_depending_on("target_module")

        assert len(dependents) == 2
        assert "module1" in dependents
        assert "module3" in dependents
        assert "module2" not in dependents

    def test_get_build_order_simple(self) -> None:
        """Test getting build order for simple dependency chain."""
        providers = ProviderCollection()

        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(component_type=MockComponent, from_context="module1")
        )

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        build_order = self.registry.get_build_order()

        # module1 should come before module2
        assert build_order.index("module1") < build_order.index("module2")

    def test_get_build_order_circular_dependency(self) -> None:
        """Test build order with circular dependency raises error."""
        providers = ProviderCollection()

        imports1 = ImportCollection()
        imports1.add_import(
            ModuleContextImport(component_type=MockComponent, from_context="module2")
        )

        imports2 = ImportCollection()
        imports2.add_import(
            ModuleContextImport(component_type=TestComponent, from_context="module1")
        )

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=imports1,
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports2,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        with pytest.raises(ValueError, match="Circular dependencies detected"):
            self.registry.get_build_order()

    def test_clear_registry(self) -> None:
        """Test clearing the registry."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        self.registry.register_module(metadata)

        assert len(self.registry._modules) == 1

        self.registry.clear_registry()

        assert len(self.registry._modules) == 0
        assert len(self.registry._modules_by_class) == 0
        assert len(self.registry._dependency_graph) == 0

    def test_detect_circular_dependencies_none(self) -> None:
        """Test circular dependency detection with no cycles."""
        providers = ProviderCollection()

        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(component_type=MockComponent, from_context="module1")
        )

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        cycles = self.registry._detect_circular_dependencies()

        assert cycles == []

    def test_detect_circular_dependencies_simple_cycle(self) -> None:
        """Test circular dependency detection with simple cycle."""
        providers = ProviderCollection()

        imports1 = ImportCollection()
        imports1.add_import(
            ModuleContextImport(component_type=MockComponent, from_context="module2")
        )

        imports2 = ImportCollection()
        imports2.add_import(
            ModuleContextImport(component_type=TestComponent, from_context="module1")
        )

        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=providers,
            imports=imports1,
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=providers,
            imports=imports2,
            exports=[],
        )

        self.registry.register_module(metadata1)
        self.registry.register_module(metadata2)

        cycles = self.registry._detect_circular_dependencies()

        assert len(cycles) > 0
        # Should detect the cycle involving module1 and module2


class TestGlobalRegistryFunctions:
    """Test global registry functions."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    def test_get_global_registry(self) -> None:
        """Test getting global registry instance."""
        registry1 = get_global_registry()
        registry2 = get_global_registry()

        # Should be the same instance
        assert registry1 is registry2

    def test_register_module_function(self) -> None:
        """Test module registration function."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        register_module(metadata)

        registry = get_global_registry()
        assert "test_module" in registry._modules

    def test_get_module_function(self) -> None:
        """Test get module function."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        register_module(metadata)

        result = get_module("test_module")

        assert result == metadata

    def test_get_all_modules_function(self) -> None:
        """Test get all modules function."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        register_module(metadata)

        modules = get_all_modules()

        assert len(modules) == 1
        assert metadata in modules

    def test_get_build_order_function(self) -> None:
        """Test get build order function."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        register_module(metadata)

        build_order = get_build_order()

        assert "test_module" in build_order

    def test_clear_global_registry_function(self) -> None:
        """Test clear global registry function."""
        providers = ProviderCollection()

        metadata = ModuleMetadata(
            name="test_module",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[],
        )

        register_module(metadata)

        registry = get_global_registry()
        assert len(registry._modules) == 1

        clear_global_registry()

        assert len(registry._modules) == 0
