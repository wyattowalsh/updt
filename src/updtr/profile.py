"""System profile generation for tracking installed packages."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from rich.console import Console
from rich.table import Table

from .models.config import UpdtConfig
from .updater import UpdateManager


class SystemProfile:
    """Generate system profile showing what's installed via which package manager."""

    def __init__(self, config: UpdtConfig):
        """Initialize system profile generator.

        Args:
            config: Application configuration
        """
        self.config = config
        self.console = Console()

    async def generate(
        self, project_path: Path | None = None, output_format: str = "text"
    ) -> dict[str, Any]:
        """Generate system profile.

        Args:
            project_path: Optional project path for local dependencies
            output_format: Output format (text, json, markdown)

        Returns:
            Dictionary containing profile data
        """
        logger.info("Generating system profile...")

        manager = UpdateManager(self.config)
        await manager.initialize()

        profile_data = {
            "generated_at": datetime.now().isoformat(),
            "project_path": str(project_path) if project_path else None,
            "ecosystems": {},
            "summary": {
                "total_ecosystems": 0,
                "total_packages": 0,
                "available_updates": 0,
            },
        }

        # Get all available updates (which includes current packages)
        updates = await manager.check_updates(project_path=project_path)

        # Organize by ecosystem
        for update in updates:
            eco = update.ecosystem
            if eco not in profile_data["ecosystems"]:
                profile_data["ecosystems"][eco] = {
                    "packages": [],
                    "plugin_available": True,
                    "total_packages": 0,
                    "updates_available": 0,
                }

            package_info = {
                "name": update.package,
                "current_version": update.current_version,
                "latest_version": update.latest_version,
                "is_global": update.is_global,
                "has_update": update.latest_version != update.current_version,
                "metadata": update.metadata,
            }

            profile_data["ecosystems"][eco]["packages"].append(package_info)
            profile_data["ecosystems"][eco]["total_packages"] += 1

            if package_info["has_update"]:
                profile_data["ecosystems"][eco]["updates_available"] += 1
                profile_data["summary"]["available_updates"] += 1

        profile_data["summary"]["total_ecosystems"] = len(profile_data["ecosystems"])
        profile_data["summary"]["total_packages"] = sum(
            eco["total_packages"] for eco in profile_data["ecosystems"].values()
        )

        # Output in requested format
        if output_format == "json":
            self._output_json(profile_data)
        elif output_format == "markdown":
            self._output_markdown(profile_data)
        else:
            self._output_text(profile_data)

        return profile_data

    def _output_text(self, data: dict[str, Any]) -> None:
        """Output profile in text format with Rich tables."""
        self.console.print("\n[bold cyan]System Package Profile[/bold cyan]")
        self.console.print(f"Generated: {data['generated_at']}")

        if data["project_path"]:
            self.console.print(f"Project: {data['project_path']}")

        # Summary
        self.console.print("\n[bold]Summary:[/bold]")
        summary = data["summary"]
        self.console.print(f"  • Total Ecosystems: {summary['total_ecosystems']}")
        self.console.print(f"  • Total Packages: {summary['total_packages']}")
        self.console.print(f"  • Updates Available: {summary['available_updates']}")

        # Per-ecosystem tables
        for eco_name, eco_data in sorted(data["ecosystems"].items()):
            self.console.print(f"\n[bold green]📦 {eco_name.upper()}[/bold green]")
            self.console.print(
                f"  Packages: {eco_data['total_packages']} | "
                f"Updates: {eco_data['updates_available']}"
            )

            if eco_data["packages"]:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Package", style="cyan")
                table.add_column("Current", style="yellow")
                table.add_column("Latest", style="green")
                table.add_column("Scope")
                table.add_column("Status")

                for pkg in sorted(eco_data["packages"], key=lambda x: x["name"]):
                    scope = "Global" if pkg["is_global"] else "Local"
                    status = "⬆ Update" if pkg["has_update"] else "✓ Current"
                    status_style = "[yellow]" if pkg["has_update"] else "[green]"

                    table.add_row(
                        pkg["name"],
                        pkg["current_version"] or "—",
                        pkg["latest_version"] or "—",
                        scope,
                        f"{status_style}{status}[/]",
                    )

                self.console.print(table)

    def _output_json(self, data: dict[str, Any]) -> None:
        """Output profile in JSON format."""
        self.console.print(json.dumps(data, indent=2, default=str))

    def _output_markdown(self, data: dict[str, Any]) -> None:
        """Output profile in Markdown format."""
        md_lines = [
            "# System Package Profile",
            "",
            f"**Generated:** {data['generated_at']}",
        ]

        if data["project_path"]:
            md_lines.append(f"**Project:** {data['project_path']}")

        md_lines.extend(
            [
                "",
                "## Summary",
                "",
                f"- **Total Ecosystems:** {data['summary']['total_ecosystems']}",
                f"- **Total Packages:** {data['summary']['total_packages']}",
                f"- **Updates Available:** {data['summary']['available_updates']}",
                "",
                "## Ecosystems",
                "",
            ]
        )

        for eco_name, eco_data in sorted(data["ecosystems"].items()):
            md_lines.extend(
                [
                    f"### {eco_name.upper()}",
                    "",
                    f"- **Packages:** {eco_data['total_packages']}",
                    f"- **Updates Available:** {eco_data['updates_available']}",
                    "",
                    "| Package | Current | Latest | Scope | Status |",
                    "|---------|---------|--------|-------|--------|",
                ]
            )

            for pkg in sorted(eco_data["packages"], key=lambda x: x["name"]):
                scope = "Global" if pkg["is_global"] else "Local"
                status = "⬆ Update" if pkg["has_update"] else "✓ Current"
                md_lines.append(
                    f"| {pkg['name']} | {pkg['current_version'] or '—'} | "
                    f"{pkg['latest_version'] or '—'} | {scope} | {status} |"
                )

            md_lines.append("")

        self.console.print("\n".join(md_lines))

    async def export_to_file(
        self,
        output_path: Path,
        project_path: Path | None = None,
        format: str = "json",
    ) -> None:
        """Export profile to file.

        Args:
            output_path: Path to output file
            project_path: Optional project path
            format: Output format (json, markdown)
        """
        profile_data = await self.generate(
            project_path=project_path, output_format="json"
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "markdown":
            # Convert to markdown
            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()

            self._output_markdown(profile_data)

            sys.stdout = old_stdout
            content = buffer.getvalue()
            output_path.write_text(content)
        else:
            # JSON
            with output_path.open("w") as f:
                json.dump(profile_data, f, indent=2, default=str)

        logger.info(f"Profile exported to {output_path}")
