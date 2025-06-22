"""Tests for validation utilities."""

from abc import ABC, abstractmethod
from unittest.mock import patch

import pytest

from opusgenie_di._utils.validation import (
    ComponentValidationError,
    ModuleValidationError,
    ValidationError,
    validate_component_dependencies,
    validate_component_registration,
    validate_context_name,
    validate_exports,
    validate_module_name,
    validate_provider_name,
    validate_tags,
)


class TestValidationExceptions:
    """Test validation exception classes."""

    def test_validation_error_basic(self) -> None:
        """Test basic ValidationError creation."""

        error = ValidationError("Test message")
        assert str(error) == "Test message"
        assert error.message == "Test message"
        assert error.details is None

    def test_validation_error_with_details(self) -> None:
        """Test ValidationError with details."""

        error = ValidationError("Test message", "Additional details")
        assert str(error) == "Test message"
        assert error.message == "Test message"
        assert error.details == "Additional details"

    def test_component_validation_error(self) -> None:
        """Test ComponentValidationError."""

        error = ComponentValidationError(
            "Component error",
            component_type="TestComponent",
            details="Component details",
        )
        assert str(error) == "Component error"
        assert error.message == "Component error"
        assert error.component_type == "TestComponent"
        assert error.details == "Component details"

    def test_component_validation_error_minimal(self) -> None:
        """Test ComponentValidationError with minimal arguments."""

        error = ComponentValidationError("Component error")
        assert str(error) == "Component error"
        assert error.component_type is None
        assert error.details is None

    def test_module_validation_error(self) -> None:
        """Test ModuleValidationError."""

        error = ModuleValidationError(
            "Module error", module_name="TestModule", details="Module details"
        )
        assert str(error) == "Module error"
        assert error.message == "Module error"
        assert error.module_name == "TestModule"
        assert error.details == "Module details"

    def test_module_validation_error_minimal(self) -> None:
        """Test ModuleValidationError with minimal arguments."""

        error = ModuleValidationError("Module error")
        assert str(error) == "Module error"
        assert error.module_name is None
        assert error.details is None


class TestComponentRegistrationValidation:
    """Test validate_component_registration function."""

    def test_valid_component_registration(self) -> None:
        """Test validation of valid component registration."""

        class Interface:
            pass

        class Implementation(Interface):
            def __init__(self) -> None:
                pass

        # Should not raise
        validate_component_registration(Interface, Implementation)

    def test_valid_component_registration_with_name(self) -> None:
        """Test validation with custom component name."""

        class Interface:
            pass

        class Implementation(Interface):
            def __init__(self) -> None:
                pass

        # Should not raise
        validate_component_registration(Interface, Implementation, "CustomName")

    def test_implementation_not_concrete(self) -> None:
        """Test validation when implementation is not concrete."""

        class Interface:
            pass

        class AbstractImplementation(Interface, ABC):
            @abstractmethod
            def abstract_method(self) -> None:
                pass

        with patch(
            "opusgenie_di._utils.validation.is_concrete_type", return_value=False
        ):
            with pytest.raises(ComponentValidationError) as exc_info:
                validate_component_registration(Interface, AbstractImplementation)

            assert "is not instantiable" in str(exc_info.value)
            assert exc_info.value.component_type == "AbstractImplementation"

    def test_interface_implementation_incompatibility_warning(self) -> None:
        """Test warning when interface and implementation are incompatible."""

        class Interface:
            pass

        class UnrelatedImplementation:
            def __init__(self) -> None:
                pass

        with (
            patch(
                "opusgenie_di._utils.validation.validate_type_compatibility",
                return_value=False,
            ),
            patch("opusgenie_di._utils.validation.logger") as mock_logger,
        ):
            # Should not raise, but should log warning
            validate_component_registration(Interface, UnrelatedImplementation)
            mock_logger.warning.assert_called_once()


