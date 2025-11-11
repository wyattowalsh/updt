# Contributing to updt

We welcome contributions! Please see AGENTS.md for development guidelines.

## Development Setup

```bash
git clone https://github.com/wyattowalsh/updt.git
cd updt
uv sync --all-extras
```

## Running Tests

```bash
uv run pytest
```

## Code Style

```bash
uv run ruff check .
```

## Building Documentation

```bash
cd docs
uv run sphinx-build -b html source _build/html
```
