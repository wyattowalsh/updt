# updt Documentation

Welcome to **updt** — a universal package dependency tracker and updater for managing multiple package ecosystems from a single tool.

```{note}
updt supports 16 package managers including brew, npm, pip, conda, cargo, and more!
```

## Quick Links

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 🚀 Getting Started
:link: guides/quickstart
:link-type: doc

Install updt and check for updates across all your package managers
:::

:::{grid-item-card} 📖 User Guide
:link: guides/index
:link-type: doc

Learn how to use updt effectively
:::

:::{grid-item-card} 🛠️ CLI Reference
:link: cli
:link-type: doc

Complete command-line interface documentation
:::

:::{grid-item-card} 📚 API Reference
:link: api/index
:link-type: doc

Python API documentation for developers
:::

::::

## Features

- **Multi-ecosystem support**: Manages 16 package managers including brew, npm, uv, pip, pipx, conda, poetry, yarn, pnpm, cargo, gem, bundler, and version managers (nvm, rvm, pyenv)
- **Smart detection**: Automatically detects installed package managers
- **Async operations**: Fast concurrent update checking and execution
- **Rich CLI**: Beautiful terminal output with progress indicators
- **Interactive TUI**: Text-based user interface for interactive management
- **System profiling**: Generate reports of all installed packages
- **Configurable**: Flexible configuration via pyproject.toml, .env, or environment variables
- **Dry-run mode**: Preview changes before applying them
- **Plugin architecture**: Extensible system for new package managers

## Installation

:::::{tab-set}

::::{tab-item} uvx (recommended)
:sync: uvx

```bash
uvx updt --help
```
::::

::::{tab-item} uv
:sync: uv

```bash
uv tool install updt
updt --help
```
::::

::::{tab-item} pipx
:sync: pipx

```bash
pipx install updt
updt --help
```
::::

::::{tab-item} pip
:sync: pip

```bash
pip install updt
updt --help
```
::::

:::::

## Quick Start

Check for updates across all package managers:

```bash
updt check
```

Perform updates:

```bash
updt update
```

Generate a system profile:

```bash
updt profile
```

Launch the interactive TUI:

```bash
updt tui
```

## Contents

```{toctree}
:maxdepth: 2
:caption: User Guide

guides/index
guides/quickstart
guides/configuration
guides/plugins
guides/profile
```

```{toctree}
:maxdepth: 2
:caption: Reference

cli
api/index
changelog
```

```{toctree}
:maxdepth: 1
:caption: Development

contributing
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
