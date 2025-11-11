# System Profiling

Generate comprehensive reports of installed packages.

## Basic Usage

```bash
updtr profile
```

## Export Formats

- Text (default) - Rich terminal output
- JSON - Machine-readable format
- Markdown - Documentation-friendly format

## Examples

```bash
# Export as JSON
updtr profile --output system.json

# Export as Markdown
updtr profile --output PACKAGES.md --format markdown
```
