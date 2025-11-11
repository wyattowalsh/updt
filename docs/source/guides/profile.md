# System Profiling

Generate comprehensive reports of installed packages.

## Basic Usage

```bash
updt profile
```

## Export Formats

- Text (default) - Rich terminal output
- JSON - Machine-readable format
- Markdown - Documentation-friendly format

## Examples

```bash
# Export as JSON
updt profile --output system.json

# Export as Markdown
updt profile --output PACKAGES.md --format markdown
```
