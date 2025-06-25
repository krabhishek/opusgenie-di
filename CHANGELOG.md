# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.8] - 2025-01-23

### Improved
- 🔧 **Enhanced Type Support**: Comprehensive improvements to type checking and stub files
  - **Complete Stub Files**: Auto-generated `.pyi` stub files for all modules using `stubgen`
  - **Type Safety**: Resolved all MyPy type checking errors across the entire codebase
  - **Lint Compliance**: Fixed all Ruff lint errors including unused imports and naming conventions
  - **CI Integration**: Added automatic stub file generation to GitHub Actions release workflow
  - **Developer Experience**: Improved IDE support with accurate type hints and autocompletion

### Fixed
- 🔍 **Stub File Quality**: Fixed missing method signatures in type stub files
  - Added missing `enable_auto_wiring()` and `shutdown()` methods to Context class stubs
  - Corrected TypeVar naming conventions to follow PYI standards
  - Removed unused imports and resolved all stub file inconsistencies
- 🛠️ **Configuration Issues**: Fixed regex patterns in MyPy and Ruff configuration
  - Corrected `.pyi` file exclusion patterns to prevent linting errors
  - Improved build tool configuration for better type checking workflow

### Added
- 🚀 **Automated Stub Generation**: GitHub Actions workflow now automatically generates type stubs before PyPI release
  - Ensures published packages always have complete and up-to-date type information
  - Validates stub file quality as part of the CI/CD pipeline
  - Maintains consistency between implementation and type declarations

### Technical Details
- Integrated `stubgen` from MyPy for automatic stub file generation
- Enhanced pyproject.toml configuration for better tool integration
- Improved developer workflow with comprehensive type checking support
- All type stubs now include private methods, docstrings, and complete signatures

## [0.1.4] - 2025-06-22

### Added
- 🚀 **Comprehensive Async Lifecycle Management**: Revolutionary async/await support for robust production applications
  - **EventLoopManager**: Centralized event loop management for guaranteed async execution
  - **Async Component Lifecycle**: Full support for async `initialize()`, `start()`, `stop()`, and `cleanup()` methods
  - **Mixed Sync/Async Support**: Automatic fallback between async and sync lifecycle methods
  - **Thread-Safe Execution**: Safe async operations in any context with proper event loop handling
- 📊 **Event-Driven Monitoring**: Lifecycle callbacks for component observability
  - Component creation and disposal events
  - Configurable lifecycle callbacks on `ScopeManager`
  - Real-time monitoring of component lifecycle events
- 🔄 **Enhanced Component Disposal**: Improved cleanup with proper async handling
  - Async disposal through EventLoopManager integration
  - Graceful fallback when no event loop is available
  - Support for multiple disposal methods (`cleanup`, `dispose`, `close`, `shutdown`)
- 🔄 **Runtime Circular Dependency Detection**: Comprehensive runtime detection of circular dependencies with detailed error reporting
  - Thread-safe resolution chain tracking using thread-local storage
  - Clear error messages showing complete dependency chains
  - Support for forward references in type hints (e.g., `"ServiceB"`)
  - Zero performance impact when no circular dependencies exist
- 📚 **Enhanced Documentation**: Added comprehensive sections to README
  - Async lifecycle management with examples
  - Event-driven monitoring capabilities
  - Mixed sync/async patterns and best practices
  - Circular dependency detection examples and best practices

### Improved
- **Test Reliability**: Fixed 24 failing tests and achieved 100% test suite reliability
- **Test Coverage**: Improved from 81% to 84% code coverage
- **Component Lifecycle**: Enhanced BaseComponent with both sync and async lifecycle variants
- **Error Handling**: Better async error handling and reporting throughout the framework

### Fixed
- **Async Disposal Issues**: Resolved async component disposal in mixed sync/async environments
- **Event Loop Management**: Fixed event loop availability issues in testing and production
- **Module Builder**: Corrected error handling in ContextModuleBuilder
- **Registry Management**: Fixed duplicate module registration cleanup
- **Forward Reference Resolution**: Fixed type hint resolution for forward references in dependency injection
  - Supports string-based forward references like `"ComponentB"` in constructor parameters
- 🔧 **Global Context Reset**: Fixed global context reset functionality for proper test isolation
  - `reset_global_context()` now properly sets global context instance to None
  - `is_global_context_initialized()` correctly returns False after reset
  - Fixed singleton instance cleanup in GlobalContext class
