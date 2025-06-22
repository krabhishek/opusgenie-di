"""Tests for helper utilities."""

import asyncio
from typing import Any
from unittest.mock import Mock, patch

import pytest

from opusgenie_di._utils.helpers import (
    create_unique_key,
    ensure_coroutine,
    filter_none_values,
    get_class_name,
    get_module_name,
    merge_dicts,
    run_async_in_sync,
    safe_getattr,
    safe_isinstance,
    safe_issubclass,
    truncate_string,
)


class TestEnsureCoroutine:
    """Test ensure_coroutine decorator."""

    def test_async_function_passthrough(self) -> None:
        """Test that async functions are passed through unchanged."""

        async def async_func(x: int) -> int:
            return x * 2

        decorated = ensure_coroutine(async_func)
        assert decorated is async_func

    def test_sync_function_becomes_async(self) -> None:
        """Test that sync functions are wrapped to become async."""

        def sync_func(x: int) -> int:
            return x * 2

        decorated = ensure_coroutine(sync_func)
        assert asyncio.iscoroutinefunction(decorated)
        assert decorated is not sync_func

    async def test_wrapped_sync_function_execution(self) -> None:
        """Test that wrapped sync functions execute correctly."""

        def sync_func(x: int, y: int = 10) -> int:
            return x + y

        decorated = ensure_coroutine(sync_func)
        result = await decorated(5, y=15)
        assert result == 20

    async def test_wrapped_async_function_execution(self) -> None:
        """Test that wrapped async functions execute correctly."""

        async def async_func(x: int) -> int:
            await asyncio.sleep(0.01)  # Small delay
            return x * 3

        decorated = ensure_coroutine(async_func)
        result = await decorated(4)
        assert result == 12

    async def test_function_with_coroutine_result(self) -> None:
        """Test function that returns a coroutine is awaited."""

        async def inner_async() -> str:
            return "async_result"

        def outer_func() -> Any:
            return inner_async()

        decorated = ensure_coroutine(outer_func)
        result = await decorated()
        assert result == "async_result"

    async def test_function_with_exception(self) -> None:
        """Test that exceptions are properly propagated."""

        def failing_func() -> None:
            raise ValueError("test error")

        decorated = ensure_coroutine(failing_func)

        with pytest.raises(ValueError, match="test error"):
            await decorated()


class TestRunAsyncInSync:
    """Test run_async_in_sync function."""

    def test_no_running_loop(self) -> None:
        """Test when no event loop is running."""

        async def simple_coro() -> str:
            return "result"

        # Ensure no loop is running
        try:
            asyncio.get_running_loop()
            pytest.skip("Event loop is already running")
        except RuntimeError:
            pass

        result = run_async_in_sync(simple_coro())
        assert result == "result"

    def test_with_running_loop(self) -> None:
        """Test when an event loop is already running."""

        async def inner_test() -> None:
            async def nested_coro() -> str:
                await asyncio.sleep(0.01)
                return "nested_result"

            # This should use ThreadPoolExecutor
            result = run_async_in_sync(nested_coro())
            assert result == "nested_result"

        # Run inside an event loop
        asyncio.run(inner_test())

    def test_coroutine_with_exception(self) -> None:
        """Test that exceptions from coroutines are propagated."""

        async def failing_coro() -> None:
            raise RuntimeError("async error")

        try:
            asyncio.get_running_loop()
            pytest.skip("Event loop is already running")
        except RuntimeError:
            pass

        with pytest.raises(RuntimeError, match="async error"):
            run_async_in_sync(failing_coro())

    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_thread_pool_execution(self, mock_executor: Mock) -> None:
        """Test that thread pool executor is used when loop is running."""

        async def test_coro() -> str:
            return "thread_result"

        # Mock the executor and future
        mock_future = Mock()
        mock_future.result.return_value = "thread_result"
        mock_executor_instance = Mock()
        mock_executor_instance.submit.return_value = mock_future
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        async def inner_test() -> None:
            result = run_async_in_sync(test_coro())
            assert result == "thread_result"
            mock_executor_instance.submit.assert_called_once()

        asyncio.run(inner_test())


