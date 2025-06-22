# Pull Request

## Description

<!-- Provide a clear and concise description of what this PR does -->

## Type of Change

Please select the relevant option:

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🔧 Code refactoring (no functional changes)
- [ ] 🧪 Test additions or improvements
- [ ] 🚀 Performance improvement
- [ ] 🎨 Style/formatting changes

## Related Issues

<!-- Link any related issues using "Fixes #123", "Closes #123", or "Relates to #123" -->

Fixes #

## Changes Made

<!-- List the main changes made in this PR -->

- 
- 
- 

## Testing

<!-- Describe the tests you ran to verify your changes -->

- [ ] Examples run successfully (`uv run python examples/basic_usage.py`)
- [ ] Examples run successfully (`uv run python examples/multi_context.py`)
- [ ] Code formatting passes (`uv run ruff format --check .`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Type checking passes (`uv run mypy opusgenie_di/`)
- [ ] All existing functionality still works
- [ ] New functionality has been tested

## Breaking Changes

<!-- If this is a breaking change, describe what users need to do to migrate -->

- [ ] This PR introduces no breaking changes
- [ ] This PR introduces breaking changes (migration guide below)

<!-- If breaking changes, provide migration guide: -->

## Documentation

- [ ] Code includes proper docstrings
- [ ] README updated (if needed)
- [ ] CHANGELOG.md updated (if needed)
- [ ] Examples updated (if needed)

## Screenshots/Examples

<!-- If applicable, add screenshots or code examples to help explain your changes -->

```python
# Example of new feature usage
@og_component()
class MyService(BaseComponent):
    pass
```

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

<!-- Add any other context about the pull request here -->