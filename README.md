<div align="center">

# 🔄 updtr

**Universal Package Dependency Tracker and Updater**

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/wyattowalsh/updtrr/workflows/CI/badge.svg)](https://github.com/wyattowalsh/updtrr/actions)
[![codecov](https://codecov.io/gh/wyattowalsh/updtrr/branch/main/graph/badge.svg)](https://codecov.io/gh/wyattowalsh/updtrr)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Plugins](#-supported-package-managers) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

**updtr** is a powerful, unified CLI tool that detects and updates dependencies across **22 package managers** and **multiple ecosystems**. Say goodbye to juggling different update commands—`updtr` handles them all with a single, intuitive interface.

```bash
# Check for updates across ALL your package managers
updtr check

# Update everything with one command
updtr update

# Or use the beautiful interactive TUI
updtr tui
```

> [!NOTE]
> **updtr** supports Python, Node.js, Ruby, Rust, macOS, and more—all through an extensible plugin architecture.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Core Capabilities

- 🔄 **22 Package Managers** — Unified interface for brew, npm, pip, cargo, and more
- ⚡ **Async Operations** — Fast concurrent update checking and execution
- 🎨 **Rich CLI & TUI** — Beautiful terminal output with interactive mode
- 📊 **System Profiling** — Generate reports of installed packages
- 🔧 **Highly Configurable** — via `pyproject.toml`, `.env`, or environment variables

</td>
<td width="50%">

### 🛠️ Developer Features

- 🔌 **Plugin Architecture** — Extensible system for new package managers
- 📝 **Structured Logging** — JSONL format for easy parsing
- 🧪 **Dry-Run Mode** — Preview changes before applying
- 🔢 **Version Managers** — Support for nvm, rvm, pyenv
- 📚 **Comprehensive Docs** — Full Sphinx documentation with Shibuya theme

</td>
</tr>
</table>

---

## 🚀 Installation

<details open>
<summary><b>Recommended: Using uvx (fastest)</b></summary>

```bash
uvx updtr
```

Run directly without installation!

</details>

<details>
<summary><b>Using uv tool install</b></summary>

```bash
uv tool install updtr
```

Installs updtr in an isolated environment.

</details>

<details>
<summary><b>Using pip</b></summary>

```bash
pip install updtr
```

Traditional pip installation.

</details>

<details>
<summary><b>From source</b></summary>

```bash
git clone https://github.com/wyattowalsh/updtrr.git
cd updtr
uv sync --all-extras
uv run updtr --help
```

For development or latest changes.

</details>

---

## 🎬 Quick Start

### Basic Commands

```bash
# Check for updates across all package managers
updtr check

# Check updates for a specific project
updtr check --project /path/to/project

# Update all packages
updtr update

# Preview updates without applying (dry-run)
updtr update --dry-run

# Launch interactive TUI
updtr tui

# List available plugins
updtr list-plugins

# Show current configuration
updtr config --show

# Generate system profile
updtr profile

# Export profile to file
updtr profile --output packages.json
updtr profile --output packages.md --format markdown
```

### Example Output

```console
$ updtr check
⠋ Checking for updates...

┏━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Ecosystem ┃ Package      ┃ Current       ┃ Latest      ┃ Scope  ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━┩
│ npm       │ typescript   │ 5.2.2         │ 5.3.3       │ global │
│ brew      │ python@3.12  │ 3.12.0        │ 3.12.1      │ global │
│ pip       │ requests     │ 2.31.0        │ 2.32.0      │ global │
└───────────┴──────────────┴───────────────┴─────────────┴────────┘

Found 3 updates across 3 ecosystems
```

---

## 🔌 Supported Package Managers

**updtr** currently supports **22 package managers** across multiple ecosystems:

### Python Ecosystem (6 plugins)

| Plugin | Description | Status |
|--------|-------------|--------|
| **uv** | Modern Python package manager | ✅ |
| **pip** | Python package installer | ✅ |
| **pipx** | Isolated Python applications | ✅ |
| **conda** | Environment & dependency manager | ✅ |
| **poetry** | Python dependency management | ✅ |
| **pyenv** | Python version manager | ✅ |

### Node.js Ecosystem (4 plugins)

| Plugin | Description | Status |
|--------|-------------|--------|
| **npm** | Node.js package manager | ✅ |
| **yarn** | Fast, reliable package manager | ✅ |
| **pnpm** | Disk-efficient package manager | ✅ |
| **nvm** | Node.js version manager | ✅ |

### Ruby Ecosystem (3 plugins)

| Plugin | Description | Status |
|--------|-------------|--------|
| **gem** | RubyGems package manager | ✅ |
| **bundler** | Ruby dependency manager | ✅ |
| **rvm** | Ruby version manager | ✅ |

### macOS Ecosystem (2 plugins)

| Plugin | Description | Status |
|--------|-------------|--------|
| **brew** | Homebrew (formulae + casks) | ✅ |
| **mas** | Mac App Store CLI | ✅ |

### Linux Ecosystem (3 plugins)

| Plugin | Description | Status |
|--------|-------------|--------|
| **apt** | Advanced Package Tool (Debian/Ubuntu) | ✅ |
| **dnf** | Dandified YUM (Fedora/RHEL/CentOS) | ✅ |
| **flatpak** | Universal Linux applications | ✅ |

### Windows Ecosystem (3 plugins)

| Plugin | Description | Status |
|--------|-------------|--------|
| **choco** | Chocolatey package manager | ✅ |
| **scoop** | Scoop package manager | ✅ |
| **winget** | Windows Package Manager | ✅ |

### Other Languages (1 plugin)

| Plugin | Description | Status |
|--------|-------------|--------|
| **cargo** | Rust package manager | ✅ |

> [!TIP]
> Need support for another package manager? [Request a plugin](https://github.com/wyattowalsh/updtrr/issues/new/choose) or [contribute one](#-contributing)!

---

## ⚙️ Configuration

Configure **updtr** via `pyproject.toml`, environment variables, or `.env` files:

<details>
<summary><b>pyproject.toml configuration</b></summary>

```toml
[tool.updtr]
log_level = "INFO"
log_format = "jsonl"  # or "text"
default_mode = "plan"
dry_run = false
max_concurrent_updates = 5
timeout = 300  # seconds

[tool.updtr.ecosystems]
brew = true
bundler = true
cargo = true
conda = true
gem = true
mas = true
npm = true
nvm = true
pip = true
pipx = true
pnpm = true
poetry = true
pyenv = true
rvm = true
uv = true
yarn = true
```

</details>

<details>
<summary><b>Environment variables</b></summary>

All configuration keys can be set via environment variables with `UPDTR_` prefix:

```bash
export UPDTR_LOG_LEVEL=DEBUG
export UPDTR_DRY_RUN=true
export UPDTR_MAX_CONCURRENT_UPDATES=10
export UPDTR_ECOSYSTEMS__BREW=true
export UPDTR_ECOSYSTEMS__NPM=false
```

</details>

<details>
<summary><b>.env file</b></summary>

Create a `.env` file in your project root:

```env
UPDTR_LOG_LEVEL=DEBUG
UPDTR_LOG_FORMAT=jsonl
UPDTR_DRY_RUN=false
UPDTR_MAX_CONCURRENT_UPDATES=5
UPDTR_TIMEOUT=300
```

</details>

---

## 🏗️ Architecture

```mermaid
graph TD
    A[CLI Commands] --> B[UpdateManager]
    B --> C[Plugin Registry]
    C --> D1[Python Plugins]
    C --> D2[Node.js Plugins]
    C --> D3[Ruby Plugins]
    C --> D4[macOS Plugins]
    C --> D5[Other Plugins]
    D1 --> E[Async Subprocess]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    B --> F[System Profile]
    B --> G[Logging System]
    A --> H[TUI Interface]
```

**Key Components:**

- **CLI**: Built with Typer for command-line interface
- **TUI**: Interactive terminal UI with Textual
- **Config**: Pydantic v2 models with pydantic-settings
- **Logging**: Structured logging with Loguru
- **Plugins**: Modular plugin system for package managers
- **Async**: Async/await for concurrent operations
- **Profiling**: System-wide package inventory generation

---

## 📚 Documentation

Comprehensive documentation is available:

- 📖 [**Full Documentation**](https://wyattowalsh.github.io/updtr/) — Sphinx docs with Shibuya theme
- 🚀 [**Quick Start Guide**](docs/source/guides/quickstart.md) — Get started in minutes
- 🔧 [**Configuration Guide**](docs/source/guides/configuration.md) — Advanced configuration
- 🔌 [**Plugin Development**](docs/source/guides/plugins.md) — Create custom plugins
- 📊 [**System Profiling**](docs/source/guides/profile.md) — Generate package reports
- 🤖 [**AGENTS.md**](AGENTS.md) — LLM development guide

### Building Documentation Locally

```bash
cd docs
uv run sphinx-build -b html source _build/html
# Open _build/html/index.html in your browser
```

---

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/wyattowalsh/updtrr.git
cd updtr

# Install all dependencies (recommended)
make dev

# Or install manually
pip install -e ".[dev,docs]"

# Install pre-commit hooks
make pre-commit
```

### Makefile Commands

The project includes a comprehensive **Makefile** with 18 commands for development:

```bash
make help         # Show all available commands

# Development
make install      # Install package
make install-dev  # Install with dev dependencies
make dev          # Install everything (dev + docs)

# Testing (80 comprehensive tests)
make test         # Run all tests
make test-cov     # Run with coverage report (35% currently)
make test-html    # Generate HTML coverage report
make test-watch   # Run tests in watch mode
make test-unit    # Run unit tests only
make test-integration  # Run integration tests only

# Code Quality
make lint         # Run linters (ruff + mypy)
make format       # Auto-format code with ruff
make check        # Run all checks (lint + test)
make pre-commit   # Install pre-commit hooks

# Documentation
make docs         # Build Sphinx documentation
make docs-serve   # Serve docs locally (http://localhost:8000)
make docs-clean   # Clean docs build

# Build
make build        # Build package wheel
make clean        # Clean all build artifacts
```

### Running Tests

```bash
# Quick test run
make test

# With coverage report
make test-cov

# Generate HTML coverage report
make test-html
# Then open htmlcov/index.html in your browser

# Run specific test file
pytest tests/test_plugins.py -v

# Run tests matching a pattern
pytest -k "test_brew" -v
```

### Project Structure

```
updtr/
├── src/updtr/               # Source code
│   ├── cli.py             # Typer CLI commands
│   ├── updater.py         # Core UpdateManager
│   ├── profile.py         # System profiling
│   ├── logging.py         # Loguru setup
│   ├── models/            # Pydantic data models
│   │   ├── config.py      # Configuration models
│   │   └── update.py      # Update info/result models
│   ├── plugins/           # Package manager plugins (16 total)
│   │   ├── base.py        # PluginBase abstract class
│   │   ├── registry.py    # Plugin registry
│   │   ├── brew.py        # Homebrew
│   │   ├── npm.py         # Node.js
│   │   ├── pip.py         # Python
│   │   └── ...            # 13 more plugins
│   └── tui/               # Textual TUI
│       └── app.py         # TUI application
├── tests/                  # Test suite
├── docs/                   # Sphinx documentation
├── pyproject.toml          # Project configuration
└── AGENTS.md               # LLM development guide
```

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug reports, feature requests, documentation improvements, or new plugins—we'd love your help.

### Ways to Contribute

1. 🐛 [**Report bugs**](https://github.com/wyattowalsh/updtrr/issues/new/choose)
2. ✨ [**Request features**](https://github.com/wyattowalsh/updtrr/issues/new/choose)
3. 🔌 [**Request plugins**](https://github.com/wyattowalsh/updtrr/issues/new/choose)
4. 💻 **Submit pull requests**
5. 📝 **Improve documentation**

### Development Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints throughout
- Keep lines under 100 characters
- Write tests for new features
- Update documentation and AGENTS.md
- Run `ruff check .` before committing

### Adding a New Plugin

See the [**Plugin Development Guide**](docs/source/guides/plugins.md) or [**AGENTS.md**](AGENTS.md) for detailed instructions.

Quick steps:
1. Create `src/updtr/plugins/mypkg.py`
2. Inherit from `PluginBase`
3. Implement required methods
4. Register plugin
5. Add to configuration
6. Write tests
7. Update documentation

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with these amazing tools:

- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Textual](https://textual.textualize.io/) — TUI framework
- [Rich](https://rich.readthedocs.io/) — Terminal styling
- [Pydantic](https://docs.pydantic.dev/) — Data validation
- [Loguru](https://loguru.readthedocs.io/) — Logging
- [uv](https://docs.astral.sh/uv/) — Python packaging

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/wyattowalsh/updtrr?style=social)
![GitHub forks](https://img.shields.io/github/forks/wyattowalsh/updtrr?style=social)
![GitHub issues](https://img.shields.io/github/issues/wyattowalsh/updtrr)
![GitHub pull requests](https://img.shields.io/github/issues-pr/wyattowalsh/updtrr)
![GitHub last commit](https://img.shields.io/github/last-commit/wyattowalsh/updtrr)

---

<div align="center">

Made with ❤️ by [wyattowalsh](https://github.com/wyattowalsh)

[⬆ Back to Top](#-updtr)

</div>
