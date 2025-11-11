# API Reference

Python API documentation for updt.

## Core Modules

```{toctree}
:maxdepth: 2

../reference/index
```

## Quick Links

- {py:mod}`updt.cli` - Command-line interface
- {py:mod}`updt.updater` - Core update manager
- {py:mod}`updt.profile` - System profiling
- {py:mod}`updt.models.config` - Configuration models
- {py:mod}`updt.models.update` - Update data models
- {py:mod}`updt.plugins.base` - Plugin base class
- {py:mod}`updt.plugins.registry` - Plugin registry

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

../reference/updt*
```
