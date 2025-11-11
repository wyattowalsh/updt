## Description

<!-- Provide a clear and concise description of your changes -->

## Type of Change

<!-- Mark relevant items with an 'x' -->

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that causes existing functionality to change)
- [ ] 📝 Documentation update
- [ ] 🔌 New plugin (adds support for a new package manager)
- [ ] ♻️ Refactoring (code improvement without changing functionality)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test updates

## Related Issues

<!-- Link related issues: Fixes #123, Closes #456, Related to #789 -->

Fixes #

## Changes Made

<!-- List the key changes in this PR -->

- 
- 
- 

## Testing

<!-- Describe the tests you ran and how to reproduce them -->

### Test Environment
- OS: <!-- e.g., macOS 14.0, Ubuntu 22.04 -->
- Python version: <!-- e.g., 3.12.0 -->
- Installation method: <!-- e.g., uvx, pip, uv tool -->

### Test Cases
<!-- Describe your test cases -->

- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

### Test Commands
```bash
# Commands you ran to test
uv run pytest
uv run ruff check .
updtr check
```

## Screenshots/Recordings

<!-- If applicable, add screenshots or recordings to demonstrate changes -->

## Documentation

<!-- Check all that apply -->

- [ ] Updated README.md
- [ ] Updated AGENTS.md
- [ ] Added/updated docstrings
- [ ] Updated Sphinx documentation
- [ ] Added usage examples
- [ ] Updated CHANGELOG

## Plugin-Specific (if applicable)

<!-- Only fill this out if adding a new plugin -->

- [ ] Plugin inherits from `PluginBase`
- [ ] Implemented `is_available()` method
- [ ] Implemented `check_updates()` method
- [ ] Implemented `perform_update()` method
- [ ] Plugin auto-registers via `registry.register()`
- [ ] Added to `models/config.py` `EcosystemConfig`
- [ ] Added to `pyproject.toml` `[tool.updtr.ecosystems]`
- [ ] Updated `.env.example`
- [ ] Imported in `cli.py`
- [ ] Supports async operations
- [ ] Handles errors gracefully
- [ ] Respects dry-run mode

## Checklist

<!-- Mark completed items with an 'x' -->

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings or errors
- [ ] I have added tests that prove my fix is effective or feature works
- [ ] New and existing tests pass locally
- [ ] I have updated the documentation accordingly
- [ ] I have checked my code for security issues
- [ ] I have run `ruff check .` and fixed all issues
- [ ] I have synced AGENTS.md with any architectural changes

## Additional Notes

<!-- Any additional information or context -->
