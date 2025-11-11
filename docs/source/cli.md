# CLI Reference

The **updt** command-line interface provides several commands for managing package updates across multiple ecosystems.

## Main Commands

```{click} updt.cli:app
:prog: updt
:nested: full
:show-nested:
```

## Command Overview

### check

Check for available updates across all enabled package managers.

```bash
updt check
updt check --project /path/to/project
```

### update

Perform updates for packages with available updates.

```bash
updt update
updt update --dry-run  # Preview without applying
```

### profile

Generate a system package profile showing what's installed via which package manager.

```bash
updt profile
updt profile --format json
updt profile --output profile.json
updt profile --output profile.md --format markdown
```

### tui

Launch the interactive Text User Interface for managing updates.

```bash
updt tui
```

### config

Display current configuration settings.

```bash
updt config --show
```

### list-plugins

List all available plugin modules.

```bash
updt list-plugins
```

## Options

### Global Options

- `--help` - Show help message and exit
- `--version` - Show version and exit

### Project-specific Options

Many commands support a `--project` option to work with project-specific dependencies:

```bash
updt check --project /path/to/project
```

## Output Formats

The `profile` command supports multiple output formats:

- **text** (default) - Rich formatted tables in the terminal
- **json** - Structured JSON output
- **markdown** - Markdown-formatted tables

## Examples

### Check All Updates

```bash
$ updt check
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
$ updt update --dry-run
[DRY RUN] Would update python from 3.11.0 to 3.12.0
[DRY RUN] Would update numpy from 1.24.0 to 1.26.0
```

### Export Profile to JSON

```bash
$ updt profile --output system-profile.json --format json
✓ Profile exported to system-profile.json
```

### Generate Markdown Report

```bash
$ updt profile --output PACKAGES.md --format markdown
✓ Profile exported to PACKAGES.md
```

## Configuration

See {doc}`guides/configuration` for details on configuring updt behavior.

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid configuration
