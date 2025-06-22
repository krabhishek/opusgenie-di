# Contributing to OpusGenie DI

Thank you for your interest in contributing to OpusGenie DI! This guide will help you get started with contributing to our dependency injection framework.

## 🌟 Ways to Contribute

- 🐛 **Report bugs** and issues
- ✨ **Suggest new features** or enhancements
- 📝 **Improve documentation**
- 🧪 **Write tests** for better coverage
- 💻 **Submit code** fixes or new features
- 📖 **Create examples** and tutorials
- 🔍 **Review pull requests**

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** (we test on 3.12 and 3.13)
- **Git** for version control
- **uv** for dependency management (recommended)

### Development Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/opusgenie-di.git
   cd opusgenie-di
   ```

2. **Install Dependencies**
   ```bash
   # Using uv (recommended)
   uv sync --dev
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Verify Setup**
   ```bash
   # Run examples to ensure everything works
   uv run python examples/basic_usage.py
   uv run python examples/multi_context.py
   
   # Run tests
   uv run pytest tests/ -v  # (when tests are available)
   ```

4. **Set up Pre-commit** (Optional but recommended)
   ```bash
   uv add --dev pre-commit
   uv run pre-commit install
   ```

## 🛠️ Development Workflow

### Code Quality Standards

We maintain high code quality through automated tools:

```bash
# Format code (required)
uv run ruff format .

# Lint code (required)
uv run ruff check .

# Type checking (required)
uv run mypy opusgenie_di/

# Run all quality checks
uv run ruff format . && uv run ruff check . && uv run mypy opusgenie_di/
```

### Making Changes

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Write Your Code**
   - Follow existing code patterns
   - Add type hints for all functions
   - Write docstrings for public APIs
   - Keep functions focused and small

3. **Test Your Changes**
   ```bash
   # Test examples still work
   uv run python examples/basic_usage.py
   uv run python examples/multi_context.py
   
   # Run quality checks
   uv run ruff format .
   uv run ruff check .
   uv run mypy opusgenie_di/
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   
   # Follow conventional commits format (see below)
   ```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or fixing tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
feat: add auto-wiring for constructor dependencies
fix: resolve circular import in builder module
docs: update README with new examples
test: add unit tests for container implementation
```

## 📋 Pull Request Process

### Before Submitting

**CRITICAL: Always run the local CI check before pushing:**
```bash
make ci-check
```

This emulates the exact GitHub Actions workflow locally and prevents CI failures.

Checklist:
- [ ] Code follows project style guidelines
- [ ] Local CI check passes (`make ci-check`)
- [ ] Examples still work correctly
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow conventional format

### Submitting

1. **Push Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to the GitHub repository
   - Click "New Pull Request"
   - Fill out the PR template completely
   - Link any related issues

3. **PR Review Process**
   - Automated CI checks will run
   - Maintainers will review your code
   - Address any feedback promptly
   - Keep discussions respectful and constructive

### PR Requirements

- ✅ All CI checks pass
- ✅ Code review approval from maintainer
- ✅ No conflicts with main branch
- ✅ Documentation updated if needed

## 🐛 Reporting Issues

### Bug Reports

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml) and include:

- **OpusGenie DI version**
- **Python version**
- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Minimal code example**
- **Error logs** if applicable

### Feature Requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml) and include:

- **Problem description** you're trying to solve
- **Proposed solution** with details
- **Use case** and examples
- **Alternative approaches** considered

## 🧪 Testing Guidelines

### Current Testing Approach

We currently use example-based testing:
- `examples/basic_usage.py` - Basic functionality
- `examples/multi_context.py` - Multi-context features

### Writing Tests (Future)

When the test suite is added, follow these guidelines:

```python
# Example test structure
import pytest
from opusgenie_di import og_component, BaseComponent, get_global_context

def test_component_registration():
    """Test basic component registration."""
    @og_component()
    class TestService(BaseComponent):
        pass
    
    context = get_global_context()
    service = context.resolve(TestService)
    assert isinstance(service, TestService)
```

### Test Categories

- **Unit Tests** - Individual component testing
- **Integration Tests** - Component interaction testing
- **Example Tests** - Verify examples work correctly
- **Performance Tests** - Ensure no regressions

## 📖 Documentation Guidelines

### Code Documentation

```python
def register_component(
    self,
    interface: type[TInterface],
    implementation: type[TInterface] | None = None,
    *,
    scope: ComponentScope = ComponentScope.SINGLETON,
) -> None:
    """
    Register a component in the dependency injection container.
    
    Args:
        interface: The interface type to register
        implementation: Implementation type (defaults to interface)
        scope: Component lifecycle scope
        
    Raises:
        ComponentRegistrationError: If registration fails
        
    Example:
        >>> @og_component()
        >>> class MyService(BaseComponent):
        ...     pass
        >>> context.register_component(MyService)
    """
```

### README Updates

When adding features, update:
- Feature list in README.md
- Usage examples
- API reference section
- Migration guide (for breaking changes)

## 🏗️ Architecture Guidelines

### Core Principles

1. **Type Safety** - Extensive use of type hints
2. **Modularity** - Clear separation of concerns
3. **Extensibility** - Plugin-friendly architecture
4. **Performance** - Efficient dependency resolution
5. **Simplicity** - Easy-to-use APIs

### Code Organization

```
opusgenie_di/
├── _base/          # Foundation components
├── _core/          # Core DI engine
├── _decorators/    # Decorator system
├── _modules/       # Module system
├── _hooks/         # Event/lifecycle hooks
├── _registry/      # Global component registry
├── _testing/       # Testing utilities
└── _utils/         # Shared utilities
```

### Design Patterns

- **Dependency Injection** - Core pattern
- **Decorator Pattern** - For component registration
- **Factory Pattern** - For component creation
- **Observer Pattern** - For event hooks
- **Builder Pattern** - For context construction

## 🔄 Release Process

### For Maintainers

1. **Update Version**
   - Follow [semantic versioning](https://semver.org/)
   - Update `CHANGELOG.md`

2. **Create Release**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

3. **Automated Pipeline**
   - CI runs quality checks
   - Package builds and deploys to TestPyPI
   - Manual approval for PyPI
   - GitHub release created

### Breaking Changes

- Increment major version
- Update migration guide
- Deprecate old APIs first (when possible)
- Provide clear upgrade path

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Maintain professional communication

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas
- **Pull Requests** - Code contributions and reviews

### Getting Help

- Check existing issues and documentation first
- Provide clear, detailed questions
- Include relevant code examples
- Be patient and respectful

## 🎯 Contribution Ideas

### Good First Issues

- Fix typos in documentation
- Add type hints to existing code
- Improve error messages
- Add examples for edge cases
- Write unit tests

### Advanced Contributions

- Performance optimizations
- New dependency injection patterns
- Integration with other frameworks
- Advanced testing utilities
- CI/CD improvements

### Research Areas

- Async dependency injection
- Performance benchmarking
- Integration patterns
- Plugin architectures

## 📄 License

By contributing to OpusGenie DI, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Project documentation
- Special thanks in README

---

**Thank you for contributing to OpusGenie DI! Together we're building a powerful, type-safe dependency injection framework for Python.** 🚀

For questions about contributing, feel free to open an issue or start a discussion. We're here to help!