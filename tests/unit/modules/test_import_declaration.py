"""Tests for import declarations."""

from unittest.mock import patch

from pydantic import ValidationError
import pytest

from opusgenie_di._modules.import_declaration import (
    ImportCollection,
    ModuleContextImport,
)
from opusgenie_di._testing import MockComponent


class TestComponent:
    """Test component for import declaration tests."""


class TestModuleContextImport:
    """Test ModuleContextImport class."""

    def test_module_context_import_basic(self) -> None:
        """Test basic import declaration creation."""
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="source_context"
        )

        assert import_decl.component_type == MockComponent
        assert import_decl.from_context == "source_context"
        assert import_decl.name is None
        assert import_decl.alias is None
        assert import_decl.required is True

    def test_module_context_import_with_name(self) -> None:
        """Test import declaration with specific name."""
        import_decl = ModuleContextImport(
            component_type=MockComponent,
            from_context="source_context",
            name="specific_name",
        )

        assert import_decl.name == "specific_name"

    def test_module_context_import_with_alias(self) -> None:
        """Test import declaration with alias."""
        import_decl = ModuleContextImport(
            component_type=MockComponent,
            from_context="source_context",
            alias="aliased_name",
        )

        assert import_decl.alias == "aliased_name"

    def test_module_context_import_optional(self) -> None:
        """Test optional import declaration."""
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="source_context", required=False
        )

        assert import_decl.required is False

    def test_get_provider_name_default(self) -> None:
        """Test get_provider_name returns component name when no name specified."""
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="source_context"
        )

        assert import_decl.get_provider_name() == "MockComponent"

    def test_get_provider_name_explicit(self) -> None:
        """Test get_provider_name returns explicit name."""
        import_decl = ModuleContextImport(
            component_type=MockComponent,
            from_context="source_context",
            name="custom_name",
        )

        assert import_decl.get_provider_name() == "custom_name"

    def test_get_import_key(self) -> None:
        """Test get_import_key generates unique key."""
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="source_context"
        )

        key = import_decl.get_import_key()

        assert key == "source_context:MockComponent"

    def test_get_import_key_with_name(self) -> None:
        """Test get_import_key with explicit name."""
        import_decl = ModuleContextImport(
            component_type=MockComponent,
            from_context="source_context",
            name="custom_name",
        )

        key = import_decl.get_import_key()

        assert key == "source_context:custom_name"

    def test_get_local_name_default(self) -> None:
        """Test get_local_name returns provider name when no alias."""
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="source_context"
        )

        assert import_decl.get_local_name() == "MockComponent"

    def test_get_local_name_with_alias(self) -> None:
        """Test get_local_name returns alias when specified."""
        import_decl = ModuleContextImport(
            component_type=MockComponent,
            from_context="source_context",
            alias="local_alias",
        )

        assert import_decl.get_local_name() == "local_alias"

    def test_to_core_import_declaration(self) -> None:
        """Test converting to core ImportDeclaration."""
        import_decl = ModuleContextImport(
            component_type=MockComponent,
            from_context="source_context",
            name="custom_name",
            alias="local_alias",
        )

        core_import = import_decl.to_core_import_declaration()

        assert core_import.component_type == MockComponent
        assert core_import.source_context == "source_context"
        assert core_import.name == "custom_name"
        assert core_import.alias == "local_alias"

    def test_repr(self) -> None:
        """Test string representation."""
        import_decl = ModuleContextImport(
            component_type=MockComponent,
            from_context="source_context",
            name="custom_name",
            alias="local_alias",
        )

        repr_str = repr(import_decl)

        assert "ModuleContextImport" in repr_str
        assert "MockComponent" in repr_str
        assert "source_context" in repr_str
        assert "custom_name" in repr_str
        assert "local_alias" in repr_str

    def test_model_post_init_valid_context(self) -> None:
        """Test validation during initialization with valid context."""
        with patch(
            "opusgenie_di._modules.import_declaration.validate_context_name"
        ) as mock_validate:
            ModuleContextImport(
                component_type=MockComponent, from_context="valid_context"
            )

            mock_validate.assert_called_once_with("valid_context")

    def test_model_post_init_invalid_component_type(self) -> None:
        """Test validation fails with invalid component type."""
        with (
            patch("opusgenie_di._modules.import_declaration.validate_context_name"),
            pytest.raises(ValidationError, match="Input should be a type"),
        ):
            ModuleContextImport(
                component_type="not_a_type",  # type: ignore
                from_context="source_context",
            )


