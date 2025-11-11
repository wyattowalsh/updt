# API Reference

Python API documentation for updtr.

## Core Modules

```{toctree}
:maxdepth: 2

../reference/index
```

## Quick Links

- {py:mod}`updtr.cli` - Command-line interface
- {py:mod}`updtr.updater` - Core update manager
- {py:mod}`updtr.profile` - System profiling
- {py:mod}`updtr.models.config` - Configuration models
- {py:mod}`updtr.models.update` - Update data models
- {py:mod}`updtr.plugins.base` - Plugin base class
- {py:mod}`updtr.plugins.registry` - Plugin registry

## Module Overview

### CLI Module

The main entry point for the command-line interface built with Typer.

### UpdateManager

Core orchestration class that manages multiple plugins and coordinates update operations.

### SystemProfile

Generates comprehensive reports of installed packages across all ecosystems.

### Models

Pydantic models for type-safe configuration and data handling.

### Plugins

Extensible plugin system for supporting different package managers.

Each plugin implements the `PluginBase` interface with three key methods:
- `is_available()` - Check if the package manager is installed
- `check_updates()` - Detect available updates
- `perform_update()` - Apply updates

## Auto-generated API Documentation

The complete API documentation is auto-generated from source code docstrings:

```{toctree}
:maxdepth: 3
:glob:

../reference/updtr*
```