- 🔧 **Auto-Wiring Control**: Fixed auto-wiring enable/disable functionality
  - `enable_auto_wiring()` method now properly sets the context's auto-wire flag
  - Auto-wiring factory respects context's `_auto_wire` setting
  - Contexts can be created with `auto_wire=False` and later enabled
- 🧪 **Test Configuration**: Added pytest-asyncio configuration for async test support
  - Added `asyncio_mode = "auto"` to pyproject.toml
  - Fixed async test execution in global context tests
- 🧪 **Test Assertions**: Fixed summary test assertions to check for class objects instead of class names
- 🧪 **Exception Test Syntax**: Fixed invalid `from` clause usage in exception tests

### Improved
- ⚡ **Dependency Resolution**: Enhanced type hint resolution with proper module globals handling
- 🔍 **Error Reporting**: CircularDependencyError includes complete dependency chain for debugging
- 🛡️ **Thread Safety**: Resolution chain tracking is thread-safe using thread-local storage
- 🧪 **Test Coverage**: All core functionality tests now pass (37/37 tests in key areas)

### Technical Details
- Added thread-local resolution chain tracking in `container_impl.py`
- Enhanced `get_constructor_dependencies()` to resolve forward references correctly
- Improved global context lifecycle management and singleton behavior
- Fixed context auto-wiring state management

## [0.1.3] - 2025-06-22

### Fixed
- 🚀 **PyPI Release Process**: Fixed workflow to allow PyPI deployment when TestPyPI already has the version
- 🔧 **Release Workflow**: Made TestPyPI dependency optional for PyPI deployment
- 🔐 **Workflow Security**: Added least-privilege permissions to all GitHub Actions jobs

### Added
- 🔒 **Security Enhancements**: Comprehensive security measures including branch protection
- 📝 **Security Documentation**: Added SECURITY.md with detailed security policies

## [0.1.2] - 2025-01-22

### Fixed
- 🔧 **CI Pipeline**: Fixed grep pattern for registered types verification
- 🏗️ **Local CI**: Added consistency between local and GitHub Actions CI

## [0.1.1] - 2025-01-22

### Fixed
- 🔧 **MyPy Compatibility**: Resolved all MyPy type checking errors for full type safety
- 🔒 **Privacy Protection**: Removed email address exposure from package metadata
- 🏗️ **Type Annotations**: Fixed protocol covariance, return types, and generic annotations
- 🔄 **Iterator Overrides**: Proper handling of Pydantic BaseModel iterator methods

### Added
- 🚀 **Local CI Emulation**: Complete GitHub Actions emulation for local development
- 📝 **Development Scripts**: `ci-check.sh`, `setup-dev.sh`, and comprehensive Makefile
- 🛠️ **Developer Workflow**: Pre-push validation to prevent CI failures
- 📖 **Enhanced Documentation**: Updated CONTRIBUTING.md and README.md with local CI workflow

### Improved
- ⚡ **Developer Experience**: Fast feedback loop with `make ci-check` command
- 🎯 **Code Quality**: Stricter type checking and validation
- 🔍 **Error Prevention**: Catch issues locally before pushing to GitHub

## [0.1.0] - 2025-01-22

### Added
- 🎉 **Initial release of OpusGenie DI**
- **Multi-Context Architecture**: Support for isolated dependency injection contexts
- **Automatic Dependency Injection**: Robust auto-wiring based on type hints
- **Cross-Context Imports**: Import dependencies between different contexts
- **Declarative Configuration**: `@og_component` and `@og_context` decorators
- **Component Scopes**: Singleton, Transient, and Scoped lifecycle management
- **Type Safety**: Full type safety with Python type hints and runtime validation
- **Event System**: Built-in event hooks for monitoring and extension
- **Natural Assignment**: Clean dependency injection with `self.attr = dependency`
- **BaseComponent**: Pydantic-based component with lifecycle management
- **Testing Utilities**: Comprehensive testing support with mocks and fixtures

### Features
- Angular-style dependency injection for Python
- Support for Python 3.12+
- Built on top of `dependency-injector` for proven reliability
- Comprehensive documentation with examples
- MyPy compatible with extensive type hints

### Examples
- Basic usage example demonstrating singleton and transient components
- Multi-context example showing cross-context dependency injection
- Comprehensive README with usage patterns and best practices