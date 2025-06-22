"""Tests for context module builder."""

from unittest.mock import patch

import pytest

from opusgenie_di import BaseComponent, ComponentScope
from opusgenie_di._core import Context
from opusgenie_di._decorators import og_component, og_context
from opusgenie_di._modules import ModuleContextImport
from opusgenie_di._modules.builder import ContextModuleBuilder
from opusgenie_di._registry import ModuleMetadata
from opusgenie_di._testing import MockComponent, reset_global_state


class TestContextModuleBuilder:
    """Test ContextModuleBuilder class."""

    def setup_method(self) -> None:
        """Setup for each test."""
        reset_global_state()
        self.builder = ContextModuleBuilder()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        reset_global_state()

    @pytest.mark.asyncio
    async def test_build_contexts_empty(self) -> None:
        """Test building contexts with no modules."""
        result = await self.builder.build_contexts()
        assert result == {}

    @pytest.mark.asyncio
    async def test_build_contexts_single_module(self) -> None:
        """Test building contexts with a single module."""

        @og_context(name="test_module", providers=[MockComponent])
        class TestModule:
            pass

        result = await self.builder.build_contexts(TestModule)

        assert "test_module" in result
        assert isinstance(result["test_module"], Context)
        assert result["test_module"].name == "test_module"
        assert result["test_module"].is_registered(MockComponent)

    @pytest.mark.asyncio
    async def test_build_contexts_multiple_modules(self) -> None:
        """Test building contexts with multiple modules."""

        @og_component(scope=ComponentScope.SINGLETON)
        class ServiceA(BaseComponent):
            pass

        @og_component(scope=ComponentScope.SINGLETON)
        class ServiceB(BaseComponent):
            def __init__(self, service_a: ServiceA) -> None:
                super().__init__()
                self.service_a = service_a

        @og_context(name="module_a", providers=[ServiceA], exports=[ServiceA])
        class ModuleA:
            pass

        @og_context(
            name="module_b",
            providers=[ServiceB],
            imports=[
                ModuleContextImport(component_type=ServiceA, from_context="module_a")
            ],
        )
        class ModuleB:
            pass

        result = await self.builder.build_contexts(ModuleA, ModuleB)

        assert len(result) == 2
        assert "module_a" in result
        assert "module_b" in result

        # Check that modules are built in correct order (dependencies first)
        assert result["module_a"].is_registered(ServiceA)
        assert result["module_b"].is_registered(ServiceB)

    @pytest.mark.asyncio
    async def test_build_contexts_invalid_module(self) -> None:
        """Test building contexts with invalid module."""

        class NotAModule:
            pass

        with pytest.raises(RuntimeError, match="is not a context module"):
            await self.builder.build_contexts(NotAModule)

    @pytest.mark.asyncio
    async def test_build_contexts_missing_metadata(self) -> None:
        """Test building contexts with module missing metadata."""

        @og_context(name="test_module")
        class TestModule:
            pass

        # Mock get_module_metadata to return None
        with (
            patch(
                "opusgenie_di._decorators.context_decorator.get_module_metadata",
                return_value=None,
            ),
            pytest.raises(RuntimeError, match="No metadata found for module"),
        ):
            await self.builder.build_contexts(TestModule)

    @pytest.mark.asyncio
    async def test_build_contexts_dependency_validation_error(self) -> None:
        """Test building contexts with dependency validation errors."""

        @og_context(name="test_module", providers=[MockComponent])
        class TestModule:
            pass

        with patch(
            "opusgenie_di._registry.global_registry.GlobalRegistry.validate_module_dependencies"
        ) as mock_validate:
            mock_validate.return_value = ["Validation error"]

            with pytest.raises(
                RuntimeError, match="Module dependency validation failed"
            ):
                await self.builder.build_contexts(TestModule)

    @pytest.mark.asyncio
    async def test_build_contexts_runtime_error(self) -> None:
        """Test building contexts with runtime error during build."""

        @og_context(name="test_module", providers=[MockComponent])
        class TestModule:
            pass

        with (
            patch.object(
                self.builder,
                "_build_single_context",
                side_effect=Exception("Build error"),
            ),
            pytest.raises(RuntimeError, match="Failed to build contexts from modules"),
        ):
            await self.builder.build_contexts(TestModule)

    def test_build_contexts_sync(self) -> None:
        """Test synchronous version of build_contexts."""

        @og_context(name="test_module", providers=[MockComponent])
        class TestModule:
            pass

        result = self.builder.build_contexts_sync(TestModule)

        assert "test_module" in result
        assert isinstance(result["test_module"], Context)
        assert result["test_module"].name == "test_module"

    @pytest.mark.asyncio
    async def test_build_single_context(self) -> None:
        """Test building a single context from metadata."""
        from opusgenie_di._modules.import_declaration import ImportCollection
        from opusgenie_di._modules.provider_config import (
            ProviderCollection,
            ProviderConfig,
        )

        # Create test metadata
        providers = ProviderCollection()
        providers.add_provider(ProviderConfig(interface=MockComponent))

        metadata = ModuleMetadata(
            name="test_context",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[MockComponent],
        )

        context = await self.builder._build_single_context(metadata, {})

        assert context.name == "test_context"
        assert context.is_registered(MockComponent)

    @pytest.mark.asyncio
    async def test_build_single_context_with_imports(self) -> None:
        """Test building a single context with imports."""
        from opusgenie_di._modules.import_declaration import (
            ImportCollection,
            ModuleContextImport,
        )
        from opusgenie_di._modules.provider_config import (
            ProviderCollection,
        )

        # Create source context
        source_context = Context("source_context")
        source_context.register_component(MockComponent)
        existing_contexts = {"source_context": source_context}

        # Create test metadata with imports
        providers = ProviderCollection()
        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(
                component_type=MockComponent, from_context="source_context"
            )
        )

        metadata = ModuleMetadata(
            name="test_context",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=imports,
            exports=[],
        )

        # Mock registry to return source metadata
        source_metadata = ModuleMetadata(
            name="source_context",
            module_class=type("SourceModule", (), {}),
            providers=ProviderCollection(),
            imports=ImportCollection(),
            exports=[MockComponent],
        )

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.get_module.return_value = source_metadata

            context = await self.builder._build_single_context(
                metadata, existing_contexts
            )

            assert context.name == "test_context"

    @pytest.mark.asyncio
    async def test_build_single_context_auto_wiring_failure(self) -> None:
        """Test handling auto-wiring failure during context build."""
        from opusgenie_di._modules.import_declaration import ImportCollection
        from opusgenie_di._modules.provider_config import (
            ProviderCollection,
            ProviderConfig,
        )

        providers = ProviderCollection()
        providers.add_provider(ProviderConfig(interface=MockComponent))

        metadata = ModuleMetadata(
            name="test_context",
            module_class=type("TestModule", (), {}),
            providers=providers,
            imports=ImportCollection(),
            exports=[MockComponent],
        )

        with patch(
            "opusgenie_di._core.Context.enable_auto_wiring",
            side_effect=Exception("Auto-wiring failed"),
        ):
            # Should not raise, just log warning
            context = await self.builder._build_single_context(metadata, {})
            assert context.name == "test_context"

    @pytest.mark.asyncio
    async def test_configure_context_imports_required_missing(self) -> None:
        """Test configuring imports when required context is missing."""
        from opusgenie_di._modules.import_declaration import (
            ImportCollection,
            ModuleContextImport,
        )
        from opusgenie_di._modules.provider_config import ProviderCollection

        context = Context("test_context")
        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(
                component_type=MockComponent,
                from_context="missing_context",
                required=True,
            )
        )

        metadata = ModuleMetadata(
            name="test_context",
            module_class=type("TestModule", (), {}),
            providers=ProviderCollection(),
            imports=imports,
            exports=[],
        )

        with pytest.raises(
            ValueError, match="Required source context .* not available"
        ):
            await self.builder._configure_context_imports(context, metadata, {})

    @pytest.mark.asyncio
    async def test_configure_context_imports_optional_missing(self) -> None:
        """Test configuring imports when optional context is missing."""
        from opusgenie_di._modules.import_declaration import (
            ImportCollection,
            ModuleContextImport,
        )
        from opusgenie_di._modules.provider_config import ProviderCollection

        context = Context("test_context")
        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(
                component_type=MockComponent,
                from_context="missing_context",
                required=False,
            )
        )

        metadata = ModuleMetadata(
            name="test_context",
            module_class=type("TestModule", (), {}),
            providers=ProviderCollection(),
            imports=imports,
            exports=[],
        )

        # Should not raise, just log warning
        await self.builder._configure_context_imports(context, metadata, {})

    @pytest.mark.asyncio
    async def test_configure_context_imports_not_exported(self) -> None:
        """Test configuring imports when component is not exported by source."""
        from opusgenie_di._modules.import_declaration import (
            ImportCollection,
            ModuleContextImport,
        )
        from opusgenie_di._modules.provider_config import ProviderCollection

        # Create source context without exports
        source_context = Context("source_context")
        existing_contexts = {"source_context": source_context}

        context = Context("test_context")
        imports = ImportCollection()
        imports.add_import(
            ModuleContextImport(
                component_type=MockComponent,
                from_context="source_context",
                required=True,
            )
        )

        metadata = ModuleMetadata(
            name="test_context",
            module_class=type("TestModule", (), {}),
            providers=ProviderCollection(),
            imports=imports,
            exports=[],
        )

        # Mock registry to return source metadata without exports
        source_metadata = ModuleMetadata(
            name="source_context",
            module_class=type("SourceModule", (), {}),
            providers=ProviderCollection(),
            imports=ImportCollection(),
            exports=[],  # No exports
        )

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.get_module.return_value = source_metadata

            with pytest.raises(ValueError, match="does not export component"):
                await self.builder._configure_context_imports(
                    context, metadata, existing_contexts
                )

    def test_determine_build_order(self) -> None:
        """Test determining build order for modules."""
        from opusgenie_di._modules.import_declaration import ImportCollection
        from opusgenie_di._modules.provider_config import ProviderCollection

        # Create test metadata
        metadata1 = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=ProviderCollection(),
            imports=ImportCollection(),
            exports=[],
        )

        metadata2 = ModuleMetadata(
            name="module2",
            module_class=type("Module2", (), {}),
            providers=ProviderCollection(),
            imports=ImportCollection(),
            exports=[],
        )

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.get_build_order.return_value = [
                "module1",
                "module2",
            ]

            result = self.builder._determine_build_order([metadata1, metadata2])

            assert len(result) == 2
            assert result[0].name == "module1"
            assert result[1].name == "module2"

    def test_determine_build_order_circular_dependency(self) -> None:
        """Test determining build order with circular dependency error."""
        from opusgenie_di._modules.import_declaration import ImportCollection
        from opusgenie_di._modules.provider_config import ProviderCollection

        metadata = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=ProviderCollection(),
            imports=ImportCollection(),
            exports=[],
        )

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.get_build_order.side_effect = ValueError(
                "Circular dependency"
            )

            with pytest.raises(ValueError, match="Cannot determine build order"):
                self.builder._determine_build_order([metadata])

    def test_determine_build_order_missing_modules(self) -> None:
        """Test determining build order with modules not in registry."""
        from opusgenie_di._modules.import_declaration import ImportCollection
        from opusgenie_di._modules.provider_config import ProviderCollection

        metadata = ModuleMetadata(
            name="module1",
            module_class=type("Module1", (), {}),
            providers=ProviderCollection(),
            imports=ImportCollection(),
            exports=[],
        )

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.get_build_order.return_value = []  # Empty build order

            result = self.builder._determine_build_order([metadata])

            # Module should be added at the end
            assert len(result) == 1
            assert result[0].name == "module1"

    def test_validate_modules_success(self) -> None:
        """Test successful module validation."""

        @og_context(name="test_module", providers=[MockComponent])
        class TestModule:
            pass

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.validate_module_dependencies.return_value = []

            errors = self.builder.validate_modules(TestModule)
            assert errors == []

    def test_validate_modules_not_context_module(self) -> None:
        """Test validating non-context module."""

        class NotAModule:
            pass

        errors = self.builder.validate_modules(NotAModule)
        assert len(errors) == 1
        assert "is not decorated with @og_context" in errors[0]

    def test_validate_modules_missing_metadata(self) -> None:
        """Test validating module with missing metadata."""

        @og_context(name="test_module")
        class TestModule:
            pass

        with patch(
            "opusgenie_di._decorators.context_decorator.get_module_metadata",
            return_value=None,
        ):
            errors = self.builder.validate_modules(TestModule)
            assert len(errors) == 1
            assert "No metadata found for module" in errors[0]

    def test_get_module_summary(self) -> None:
        """Test getting module summary."""

        @og_context(name="test_module", providers=[MockComponent])
        class TestModule:
            pass

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.get_dependency_graph.return_value = {}
            mock_registry.return_value.get_build_order.return_value = ["test_module"]

            summary = self.builder.get_module_summary(TestModule)

            assert summary["module_count"] == 1
            assert len(summary["modules"]) == 1
            assert summary["dependency_graph"] == {}
            assert summary["build_order"] == ["test_module"]

    def test_get_module_summary_non_context_module(self) -> None:
        """Test getting summary with non-context module."""

        class NotAModule:
            pass

        with patch(
            "opusgenie_di._modules.builder.get_global_registry"
        ) as mock_registry:
            mock_registry.return_value.get_dependency_graph.return_value = {}
            mock_registry.return_value.get_build_order.return_value = []

            summary = self.builder.get_module_summary(NotAModule)

            assert summary["module_count"] == 0
            assert summary["modules"] == []
