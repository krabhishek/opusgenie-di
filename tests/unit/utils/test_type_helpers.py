"""Tests for type helper utilities."""

from abc import ABC, abstractmethod
from typing import Any
from unittest.mock import patch

import pytest

from opusgenie_di._utils.type_helpers import (
    extract_non_none_types,
    get_constructor_dependencies,
    get_primary_type,
    get_type_name,
    is_concrete_type,
    is_optional_type,
    is_union_type,
    validate_type_compatibility,
)


class TestIsUnionType:
    """Test is_union_type function."""

    def test_typing_union(self) -> None:
        """Test detection of typing.Union types."""

        assert is_union_type(str | int) is True
        assert is_union_type(str | None) is True
        assert is_union_type(str | int | None) is True

    def test_new_union_syntax(self) -> None:
        """Test detection of new | union syntax (Python 3.10+)."""

        # Only test if the feature is available
        try:
            union_type = eval("str | int")
            assert is_union_type(union_type) is True
        except (SyntaxError, TypeError):
            # Feature not available in this Python version
            pytest.skip("Union syntax str | int not available")

    def test_non_union_types(self) -> None:
        """Test that non-union types return False."""

        assert is_union_type(str) is False
        assert is_union_type(int) is False
        assert is_union_type(list[str]) is False
        assert is_union_type(dict[str, int]) is False
        assert is_union_type(Any) is False

    def test_optional_types(self) -> None:
        """Test that Optional types are detected as unions."""

        assert is_union_type(str | None) is True
        assert is_union_type(int | None) is True


class TestExtractNonNoneTypes:
    """Test extract_non_none_types function."""

    def test_union_with_none(self) -> None:
        """Test extracting non-None types from unions with None."""

        result = extract_non_none_types(str | None)
        assert result == [str]

        result = extract_non_none_types(str | int | None)
        assert set(result) == {str, int}

    def test_union_without_none(self) -> None:
        """Test extracting types from unions without None."""

        result = extract_non_none_types(str | int)
        assert set(result) == {str, int}

    def test_non_union_types(self) -> None:
        """Test extracting types from non-union types."""

        result = extract_non_none_types(str)
        assert result == [str]

        result = extract_non_none_types(int)
        assert result == [int]

    def test_none_type(self) -> None:
        """Test extracting from None type."""

        result = extract_non_none_types(type(None))
        assert result == []

    def test_optional_types(self) -> None:
        """Test extracting from Optional types."""

        result = extract_non_none_types(str | None)
        assert result == [str]

        result = extract_non_none_types(list[str] | None)
        assert result == [list[str]]


class TestGetPrimaryType:
    """Test get_primary_type function."""

    def test_simple_types(self) -> None:
        """Test getting primary type from simple types."""

        assert get_primary_type(str) is str
        assert get_primary_type(int) is int
        assert get_primary_type(list) is list

    def test_union_types(self) -> None:
        """Test getting primary type from union types."""

        assert get_primary_type(str | int) is str  # First non-None type
        assert get_primary_type(int | str) is int  # First non-None type
        assert get_primary_type(None | str) is str  # First non-None type

    def test_optional_types(self) -> None:
        """Test getting primary type from optional types."""

        assert get_primary_type(str | None) is str
        assert get_primary_type(list[int] | None) == list[int]

    def test_none_type(self) -> None:
        """Test getting primary type from None."""

        assert get_primary_type(type(None)) is None
        assert get_primary_type(type(None)) is None

    def test_non_class_types(self) -> None:
        """Test getting primary type from non-class types."""

        # Test with non-class objects
        assert get_primary_type("not_a_type") is None
        assert get_primary_type(123) is None


