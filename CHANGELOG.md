# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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