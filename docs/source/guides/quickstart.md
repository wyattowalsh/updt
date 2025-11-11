# Quickstart Guide

Get started with updtr in just a few minutes!

## Installation

:::::{tab-set}

::::{tab-item} uvx (recommended)
```bash
uvx updtr --help
```
::::

::::{tab-item} uv tool
```bash
uv tool install updtr
updtr --help
```
::::

::::{tab-item} pipx
```bash
pipx install updtr
updtr --help
```
::::

:::::

## Basic Usage

### Check for Updates

The most common operation is checking for available updates:

```bash
updtr check
```

This will scan all enabled package managers and display available updates.

### Perform Updates

To apply updates:

```bash
updtr update
```

Or use dry-run mode to preview without applying:

```bash
updtr update --dry-run
```

### Generate System Profile

Create a snapshot of all installed packages:

```bash
updtr profile
```

Export to file:

```bash
updtr profile --output packages.json
```

### Interactive TUI

Launch the text-based user interface:

```bash
updtr tui
```

## Configuration

Create a `.env` file or add to `pyproject.toml`:

```toml
[tool.updtr]
log_level = "INFO"
dry_run = false
max_concurrent_updates = 5

[tool.updtr.ecosystems]
brew = true
npm = true
pip = true
```

## Next Steps

- {doc}`configuration` - Learn about all configuration options
- {doc}`plugins` - Understand the plugin system
- {doc}`profile` - Deep dive into system profiling
- {doc}`../cli` - Complete CLI reference