class TestIsOptionalType:
    """Test is_optional_type function."""

    def test_optional_types(self) -> None:
        """Test detection of optional types."""

        assert is_optional_type(str | None) is True
        assert is_optional_type(int | None) is True
        assert is_optional_type(str | None) is True
        assert is_optional_type(int | type(None)) is True

    def test_non_optional_types(self) -> None:
        """Test detection of non-optional types."""

        assert is_optional_type(str) is False
        assert is_optional_type(int) is False
        assert is_optional_type(list[str]) is False
        assert is_optional_type(str | int) is False  # Union without None

    def test_complex_union_with_none(self) -> None:
        """Test unions with multiple types including None."""

        multi_union = str | int | None
        assert is_optional_type(multi_union) is True

        multi_union_no_none = str | int | float
        assert is_optional_type(multi_union_no_none) is False

    def test_none_type(self) -> None:
        """Test None type detection."""

        # Just None should not be detected as optional in this context
        assert is_optional_type(type(None)) is False


class TestGetTypeName:
    """Test get_type_name function."""

    def test_simple_types(self) -> None:
        """Test getting names from simple types."""

        assert get_type_name(str) == "str"
        assert get_type_name(int) == "int"
        assert get_type_name(list) == "list"

    def test_custom_classes(self) -> None:
        """Test getting names from custom classes."""

        class CustomClass:
            pass

        assert get_type_name(CustomClass) == "CustomClass"

    def test_complex_types(self) -> None:
        """Test getting names from complex types."""

        # For complex types without __name__, should return str representation
        optional_type = str | None
        result = get_type_name(optional_type)
        assert isinstance(result, str)
        assert "str" in result or "Optional" in result

    def test_none_type(self) -> None:
        """Test getting name from None type."""

        result = get_type_name(type(None))
        assert isinstance(result, str)


class TestIsConcreteType:
    """Test is_concrete_type function."""

    def test_concrete_classes(self) -> None:
        """Test concrete classes return True."""

        class ConcreteClass:
            def __init__(self) -> None:
                pass

        class ConcreteWithMethods:
            def __init__(self, value: int) -> None:
                self.value = value

            def method(self) -> str:
                return "test"

        assert is_concrete_type(ConcreteClass) is True
        assert is_concrete_type(ConcreteWithMethods) is True
        assert is_concrete_type(str) is True
        assert is_concrete_type(int) is True
        assert is_concrete_type(list) is True

    def test_abstract_classes(self) -> None:
        """Test abstract classes return True (has __init__)."""

        class AbstractClass(ABC):
            @abstractmethod
            def abstract_method(self) -> None:
                pass

        # Note: The current implementation only checks for __init__, not abstractness
        assert is_concrete_type(AbstractClass) is True

    def test_class_without_init(self) -> None:
        """Test classes without __init__ method."""

        class NoInit:
            pass

        # Should still be concrete (inherits object.__init__)
        assert is_concrete_type(NoInit) is True

    def test_non_classes(self) -> None:
        """Test non-class objects return False."""

        assert is_concrete_type("not_a_class") is False
        assert is_concrete_type(123) is False
        assert is_concrete_type([1, 2, 3]) is False
        assert is_concrete_type(lambda x: x) is False

    def test_none_values(self) -> None:
        """Test None and NoneType."""

        assert is_concrete_type(None) is False
        assert is_concrete_type(type(None)) is False

    def test_exception_handling(self) -> None:
        """Test that exceptions during inspection are handled."""

        # Create a class that raises when we try to check it
        class BadClass:
            @property
            def __init__(self):
                raise Exception("inspection failed")

        # Mock inspect.isclass to raise an exception
        with patch(
            "opusgenie_di._utils.type_helpers.inspect.isclass",
            side_effect=Exception("inspection error"),
        ):
            # Should return False when inspection fails
            assert is_concrete_type(BadClass) is False


