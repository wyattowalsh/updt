# updt

Universal Package Dependency Tracker and Updater

A powerful CLI tool to detect and update dependencies across multiple package managers and ecosystems.

## Features

- 🔄 **Multi-ecosystem support**: Manages updates for brew, npm, uv/pip, yarn, pnpm, cargo, poetry, gem, bundler, mas, and macOS Software Update
- 🎯 **Smart detection**: Automatically detects installed package managers and available updates
- ⚡ **Async operations**: Fast concurrent update checking and execution
- 🎨 **Rich CLI**: Beautiful terminal output with Rich and Textual TUI
- 📝 **Structured logging**: JSONL format for easy parsing and analysis
- 🔧 **Configurable**: Flexible configuration via pyproject.toml, .env, or environment variables
- 🧪 **Dry-run mode**: Preview changes before applying them
- 🔌 **Plugin architecture**: Extensible plugin system for new package managers

## Installation

### Using uvx (recommended)

```bash
uvx updt
```

### Using uv

```bash
uv tool install updt
```

### Using pip

```bash
pip install updt
```

## Usage

### Check for updates

```bash
updt check
```

### Check updates for a specific project

```bash
updt check --project /path/to/project
```

### Update all packages

```bash
updt update
```

### Dry run (preview updates)

```bash
updt update --dry-run
```

### Show configuration

```bash
updt config --show
```

## Configuration

Configure updt via `pyproject.toml`:

```toml
[tool.updt]
log_level = "INFO"
log_format = "jsonl"
default_mode = "plan"
dry_run = false
max_concurrent_updates = 5
timeout = 300

[tool.updt.ecosystems]
brew = true
softwareupdate = true
mas = true
uv = true
pip = true
npm = true
yarn = true
pnpm = true
gem = true
bundler = true
cargo = true
poetry = true
```

Or use environment variables with `UPDT_` prefix:

```bash
export UPDT_LOG_LEVEL=DEBUG
export UPDT_DRY_RUN=true
```

Or create a `.env` file:

```env
UPDT_LOG_LEVEL=DEBUG
UPDT_DRY_RUN=true
```

## Supported Package Managers

- **Homebrew** (`brew`) - macOS package manager
- **macOS Software Update** (`softwareupdate`) - System updates
- **Mac App Store** (`mas`) - App Store applications
- **UV** (`uv`) - Modern Python package manager
- **Pip** (`pip`) - Python package installer
- **NPM** (`npm`) - Node.js package manager
- **Yarn** (`yarn`) - Alternative Node.js package manager
- **PNPM** (`pnpm`) - Fast Node.js package manager
- **Cargo** (`cargo`) - Rust package manager
- **Poetry** (`poetry`) - Python dependency management
- **RubyGems** (`gem`) - Ruby package manager
- **Bundler** (`bundler`) - Ruby dependency manager

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/wyattowalsh/updt.git
cd updt

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run type checker
uv run mypy .
```

### Running locally

```bash
uv run updt check
```

## Architecture

- **CLI**: Built with Typer for command-line interface
- **TUI**: Interactive terminal UI with Textual
- **Config**: Pydantic v2 models with pydantic-settings
- **Logging**: Structured logging with Loguru
- **Plugins**: Modular plugin system for package managers
- **Async**: Async/await for concurrent operations

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.