class TestSafeHelpers:
    """Test safe helper functions."""

    def test_safe_getattr_success(self) -> None:
        """Test safe_getattr with existing attribute."""

        class TestObj:
            attr = "value"

        obj = TestObj()
        result = safe_getattr(obj, "attr", "default")
        assert result == "value"

    def test_safe_getattr_missing_attribute(self) -> None:
        """Test safe_getattr with missing attribute."""

        class TestObj:
            pass

        obj = TestObj()
        result = safe_getattr(obj, "missing", "default")
        assert result == "default"

    def test_safe_getattr_with_exception(self) -> None:
        """Test safe_getattr when attribute access raises exception."""

        class TestObj:
            @property
            def failing_prop(self) -> str:
                raise RuntimeError("Property access failed")

        obj = TestObj()
        result = safe_getattr(obj, "failing_prop", "default")
        assert result == "default"

    def test_safe_isinstance_success(self) -> None:
        """Test safe_isinstance with valid type check."""

        assert safe_isinstance("string", str) is True
        assert safe_isinstance(42, int) is True
        assert safe_isinstance([], (list, tuple)) is True
        assert safe_isinstance("string", int) is False

    def test_safe_isinstance_with_exception(self) -> None:
        """Test safe_isinstance when isinstance raises exception."""

        # Create a mock object that raises when used with isinstance
        mock_obj = Mock()

        with patch("builtins.isinstance", side_effect=TypeError("isinstance failed")):
            result = safe_isinstance(mock_obj, str)
            assert result is False

    def test_safe_issubclass_success(self) -> None:
        """Test safe_issubclass with valid subclass check."""

        class Parent:
            pass

        class Child(Parent):
            pass

        assert safe_issubclass(Child, Parent) is True
        assert safe_issubclass(str, object) is True
        assert safe_issubclass(int, str) is False

    def test_safe_issubclass_with_invalid_input(self) -> None:
        """Test safe_issubclass with invalid input."""

        # Non-class object should return False safely
        assert safe_issubclass("not_a_class", object) is False
        assert safe_issubclass(42, int) is False

    def test_safe_issubclass_with_exception(self) -> None:
        """Test safe_issubclass when issubclass raises exception."""

        with patch("builtins.issubclass", side_effect=TypeError("issubclass failed")):
            result = safe_issubclass(str, object)
            assert result is False


class TestDictUtilities:
    """Test dictionary utility functions."""

    def test_merge_dicts_empty(self) -> None:
        """Test merging empty dictionaries."""

        result = merge_dicts()
        assert result == {}

        result = merge_dicts({})
        assert result == {}

        result = merge_dicts({}, {}, {})
        assert result == {}

    def test_merge_dicts_single(self) -> None:
        """Test merging single dictionary."""

        input_dict = {"a": 1, "b": 2}
        result = merge_dicts(input_dict)
        assert result == {"a": 1, "b": 2}
        assert result is not input_dict  # Should be a copy

    def test_merge_dicts_multiple(self) -> None:
        """Test merging multiple dictionaries."""

        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        dict3 = {"c": 5, "d": 6}

        result = merge_dicts(dict1, dict2, dict3)
        assert result == {"a": 1, "b": 3, "c": 5, "d": 6}

    def test_merge_dicts_with_none(self) -> None:
        """Test merging dictionaries with None values."""

        dict1 = {"a": 1}
        dict2 = None
        dict3 = {"b": 2}

        result = merge_dicts(dict1, dict2, dict3)
        assert result == {"a": 1, "b": 2}

    def test_filter_none_values(self) -> None:
        """Test filtering None values from dictionary."""

        input_dict = {
            "a": 1,
            "b": None,
            "c": "value",
            "d": None,
            "e": 0,
            "f": "",
            "g": False,
        }

        result = filter_none_values(input_dict)
        expected = {
            "a": 1,
            "c": "value",
            "e": 0,
            "f": "",
            "g": False,
        }
        assert result == expected

    def test_filter_none_values_empty(self) -> None:
        """Test filtering None values from empty dictionary."""

        result = filter_none_values({})
        assert result == {}

        result = filter_none_values({"a": None, "b": None})
        assert result == {}


