# CLI Reference

The **updtr** command-line interface provides several commands for managing package updates across multiple ecosystems.

## Main Commands

```{click} updtr.cli:app
:prog: updtr
:nested: full
:show-nested:
```

## Command Overview

### check

Check for available updates across all enabled package managers.

```bash
updtr check
updtr check --project /path/to/project
```

### update

Perform updates for packages with available updates.

```bash
updtr update
updtr update --dry-run  # Preview without applying
```

### profile

Generate a system package profile showing what's installed via which package manager.

```bash
updtr profile
updtr profile --format json
updtr profile --output profile.json
updtr profile --output profile.md --format markdown
```

### tui

Launch the interactive Text User Interface for managing updates.

```bash
updtr tui
```

### config

Display current configuration settings.

```bash
updtr config --show
```

### list-plugins

List all available plugin modules.

```bash
updtr list-plugins
```

## Options

### Global Options

- `--help` - Show help message and exit
- `--version` - Show version and exit

### Project-specific Options

Many commands support a `--project` option to work with project-specific dependencies:

```bash
updtr check --project /path/to/project
```

## Output Formats

The `profile` command supports multiple output formats:

- **text** (default) - Rich formatted tables in the terminal
- **json** - Structured JSON output
- **markdown** - Markdown-formatted tables

## Examples

### Check All Updates

```bash
$ updtr check
Checking for updates...

Found updates:
┌──────────┬─────────┬────────┬────────────┐
│ Package  │ Current │ Latest │ Ecosystem  │
├──────────┼─────────┼────────┼────────────┤
│ python   │ 3.11.0  │ 3.12.0 │ brew       │
│ numpy    │ 1.24.0  │ 1.26.0 │ pip        │
└──────────┴─────────┴────────┴────────────┘
```

### Dry Run Update

```bash
$ updtr update --dry-run
[DRY RUN] Would update python from 3.11.0 to 3.12.0
[DRY RUN] Would update numpy from 1.24.0 to 1.26.0
```

### Export Profile to JSON

```bash
$ updtr profile --output system-profile.json --format json
✓ Profile exported to system-profile.json
```

### Generate Markdown Report

```bash
$ updtr profile --output PACKAGES.md --format markdown
✓ Profile exported to PACKAGES.md
```

## Configuration

See {doc}`guides/configuration` for details on configuring updtr behavior.

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid configuration