class TestContextNameValidation:
    """Test validate_context_name function."""

    def test_valid_context_names(self) -> None:
        """Test validation of valid context names."""

        valid_names = [
            "simple",
            "with_underscore",
            "with-dash",
            "with123numbers",
            "CamelCase",
            "with.dot",
            "with space",
        ]

        for name in valid_names:
            validate_context_name(name)  # Should not raise

    def test_empty_context_name(self) -> None:
        """Test validation of empty context name."""

        with pytest.raises(ValidationError) as exc_info:
            validate_context_name("")

        assert "Context name cannot be empty" in str(exc_info.value)

    def test_whitespace_only_context_name(self) -> None:
        """Test validation of whitespace-only context name."""

        with pytest.raises(ValidationError) as exc_info:
            validate_context_name("   ")

        assert "Context name cannot be empty" in str(exc_info.value)

    def test_non_string_context_name(self) -> None:
        """Test validation of non-string context name."""

        with pytest.raises(ValidationError) as exc_info:
            validate_context_name(123)  # type: ignore

        assert "Context name must be a string" in str(exc_info.value)

    def test_context_name_with_invalid_characters(self) -> None:
        """Test validation of context names with invalid characters."""

        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]

        for char in invalid_chars:
            invalid_name = f"test{char}name"
            with pytest.raises(ValidationError) as exc_info:
                validate_context_name(invalid_name)

            assert f"contains invalid character '{char}'" in str(exc_info.value)


class TestModuleNameValidation:
    """Test validate_module_name function."""

    def test_valid_module_names(self) -> None:
        """Test validation of valid module names."""

        valid_names = [
            "simple",
            "with_underscore",
            "with-dash",
            "with123numbers",
            "CamelCase",
        ]

        for name in valid_names:
            validate_module_name(name)  # Should not raise

    def test_non_string_module_name(self) -> None:
        """Test validation of non-string module name."""

        with pytest.raises(ModuleValidationError) as exc_info:
            validate_module_name(123)  # type: ignore

        assert "Module name must be a string" in str(exc_info.value)


class TestProviderNameValidation:
    """Test validate_provider_name function."""

    def test_valid_provider_names(self) -> None:
        """Test validation of valid provider names."""

        valid_names = [
            "simple",
            "with_underscore",
            "with-dash",
            "with123numbers",
            "CamelCase",
        ]

        for name in valid_names:
            validate_provider_name(name)  # Should not raise

    def test_non_string_provider_name(self) -> None:
        """Test validation of non-string provider name."""

        with pytest.raises(ValidationError) as exc_info:
            validate_provider_name(123)  # type: ignore

        assert "Provider name must be a string" in str(exc_info.value)


