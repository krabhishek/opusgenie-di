# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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