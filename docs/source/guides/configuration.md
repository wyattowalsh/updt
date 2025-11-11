# Configuration Guide

Learn how to configure updtr for your needs.

## Configuration Sources

updtr loads configuration from multiple sources (in order of precedence):

1. Environment variables (prefixed with `UPDTR_`)
2. `.env` file in current directory
3. `pyproject.toml` `[tool.updtr]` section
4. Default values

## Configuration Options

See {doc}`../api/index` for complete configuration schema.
