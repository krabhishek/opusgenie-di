"""Tests for exception hierarchy."""

import pytest

from opusgenie_di import (
    CircularDependencyError,
    ComponentRegistrationError,
    ComponentResolutionError,
    ConfigurationError,
    ContainerError,
    ContextError,
    DIError,
    ImportError,
    LifecycleError,
    ModuleError,
    ProviderError,
    ScopeError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test exception hierarchy and behavior."""

    def test_base_di_error(self) -> None:
        """Test base DIError."""
        error = DIError("Base DI error")
        assert str(error) == "Base DI error"
        assert isinstance(error, Exception)

    def test_container_error_inheritance(self) -> None:
        """Test ContainerError inherits from DIError."""
        error = ContainerError("Container error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Container error"

    def test_context_error_inheritance(self) -> None:
        """Test ContextError inherits from DIError."""
        error = ContextError("Context error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Context error"

    def test_component_registration_error_inheritance(self) -> None:
        """Test ComponentRegistrationError inherits correctly."""
        error = ComponentRegistrationError("Registration error")
        assert isinstance(error, ContextError)
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Registration error"

    def test_component_resolution_error_inheritance(self) -> None:
        """Test ComponentResolutionError inherits correctly."""
        error = ComponentResolutionError("Resolution error")
        assert isinstance(error, ContextError)
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Resolution error"

    def test_circular_dependency_error_inheritance(self) -> None:
        """Test CircularDependencyError inherits correctly."""
        error = CircularDependencyError("Circular dependency")
        assert isinstance(error, ComponentResolutionError)
        assert isinstance(error, ContextError)
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Circular dependency"

    def test_scope_error_inheritance(self) -> None:
        """Test ScopeError inherits from DIError."""
        error = ScopeError("Scope error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Scope error"

    def test_provider_error_inheritance(self) -> None:
        """Test ProviderError inherits from ContainerError."""
        error = ProviderError("Provider error")
        assert isinstance(error, ContainerError)
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Provider error"

    def test_import_error_inheritance(self) -> None:
        """Test ImportError inherits from DIError."""
        error = ImportError("Import error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Import error"

    def test_module_error_inheritance(self) -> None:
        """Test ModuleError inherits from DIError."""
        error = ModuleError("Module error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Module error"

    def test_lifecycle_error_inheritance(self) -> None:
        """Test LifecycleError inherits from DIError."""
        error = LifecycleError("Lifecycle error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Lifecycle error"

    def test_validation_error_inheritance(self) -> None:
        """Test ValidationError inherits from DIError."""
        error = ValidationError("Validation error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Validation error"

    def test_configuration_error_inheritance(self) -> None:
        """Test ConfigurationError inherits from DIError."""
        error = ConfigurationError("Configuration error")
        assert isinstance(error, DIError)
        assert isinstance(error, Exception)
        assert str(error) == "Configuration error"

    def test_error_with_cause(self) -> None:
        """Test error with underlying cause."""
        cause = ValueError("Original error")
        try:
            raise ComponentResolutionError("Resolution failed") from cause
        except ComponentResolutionError as error:
            assert isinstance(error, ComponentResolutionError)
            assert error.__cause__ is cause
            assert str(error) == "Resolution failed"

    def test_error_chaining(self) -> None:
        """Test error chaining behavior."""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            try:
                raise ComponentRegistrationError("Registration failed") from e
            except ComponentRegistrationError as reg_error:
                assert isinstance(reg_error, ComponentRegistrationError)
                assert isinstance(reg_error.__cause__, ValueError)
                assert str(reg_error.__cause__) == "Original error"

    def test_error_with_additional_context(self) -> None:
        """Test errors with additional context information."""
        component_type = str
        error = ComponentResolutionError(
            f"Could not resolve component of type {component_type.__name__}"
        )

        assert "str" in str(error)
        assert isinstance(error, ComponentResolutionError)

    def test_circular_dependency_error_details(self) -> None:
        """Test CircularDependencyError with dependency chain."""
        dependency_chain = ["ComponentA", "ComponentB", "ComponentA"]
        error = CircularDependencyError(
            f"Circular dependency detected: {' -> '.join(dependency_chain)}"
        )

        assert "ComponentA -> ComponentB -> ComponentA" in str(error)
        assert isinstance(error, CircularDependencyError)

    def test_exception_attributes(self) -> None:
        """Test that exceptions maintain proper attributes."""
        message = "Test error message"
        error = ComponentRegistrationError(message)

        assert error.args == (message,)
        assert str(error) == message

    def test_exception_raising_and_catching(self) -> None:
        """Test proper exception raising and catching."""
        with pytest.raises(DIError):
            raise ComponentResolutionError("Test error")

        with pytest.raises(ContextError):
            raise ComponentRegistrationError("Test error")

        with pytest.raises(ComponentResolutionError):
            raise CircularDependencyError("Test error")

        # Test catching specific vs general
        try:
            raise ComponentRegistrationError("Specific error")
        except ComponentRegistrationError:
            # Should catch specific exception
            pass
        except ContextError:
            pytest.fail("Should have caught specific exception")

        try:
            raise ComponentRegistrationError("General error")
        except ContextError:
            # Should catch parent exception
            pass
        except Exception:
            pytest.fail("Should have caught parent exception")

    def test_exception_in_inheritance_check(self) -> None:
        """Test exception inheritance checking utilities."""

        def is_resolution_error(error: Exception) -> bool:
            return isinstance(error, ComponentResolutionError)

        def is_context_error(error: Exception) -> bool:
            return isinstance(error, ContextError)

        def is_di_error(error: Exception) -> bool:
            return isinstance(error, DIError)

        circular_error = CircularDependencyError("Circular")
        registration_error = ComponentRegistrationError("Registration")
        container_error = ContainerError("Container")

        # CircularDependencyError checks
        assert is_resolution_error(circular_error)
        assert is_context_error(circular_error)
        assert is_di_error(circular_error)

        # ComponentRegistrationError checks
        assert not is_resolution_error(registration_error)
        assert is_context_error(registration_error)
        assert is_di_error(registration_error)

        # ContainerError checks
        assert not is_resolution_error(container_error)
        assert not is_context_error(container_error)
        assert is_di_error(container_error)