class TestValidateTypeCompatibility:
    """Test validate_type_compatibility function."""

    def test_same_types(self) -> None:
        """Test compatibility when types are the same."""

        class TestClass:
            pass

        assert validate_type_compatibility(TestClass, TestClass) is True
        assert validate_type_compatibility(str, str) is True
        assert validate_type_compatibility(int, int) is True

    def test_inheritance_compatibility(self) -> None:
        """Test compatibility with inheritance."""

        class Parent:
            pass

        class Child(Parent):
            pass

        class Grandchild(Child):
            pass

        # Child implements Parent interface
        assert validate_type_compatibility(Parent, Child) is True
        assert validate_type_compatibility(Parent, Grandchild) is True
        assert validate_type_compatibility(Child, Grandchild) is True

        # But not the reverse
        assert validate_type_compatibility(Child, Parent) is False

    def test_builtin_type_compatibility(self) -> None:
        """Test compatibility with built-in types."""

        class CustomInt(int):
            pass

        class CustomStr(str):
            pass

        assert validate_type_compatibility(int, CustomInt) is True
        assert validate_type_compatibility(str, CustomStr) is True
        assert validate_type_compatibility(object, str) is True
        assert validate_type_compatibility(object, int) is True

    def test_unrelated_types(self) -> None:
        """Test incompatibility with unrelated types."""

        class ClassA:
            pass

        class ClassB:
            pass

        assert validate_type_compatibility(ClassA, ClassB) is False
        assert validate_type_compatibility(str, int) is False
        assert validate_type_compatibility(list, dict) is False

    def test_non_class_types(self) -> None:
        """Test compatibility with non-class types."""

        # Non-classes should return True (assume compatible)
        assert validate_type_compatibility("not_a_class", "also_not_a_class") is True
        assert validate_type_compatibility(str, "not_a_class") is True

    def test_exception_handling(self) -> None:
        """Test exception handling during compatibility check."""

        # Mock issubclass to raise exception
        with patch("builtins.issubclass", side_effect=TypeError("issubclass failed")):
            result = validate_type_compatibility(str, int)
            assert result is True  # Should return True on error


class TestGetConstructorDependencies:
    """Test get_constructor_dependencies function."""

    def test_simple_constructor(self) -> None:
        """Test extracting dependencies from simple constructor."""

        class SimpleClass:
            def __init__(self, a: int, b: str) -> None:
                self.a = a
                self.b = b

        deps = get_constructor_dependencies(SimpleClass)

        assert len(deps) == 2
        assert deps["a"] == (int, False)
        assert deps["b"] == (str, False)

    def test_constructor_with_optional_params(self) -> None:
        """Test extracting dependencies with optional parameters."""

        class OptionalClass:
            def __init__(self, required: int, optional: str | None = None) -> None:
                self.required = required
                self.optional = optional

        deps = get_constructor_dependencies(OptionalClass)

        assert len(deps) == 2
        assert deps["required"] == (int, False)
        assert deps["optional"] == (str, True)  # Primary type is str, is_optional=True

    def test_constructor_with_defaults(self) -> None:
        """Test extracting dependencies with default values."""

        class DefaultClass:
            def __init__(self, a: int, b: str = "default", c: int = 42) -> None:
                self.a = a
                self.b = b
                self.c = c

        deps = get_constructor_dependencies(DefaultClass)

        assert len(deps) == 3
        assert deps["a"] == (int, False)
        assert deps["b"] == (str, True)
        assert deps["c"] == (int, True)

    def test_constructor_without_annotations(self) -> None:
        """Test constructor without type annotations."""

        class NoAnnotations:
            def __init__(self, a, b=None):
                self.a = a
                self.b = b

        deps = get_constructor_dependencies(NoAnnotations)

        # Should skip parameters without annotations
        assert len(deps) == 0

    def test_constructor_with_union_types(self) -> None:
        """Test constructor with union types."""

        class UnionClass:
            def __init__(
                self, union_param: str | int, optional_union: str | int | None = None
            ) -> None:
                self.union_param = union_param
                self.optional_union = optional_union

        deps = get_constructor_dependencies(UnionClass)

        assert len(deps) == 2
        assert deps["union_param"] == (str, False)  # Primary type is first in union
        assert deps["optional_union"] == (
            str,
            True,
        )  # Primary type is first in union, is_optional=True

    def test_class_without_init(self) -> None:
        """Test class without custom __init__ method."""

        class NoInit:
            pass

        deps = get_constructor_dependencies(NoInit)

        # Should return empty dependencies
        assert len(deps) == 0

    def test_constructor_with_forward_references(self) -> None:
        """Test constructor with forward references."""

        class ForwardRefClass:
            def __init__(self, dependency: "ForwardRefClass") -> None:
                self.dependency = dependency

        deps = get_constructor_dependencies(ForwardRefClass)

        # May or may not resolve forward reference depending on implementation
        assert len(deps) <= 1  # Should have at most 1 dependency
        if len(deps) == 1:
            assert "dependency" in deps

    def test_inherited_constructor(self) -> None:
        """Test class with inherited constructor."""

        class Parent:
            def __init__(self, parent_param: str) -> None:
                self.parent_param = parent_param

        class Child(Parent):
            pass  # Inherits parent's __init__

        deps = get_constructor_dependencies(Child)

        assert len(deps) == 1
        assert deps["parent_param"] == (str, False)

    def test_exception_handling(self) -> None:
        """Test exception handling during dependency extraction."""

        class ProblematicClass:
            def __init__(self, param: int) -> None:
                pass

        # Mock inspect.signature to raise exception
        with patch("inspect.signature", side_effect=Exception("signature error")):
            deps = get_constructor_dependencies(ProblematicClass)
            # Should return empty dict on error
            assert deps == {}

    def test_constructor_with_args_kwargs(self) -> None:
        """Test constructor with *args and **kwargs."""

        class ArgsKwargsClass:
            def __init__(self, a: int, *args: Any, **kwargs: Any) -> None:
                self.a = a
                self.args = args
                self.kwargs = kwargs

        deps = get_constructor_dependencies(ArgsKwargsClass)

        # Currently includes all parameters including *args/**kwargs
        assert len(deps) == 3
        assert deps["a"] == (int, False)
        # *args and **kwargs are included with their type hints
        assert deps["args"] == (Any, False)
        assert deps["kwargs"] == (Any, False)