class TestNameUtilities:
    """Test name utility functions."""

    def test_get_class_name_with_class(self) -> None:
        """Test get_class_name with actual classes."""

        class TestClass:
            pass

        assert get_class_name(TestClass) == "TestClass"
        assert get_class_name(str) == "str"
        assert get_class_name(list) == "list"

    def test_get_class_name_with_instance(self) -> None:
        """Test get_class_name with class instances."""

        class TestClass:
            pass

        obj = TestClass()
        assert get_class_name(obj) == "TestClass"
        assert get_class_name("string") == "str"
        assert get_class_name([1, 2, 3]) == "list"

    def test_get_class_name_with_no_name(self) -> None:
        """Test get_class_name with objects that have no __name__ attribute."""

        # Object instance (has __class__ but no __name__)
        mock_obj = object()
        result = get_class_name(mock_obj)
        assert result == "object"

        # Create a mock object that has neither __name__ nor __class__
        # This will fall back to str()
        class NoClassMock:
            __class__ = property(lambda self: self._raise_error())

            def _raise_error(self):
                raise AttributeError("no __class__")

            def __str__(self):
                return "custom_str_representation"

        mock = NoClassMock()
        # Use hasattr to avoid the exception
        with patch("opusgenie_di._utils.helpers.hasattr", side_effect=[False, False]):
            result = get_class_name(mock)
            assert result == "custom_str_representation"

    def test_get_module_name_with_class(self) -> None:
        """Test get_module_name with classes."""

        assert get_module_name(str) == "builtins"
        assert get_module_name(list) == "builtins"

        class TestClass:
            pass

        assert get_module_name(TestClass) == "unit.utils.test_helpers"

    def test_get_module_name_with_instance(self) -> None:
        """Test get_module_name with instances."""

        assert get_module_name("string") == "builtins"
        assert get_module_name([1, 2, 3]) == "builtins"

    def test_get_module_name_unknown(self) -> None:
        """Test get_module_name fallback to 'unknown'."""

        # Create object without __module__ attributes
        class NoModuleMock:
            def __getattr__(self, name):
                if name in ("__module__", "__class__"):
                    raise AttributeError(f"no {name}")
                return super().__getattribute__(name)

        mock_obj = NoModuleMock()

        # Mock hasattr to return False for both checks
        with patch("opusgenie_di._utils.helpers.hasattr", side_effect=[False, False]):
            result = get_module_name(mock_obj)
            assert result == "unknown"


class TestStringUtilities:
    """Test string utility functions."""

    def test_create_unique_key_simple(self) -> None:
        """Test creating unique key from simple parts."""

        result = create_unique_key("a", "b", "c")
        assert result == "a:b:c"

    def test_create_unique_key_with_none(self) -> None:
        """Test creating unique key filtering None values."""

        result = create_unique_key("a", None, "b", None, "c")
        assert result == "a:b:c"

    def test_create_unique_key_with_numbers(self) -> None:
        """Test creating unique key with different types."""

        result = create_unique_key("prefix", 123, True, "suffix")
        assert result == "prefix:123:True:suffix"

    def test_create_unique_key_empty(self) -> None:
        """Test creating unique key with no parts."""

        result = create_unique_key()
        assert result == ""

        result = create_unique_key(None, None)
        assert result == ""

    def test_truncate_string_no_truncation(self) -> None:
        """Test truncating string that doesn't need truncation."""

        text = "short text"
        result = truncate_string(text, 50)
        assert result == "short text"

    def test_truncate_string_with_truncation(self) -> None:
        """Test truncating long string."""

        text = "This is a very long string that needs to be truncated"
        result = truncate_string(text, 20)
        assert result == "This is a very lo..."
        assert len(result) == 20

    def test_truncate_string_exact_length(self) -> None:
        """Test truncating string that's exactly max length."""

        text = "exactly20characters!"
        result = truncate_string(text, 20)
        assert result == "exactly20characters!"

    def test_truncate_string_suffix_longer_than_max(self) -> None:
        """Test truncating when suffix is longer than max length."""

        text = "short"
        result = truncate_string(text, 3, "very_long_suffix")
        # When suffix is longer than max_length, we get the suffix
        assert result == "very_long_suffix"
