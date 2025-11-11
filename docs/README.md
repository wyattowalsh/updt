# updt Documentation

This directory contains the Sphinx documentation for updt.

## Building Documentation

### Install Dependencies

```bash
uv sync --all-extras
```

### Build HTML

```bash
cd docs
uv run sphinx-build -b html source _build/html
```

### View Documentation

```bash
# macOS
open _build/html/index.html

# Linux
xdg-open _build/html/index.html
```

## Documentation Structure

- `source/` - Documentation source files (MyST Markdown + rST)
  - `index.md` - Main landing page
  - `cli.md` - CLI reference
  - `guides/` - User guides
  - `api/` - API reference
  - `_static/` - Static assets (CSS, JS, images)
  - `_templates/` - Custom templates
  - `conf.py` - Sphinx configuration

## Extensions Used

- **shibuya** - Modern Sphinx theme
- **myst-parser** - Markdown support
- **sphinx-autodoc2** - API documentation from source
- **sphinx-click** - CLI documentation
- **sphinx-design** - Grid layouts and components
- **sphinxcontrib-mermaid** - Diagram support
- Plus many more (see conf.py)

## Contributing to Documentation

1. Edit files in `source/`
2. Build locally to preview changes
3. Submit PR with documentation updates

See `AGENTS.md` for development guidelines.
