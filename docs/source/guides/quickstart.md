# Quickstart Guide

Get started with updt in just a few minutes!

## Installation

:::::{tab-set}

::::{tab-item} uvx (recommended)
```bash
uvx updt --help
```
::::

::::{tab-item} uv tool
```bash
uv tool install updt
updt --help
```
::::

::::{tab-item} pipx
```bash
pipx install updt
updt --help
```
::::

:::::

## Basic Usage

### Check for Updates

The most common operation is checking for available updates:

```bash
updt check
```

This will scan all enabled package managers and display available updates.

### Perform Updates

To apply updates:

```bash
updt update
```

Or use dry-run mode to preview without applying:

```bash
updt update --dry-run
```

### Generate System Profile

Create a snapshot of all installed packages:

```bash
updt profile
```

Export to file:

```bash
updt profile --output packages.json
```

### Interactive TUI

Launch the text-based user interface:

```bash
updt tui
```

## Configuration

Create a `.env` file or add to `pyproject.toml`:

```toml
[tool.updt]
log_level = "INFO"
dry_run = false
max_concurrent_updates = 5

[tool.updt.ecosystems]
brew = true
npm = true
pip = true
```

## Next Steps

- {doc}`configuration` - Learn about all configuration options
- {doc}`plugins` - Understand the plugin system
- {doc}`profile` - Deep dive into system profiling
- {doc}`../cli` - Complete CLI reference