class TestImportCollection:
    """Test ImportCollection class."""

    def test_import_collection_empty(self) -> None:
        """Test empty import collection."""
        collection = ImportCollection()

        assert len(collection) == 0
        assert collection.get_import_count() == 0
        assert collection.get_component_types() == []
        assert collection.get_source_contexts() == []

    def test_add_import(self) -> None:
        """Test adding import to collection."""
        collection = ImportCollection()
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="source_context"
        )

        collection.add_import(import_decl)

        assert len(collection) == 1
        assert import_decl in collection.imports

    def test_add_import_duplicate(self) -> None:
        """Test adding duplicate import (by key)."""
        collection = ImportCollection()
        import_decl1 = ModuleContextImport(
            component_type=MockComponent, from_context="source_context"
        )
        import_decl2 = ModuleContextImport(
            component_type=MockComponent, from_context="source_context"
        )

        collection.add_import(import_decl1)
        collection.add_import(import_decl2)  # Should be ignored

        assert len(collection) == 1
        assert collection.imports[0] == import_decl1

    def test_get_imports_by_context(self) -> None:
        """Test getting imports from specific context."""
        collection = ImportCollection()

        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        import2 = ModuleContextImport(
            component_type=TestComponent, from_context="context_b"
        )
        # Different component from context_a to avoid duplicate
        import3 = ModuleContextImport(
            component_type=TestComponent, from_context="context_a"
        )

        collection.add_import(import1)
        collection.add_import(import2)
        collection.add_import(import3)

        context_a_imports = collection.get_imports_by_context("context_a")
        context_b_imports = collection.get_imports_by_context("context_b")

        assert len(context_a_imports) == 2
        assert import1 in context_a_imports
        assert import3 in context_a_imports
        assert len(context_b_imports) == 1
        assert import2 in context_b_imports

    def test_get_required_imports(self) -> None:
        """Test getting required imports."""
        collection = ImportCollection()

        required_import = ModuleContextImport(
            component_type=MockComponent, from_context="context_a", required=True
        )
        optional_import = ModuleContextImport(
            component_type=TestComponent, from_context="context_b", required=False
        )

        collection.add_import(required_import)
        collection.add_import(optional_import)

        required = collection.get_required_imports()

        assert len(required) == 1
        assert required_import in required

    def test_get_optional_imports(self) -> None:
        """Test getting optional imports."""
        collection = ImportCollection()

        required_import = ModuleContextImport(
            component_type=MockComponent, from_context="context_a", required=True
        )
        optional_import = ModuleContextImport(
            component_type=TestComponent, from_context="context_b", required=False
        )

        collection.add_import(required_import)
        collection.add_import(optional_import)

        optional = collection.get_optional_imports()

        assert len(optional) == 1
        assert optional_import in optional

    def test_get_component_types(self) -> None:
        """Test getting all imported component types."""
        collection = ImportCollection()

        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        import2 = ModuleContextImport(
            component_type=TestComponent, from_context="context_b"
        )

        collection.add_import(import1)
        collection.add_import(import2)

        component_types = collection.get_component_types()

        assert len(component_types) == 2
        assert MockComponent in component_types
        assert TestComponent in component_types

    def test_get_source_contexts(self) -> None:
        """Test getting all unique source context names."""
        collection = ImportCollection()

        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        import2 = ModuleContextImport(
            component_type=TestComponent, from_context="context_b"
        )
        # Different component from context_a (not duplicate as it's different component)
        import3 = ModuleContextImport(
            component_type=TestComponent, from_context="context_a"
        )

        collection.add_import(import1)
        collection.add_import(import2)
        collection.add_import(import3)

        contexts = collection.get_source_contexts()

        assert len(contexts) == 2
        assert "context_a" in contexts
        assert "context_b" in contexts

    def test_validate_imports_no_errors(self) -> None:
        """Test validating imports with no errors."""
        collection = ImportCollection()

        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        import2 = ModuleContextImport(
            component_type=TestComponent, from_context="context_b"
        )

        collection.add_import(import1)
        collection.add_import(import2)

        errors = collection.validate_imports()

        assert errors == []

    def test_validate_imports_component_conflict(self) -> None:
        """Test validating imports with component conflicts."""
        collection = ImportCollection()

        # Same component type from different contexts
        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        import2 = ModuleContextImport(
            component_type=MockComponent, from_context="context_b"
        )

        collection.add_import(import1)
        collection.add_import(import2)

        errors = collection.validate_imports()

        assert len(errors) == 1
        assert "MockComponent imported from multiple contexts" in errors[0]
        assert "context_a" in errors[0]
        assert "context_b" in errors[0]

    def test_clear(self) -> None:
        """Test clearing all imports."""
        collection = ImportCollection()
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        collection.add_import(import_decl)

        assert len(collection) == 1

        collection.clear()

        assert len(collection) == 0

    def test_iter(self) -> None:
        """Test iterating over imports."""
        collection = ImportCollection()

        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        import2 = ModuleContextImport(
            component_type=TestComponent, from_context="context_b"
        )

        collection.add_import(import1)
        collection.add_import(import2)

        imports = list(collection)

        assert len(imports) == 2
        assert import1 in imports
        assert import2 in imports

    def test_contains_import_declaration(self) -> None:
        """Test contains with ModuleContextImport."""
        collection = ImportCollection()
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        collection.add_import(import_decl)

        assert import_decl in collection

        other_import = ModuleContextImport(
            component_type=TestComponent, from_context="context_b"
        )
        assert other_import not in collection

    def test_contains_string(self) -> None:
        """Test contains with string (import key)."""
        collection = ImportCollection()
        import_decl = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        collection.add_import(import_decl)

        import_key = import_decl.get_import_key()
        assert import_key in collection
        assert "nonexistent_key" not in collection

    def test_contains_invalid_type(self) -> None:
        """Test contains with invalid type."""
        collection = ImportCollection()

        assert 42 not in collection
        assert None not in collection