class TestTagsValidation:
    """Test validate_tags function."""

    def test_valid_tags(self) -> None:
        """Test validation of valid tags."""

        valid_tags = [
            {},
            {"simple": "value"},
            {"multiple": "values", "with": "different", "keys": "and_values"},
            {"number": 123, "boolean": True, "list": [1, 2, 3]},
        ]

        for tags in valid_tags:
            validate_tags(tags)  # Should not raise

    def test_non_dict_tags(self) -> None:
        """Test validation of non-dictionary tags."""

        invalid_tags = [
            "not_a_dict",
            123,
            ["list", "of", "tags"],
            ("tuple", "of", "tags"),
        ]

        for tags in invalid_tags:
            with pytest.raises(ValidationError) as exc_info:
                validate_tags(tags)  # type: ignore

            assert "Tags must be a dictionary" in str(exc_info.value)

    def test_non_string_tag_keys(self) -> None:
        """Test validation of tags with non-string keys."""

        invalid_tags = [
            {123: "value"},
            {("tuple", "key"): "value"},
            {None: "value"},
        ]

        for tags in invalid_tags:
            with pytest.raises(ValidationError) as exc_info:
                validate_tags(tags)  # type: ignore

            assert "Tag key must be a string" in str(exc_info.value)

    def test_non_string_tag_values_logged(self) -> None:
        """Test that non-string tag values are logged but not rejected."""

        tags = {
            "number": 123,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        with patch("opusgenie_di._utils.validation.logger") as mock_logger:
            validate_tags(tags)  # Should not raise
            # Should log conversion messages
            assert mock_logger.debug.call_count == 4


class TestExportsValidation:
    """Test validate_exports function."""

    def test_valid_exports(self) -> None:
        """Test validation of valid exports."""

        class ComponentA:
            pass

        class ComponentB:
            pass

        valid_exports = [
            [],
            [ComponentA],
            [ComponentA, ComponentB],
            [str, int, list],
        ]

        for exports in valid_exports:
            validate_exports(exports)  # Should not raise

    def test_non_list_exports(self) -> None:
        """Test validation of non-list exports."""

        class Component:
            pass

        invalid_exports = [
            "not_a_list",
            Component,
            {"not": "a_list"},
            (Component,),  # Tuple instead of list
        ]

        for exports in invalid_exports:
            with pytest.raises(ModuleValidationError) as exc_info:
                validate_exports(exports)  # type: ignore

            assert "Exports must be a list" in str(exc_info.value)

    def test_non_type_exports(self) -> None:
        """Test validation of exports containing non-types."""

        class Component:
            pass

        invalid_exports = [
            ["not_a_type"],
            [Component, "not_a_type"],
            [Component(), Component],  # Instance instead of type
            [123],
        ]

        for exports in invalid_exports:
            with pytest.raises(ModuleValidationError) as exc_info:
                validate_exports(exports)  # type: ignore

            assert "Export must be a type" in str(exc_info.value)


class TestComponentDependenciesValidation:
    """Test validate_component_dependencies function."""

    def test_valid_dependencies(self) -> None:
        """Test validation of valid component dependencies."""

        valid_dependencies = [
            [],
            ["ComponentA"],
            ["ComponentA", "ComponentB", "ComponentC"],
            ["some.module.Component", "another.Component"],
        ]

        for dependencies in valid_dependencies:
            validate_component_dependencies(dependencies)  # Should not raise

    def test_non_list_dependencies(self) -> None:
        """Test validation of non-list dependencies."""

        invalid_dependencies = [
            "single_dependency",
            {"not": "a_list"},
            ("tuple", "instead", "of", "list"),
            123,
        ]

        for dependencies in invalid_dependencies:
            with pytest.raises(ComponentValidationError) as exc_info:
                validate_component_dependencies(dependencies)  # type: ignore

            assert "Dependencies must be a list" in str(exc_info.value)

    def test_non_string_dependencies(self) -> None:
        """Test validation of dependencies containing non-strings."""

        invalid_dependencies = [
            [123],
            ["valid_dependency", 456],
            [None],
            [str],  # Type instead of string
        ]

        for dependencies in invalid_dependencies:
            with pytest.raises(ComponentValidationError) as exc_info:
                validate_component_dependencies(dependencies)  # type: ignore

            assert "Dependency must be a string" in str(exc_info.value)


class TestValidationIntegration:
    """Test validation functions working together."""

    def test_all_validation_errors_inherit_correctly(self) -> None:
        """Test that all validation errors inherit from ValidationError."""

        ValidationError("base")
        component_error = ComponentValidationError("component")
        module_error = ModuleValidationError("module")

        assert isinstance(component_error, ValidationError)
        assert isinstance(module_error, ValidationError)

        # Test exception catching
        try:
            raise component_error
        except ValidationError:
            pass  # Should catch as ValidationError
        else:
            pytest.fail("ComponentValidationError should be caught as ValidationError")

    def test_validation_with_mocked_dependencies(self) -> None:
        """Test validation functions with mocked external dependencies."""

        class TestComponent:
            def __init__(self) -> None:
                pass

        # Mock is_concrete_type to return False
        with (
            patch(
                "opusgenie_di._utils.validation.is_concrete_type", return_value=False
            ),
            pytest.raises(ComponentValidationError),
        ):
            validate_component_registration(TestComponent, TestComponent)

        # Mock validate_type_compatibility to return False
        with (
            patch("opusgenie_di._utils.validation.is_concrete_type", return_value=True),
            patch(
                "opusgenie_di._utils.validation.validate_type_compatibility",
                return_value=False,
            ),
            patch("opusgenie_di._utils.validation.logger") as mock_logger,
        ):
            validate_component_registration(TestComponent, TestComponent)
            mock_logger.warning.assert_called_once()

    def test_error_details_preservation(self) -> None:
        """Test that error details are preserved through validation chain."""

        # Test that details are preserved in ComponentValidationError
        try:
            validate_component_registration(str, "not_a_type", "TestComponent")
        except ComponentValidationError as e:
            assert e.component_type == "TestComponent"
            assert "Implementation must be a type" in e.message
            assert "Only types can be registered" in e.details

    def test_validation_edge_cases(self) -> None:
        """Test validation functions with edge cases."""

        # Test with None values where applicable
        with pytest.raises(ValidationError):
            validate_context_name(None)  # type: ignore

        with pytest.raises(ModuleValidationError):
            validate_module_name(None)  # type: ignore

        with pytest.raises(ValidationError):
            validate_provider_name(None)  # type: ignore

        # Test with empty containers
        validate_tags({})  # Should not raise
        validate_exports([])  # Should not raise
        validate_component_dependencies([])  # Should not raise
