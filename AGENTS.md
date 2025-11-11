# AGENTS.md - LLM Development Guide for updt

This document provides guidance for LLM agents working on the `updt` project.

## Project Overview

**updt** is a universal package dependency tracker and updater written in Python. It manages updates across 16 package managers using an extensible plugin architecture.

### Key Technologies

- **Python 3.12+** with modern type hints
- **Typer** for CLI
- **Textual** for TUI
- **Rich** for terminal output
- **Pydantic v2** for configuration and data models
- **Loguru** for logging
- **asyncio** for concurrent operations

## Architecture

### Core Components

```
src/updt/
├── cli.py              # Typer CLI commands
├── updater.py          # Core UpdateManager orchestration
├── profile.py          # System profile generation
├── logging.py          # Loguru setup
├── models/             # Pydantic data models
│   ├── config.py       # Configuration models
│   └── update.py       # Update info/result models
├── plugins/            # Package manager plugins (16 total)
│   ├── base.py         # PluginBase abstract class
│   ├── registry.py     # Plugin registry
│   ├── brew.py         # Homebrew (formulae + casks)
│   ├── mas.py          # Mac App Store
│   ├── npm.py          # Node.js
│   ├── pip.py          # Python
│   ├── cargo.py        # Rust
│   └── ...             # 11 more plugins
└── tui/                # Textual TUI
    └── app.py          # TUI application
```

### Plugin System

All plugins inherit from `PluginBase` and implement:

```python
class PluginBase:
    async def is_available(self) -> bool:
        """Check if the package manager is installed."""
        
    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available updates."""
        
    async def perform_update(self, update_info: UpdateInfo, dry_run: bool = False) -> UpdateResult:
        """Perform an update."""
```

Plugins auto-register via:

```python
from .registry import registry
registry.register(MyPlugin)
```

## Development Guidelines

### Code Style

- Use **ruff** for linting (configured in pyproject.toml)
- Follow **PEP 8** naming conventions
- Use **type hints** throughout
- Keep lines under **100 characters**
- Use **async/await** for I/O operations

### Adding a New Plugin

1. Create `src/updt/plugins/mypkg.py`
2. Inherit from `PluginBase`
3. Implement required methods
4. Register at module bottom: `registry.register(MyPlugin)`
5. Import in `cli.py` to trigger registration
6. Add ecosystem to `models/config.py` `EcosystemConfig`
7. Update `pyproject.toml` `[tool.updt.ecosystems]`
8. Update `.env.example` with new variable

Example:

```python
"""My Package Manager plugin."""

from pathlib import Path
from loguru import logger
from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class MyPkgPlugin(PluginBase):
    """Plugin for MyPkg package manager."""

    async def is_available(self) -> bool:
        stdout, _, exit_code = await self.run_command(["mypkg", "--version"], timeout=10)
        return exit_code == 0

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        if not await self.is_available():
            return []
        
        updates = []
        stdout, _, exit_code = await self.run_command(["mypkg", "outdated"], timeout=60)
        
        if exit_code == 0 and stdout:
            # Parse output and create UpdateInfo objects
            pass
            
        return updates

    async def perform_update(self, update_info: UpdateInfo, dry_run: bool = False) -> UpdateResult:
        # Implementation
        pass


registry.register(MyPkgPlugin)
```

### Testing

- Tests are in `tests/` directory
- Use **pytest** with **asyncio** support
- Run tests: `uv run pytest`
- All tests must pass before committing

### Documentation

- Use **NumPy/Google-style docstrings**
- Document all public APIs
- Update README.md for user-facing changes
- Add Sphinx docs for new features in `docs/source/`

### Configuration

Configuration is loaded from (in order):

1. `pyproject.toml` `[tool.updt]` section
2. Environment variables prefixed with `UPDT_`
3. `.env` file

Example configuration:

```toml
[tool.updt]
log_level = "INFO"
log_format = "text"
dry_run = false
max_concurrent_updates = 5
timeout = 300

[tool.updt.ecosystems]
brew = true
npm = true
pip = true
# ... other ecosystems
```

## Common Tasks