class TestImportIntegration:
    """Test integration scenarios with imports."""

    def test_complex_import_scenario(self) -> None:
        """Test complex import scenario with multiple contexts and components."""
        collection = ImportCollection()

        # Infrastructure components
        db_import = ModuleContextImport(
            component_type=type("DatabaseService", (), {}),
            from_context="infrastructure",
            name="db_service",
        )

        cache_import = ModuleContextImport(
            component_type=type("CacheService", (), {}),
            from_context="infrastructure",
            required=False,
        )

        # Application components
        auth_import = ModuleContextImport(
            component_type=type("AuthService", (), {}),
            from_context="auth_module",
            alias="authentication",
        )

        collection.add_import(db_import)
        collection.add_import(cache_import)
        collection.add_import(auth_import)

        # Verify collection state
        assert len(collection) == 3

        # Check required vs optional
        required = collection.get_required_imports()
        optional = collection.get_optional_imports()
        assert len(required) == 2
        assert len(optional) == 1

        # Check contexts
        contexts = collection.get_source_contexts()
        assert len(contexts) == 2
        assert "infrastructure" in contexts
        assert "auth_module" in contexts

        # Check component types
        component_types = collection.get_component_types()
        assert len(component_types) == 3

    def test_import_key_uniqueness(self) -> None:
        """Test that import keys are unique and properly generated."""
        # Same component from different contexts should have different keys
        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        import2 = ModuleContextImport(
            component_type=MockComponent, from_context="context_b"
        )

        assert import1.get_import_key() != import2.get_import_key()
        assert import1.get_import_key() == "context_a:MockComponent"
        assert import2.get_import_key() == "context_b:MockComponent"

        # Different components from same context should have different keys
        import3 = ModuleContextImport(
            component_type=TestComponent, from_context="context_a"
        )

        assert import1.get_import_key() != import3.get_import_key()
        assert import3.get_import_key() == "context_a:TestComponent"

    def test_local_name_resolution(self) -> None:
        """Test local name resolution with aliases."""
        # No alias - should use component name
        import1 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a"
        )
        assert import1.get_local_name() == "MockComponent"

        # With alias - should use alias
        import2 = ModuleContextImport(
            component_type=MockComponent, from_context="context_a", alias="MyMock"
        )
        assert import2.get_local_name() == "MyMock"

        # With both name and alias - alias takes precedence for local name
        import3 = ModuleContextImport(
            component_type=MockComponent,
            from_context="context_a",
            name="specific_name",
            alias="local_alias",
        )
        assert import3.get_provider_name() == "specific_name"
        assert import3.get_local_name() == "local_alias"