class TestTypeHelpersIntegration:
    """Test type helpers working together."""

    def test_full_dependency_resolution_workflow(self) -> None:
        """Test complete workflow of dependency resolution."""

        class ServiceA:
            def __init__(self) -> None:
                pass

        class ServiceB:
            def __init__(self, service_a: ServiceA) -> None:
                self.service_a = service_a

        class ServiceC:
            def __init__(
                self, service_b: ServiceB, optional_param: str | None = None
            ) -> None:
                self.service_b = service_b
                self.optional_param = optional_param

        # Test that all classes are concrete
        assert is_concrete_type(ServiceA) is True
        assert is_concrete_type(ServiceB) is True
        assert is_concrete_type(ServiceC) is True

        # Test type compatibility
        assert validate_type_compatibility(ServiceA, ServiceA) is True
        assert validate_type_compatibility(ServiceB, ServiceB) is True

        # Test dependency extraction
        deps_a = get_constructor_dependencies(ServiceA)
        deps_b = get_constructor_dependencies(ServiceB)
        deps_c = get_constructor_dependencies(ServiceC)

        assert len(deps_a) == 0
        assert len(deps_b) == 1
        assert deps_b["service_a"] == (ServiceA, False)

        assert len(deps_c) == 2
        assert deps_c["service_b"] == (ServiceB, False)
        assert deps_c["optional_param"] == (str, True)

    def test_union_type_workflow(self) -> None:
        """Test workflow with union types."""

        class Service:
            def __init__(self, param: str | int) -> None:
                self.param = param

        # Test union detection
        union_type = str | int
        assert is_union_type(union_type) is True
        assert is_optional_type(union_type) is False

        # Test primary type extraction
        primary = get_primary_type(union_type)
        assert primary is str  # First type in union

        # Test dependency extraction
        deps = get_constructor_dependencies(Service)
        assert len(deps) == 1
        assert deps["param"] == (str, False)  # Primary type, not optional

    def test_optional_type_workflow(self) -> None:
        """Test workflow with optional types."""

        class Service:
            def __init__(self, param: str | None = None) -> None:
                self.param = param

        # Test optional detection
        optional_type = str | None
        assert is_union_type(optional_type) is True
        assert is_optional_type(optional_type) is True

        # Test primary type extraction
        primary = get_primary_type(optional_type)
        assert primary is str

        # Test non-None type extraction
        non_none = extract_non_none_types(optional_type)
        assert non_none == [str]

        # Test dependency extraction
        deps = get_constructor_dependencies(Service)
        assert len(deps) == 1
        assert deps["param"] == (str, True)  # Primary type, is optional