### Running updt Locally

```bash
# Install dependencies
uv sync --all-extras

# Run CLI
uv run updt check

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Build
uv build
```

### Debugging

- Set `UPDT_LOG_LEVEL=DEBUG` for verbose output
- Use `UPDT_LOG_FORMAT=jsonl` for structured logs
- Check `~/.updt/logs/` for log files

### Building Documentation

```bash
cd docs
uv run sphinx-build -b html source _build/html
```

## Plugin Catalog

Current plugins (16):

### Python Ecosystem (6)
- **uv** - Modern Python package manager
- **pip** - Python package installer  
- **pipx** - Isolated Python applications
- **conda** - Environment & dependency manager
- **poetry** - Python dependency management
- **pyenv** - Python version manager

### Node.js Ecosystem (4)
- **npm** - Node.js package manager
- **yarn** - Fast, reliable package manager
- **pnpm** - Disk-efficient package manager
- **nvm** - Node.js version manager

### Ruby Ecosystem (3)
- **gem** - RubyGems package manager
- **bundler** - Ruby dependency manager
- **rvm** - Ruby version manager

### macOS Ecosystem (2)
- **brew** - Homebrew (formulae + casks)
- **mas** - Mac App Store CLI

### Other (1)
- **cargo** - Rust package manager

## API Reference

### UpdateInfo Model

```python
class UpdateInfo(BaseModel):
    ecosystem: str              # Package manager name
    package: str                # Package name
    current_version: str | None # Current version
    latest_version: str | None  # Latest available version
    is_global: bool            # Global vs project-local
    status: UpdateStatus       # AVAILABLE, SUCCESS, FAILED, SKIPPED
    message: str | None        # Optional message
    metadata: dict | None      # Plugin-specific data
```

### UpdateResult Model

```python
class UpdateResult(BaseModel):
    update_info: UpdateInfo     # The update that was attempted
    status: UpdateStatus        # Result status
    message: str                # Human-readable message
    timestamp: datetime         # When update was attempted
    duration: float             # Execution time in seconds
    stdout: str | None          # Command output
    stderr: str | None          # Command errors
    exit_code: int | None       # Process exit code
```

### UpdateManager

```python
class UpdateManager:
    async def initialize(self) -> None:
        """Initialize all enabled plugins."""
    
    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for updates across all plugins."""
    
    async def perform_updates(
        self, 
        updates: list[UpdateInfo], 
        dry_run: bool = False
    ) -> list[UpdateResult]:
        """Perform updates with concurrency control."""
```

### SystemProfile

```python
class SystemProfile:
    async def generate(
        self, 
        project_path: Path | None = None,
        output_format: str = "text"
    ) -> dict[str, Any]:
        """Generate system package profile."""
    
    async def export_to_file(
        self,
        output_path: Path,
        project_path: Path | None = None,
        format: str = "json"
    ) -> None:
        """Export profile to file."""
```

## Error Handling

- Use `try-except` blocks in plugin methods
- Log errors with `logger.exception()`
- Return empty lists for `check_updates()` on errors
- Return `UpdateResult` with `FAILED` status for `perform_update()` errors
- Never raise exceptions to the user

## Performance Considerations

- Use `asyncio` for I/O-bound operations
- Respect `max_concurrent_updates` setting (default: 5)
- Set appropriate timeouts (default: 300s)
- Use semaphores to control concurrency

## Security

- Never log sensitive data (credentials, tokens)
- Validate all external command outputs
- Use `shlex.quote()` for shell arguments when needed
- Avoid shell=True in subprocess calls

## Contribution Workflow

1. Create feature branch
2. Implement changes with tests
3. Run linting: `uv run ruff check .`
4. Run tests: `uv run pytest`
5. Build: `uv build`
6. Update documentation
7. Submit PR with descriptive title

## Resources

- **Repository**: https://github.com/wyattowalsh/updt
- **Documentation**: https://wyattowalsh.github.io/updt/
- **Issue Tracker**: https://github.com/wyattowalsh/updt/issues

## Questions?

For questions or clarifications, please open an issue on GitHub.
