# Configuration Guide

Learn how to configure updt for your needs.

## Configuration Sources

updt loads configuration from multiple sources (in order of precedence):

1. Environment variables (prefixed with `UPDT_`)
2. `.env` file in current directory
3. `pyproject.toml` `[tool.updt]` section
4. Default values

## Configuration Options

See {doc}`../api/index` for complete configuration schema.
