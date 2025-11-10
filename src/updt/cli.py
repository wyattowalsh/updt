"""Command-line interface using Typer."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from . import __version__
from .logging import setup_logging
from .models.config import UpdtConfig

# Import plugins to register them
from .plugins import brew, cargo, npm, pip, uv_plugin  # noqa: F401
from .updater import UpdateManager

app = typer.Typer(
    name="updt",
    help="Universal package dependency tracker and updater",
    add_completion=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"updt version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, help="Show version and exit"),
    ] = None,
) -> None:
    """Universal package dependency tracker and updater."""
    pass


@app.command()
def check(
    project: Annotated[
        Path | None,
        typer.Option("--project", "-p", help="Project directory to check"),
    ] = None,
    config_file: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Configuration file path"),
    ] = None,
    log_level: Annotated[
        str | None,
        typer.Option("--log-level", "-l", help="Log level"),
    ] = None,
) -> None:
    """Check for available updates across all package managers."""
    # Load configuration
    config = UpdtConfig()
    if log_level:
        config.log_level = log_level.upper()  # type: ignore

    setup_logging(config)
    logger.info("Starting update check...")

    async def _check() -> None:
        """Async check implementation."""
        manager = UpdateManager(config)
        await manager.initialize()

        updates = await manager.check_all_updates(project_path=project)

        if not updates:
            console.print("[green]✓[/green] All packages are up to date!")
            return

        # Display results in a table
        table = Table(title=f"Available Updates ({len(updates)})")
        table.add_column("Ecosystem", style="cyan")
        table.add_column("Package", style="magenta")
        table.add_column("Current", style="yellow")
        table.add_column("Latest", style="green")
        table.add_column("Type", style="blue")

        for update in updates:
            table.add_row(
                update.ecosystem,
                update.package,
                update.current_version or "N/A",
                update.latest_version or "N/A",
                "Global" if update.is_global else "Project",
            )

        console.print(table)

    asyncio.run(_check())


@app.command()
def update(
    project: Annotated[
        Path | None,
        typer.Option("--project", "-p", help="Project directory to update"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Perform a dry run without actual updates"),
    ] = False,
    config_file: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Configuration file path"),
    ] = None,
    log_level: Annotated[
        str | None,
        typer.Option("--log-level", "-l", help="Log level"),
    ] = None,
) -> None:
    """Update all packages across all package managers."""
    # Load configuration
    config = UpdtConfig()
    config.dry_run = dry_run
    if log_level:
        config.log_level = log_level.upper()  # type: ignore

    setup_logging(config)

    if dry_run:
        logger.info("Starting update in DRY RUN mode...")
    else:
        logger.info("Starting update...")

    async def _update() -> None:
        """Async update implementation."""
        manager = UpdateManager(config)
        await manager.initialize()

        # Check for updates
        updates = await manager.check_all_updates(project_path=project)

        if not updates:
            console.print("[green]✓[/green] All packages are up to date!")
            return

        console.print(f"\n[bold]Found {len(updates)} updates[/bold]\n")

        # Perform updates
        results = await manager.perform_updates(updates, dry_run=dry_run)

        # Display results
        table = Table(title="Update Results")
        table.add_column("Package", style="magenta")
        table.add_column("Status", style="cyan")
        table.add_column("Message")

        for result in results:
            status_emoji = {
                "success": "✓",
                "failed": "✗",
                "skipped": "⊘",
            }.get(result.status.value, "?")

            status_color = {
                "success": "green",
                "failed": "red",
                "skipped": "yellow",
            }.get(result.status.value, "white")

            table.add_row(
                result.update_info.package,
                f"[{status_color}]{status_emoji} {result.status.value}[/{status_color}]",
                result.message,
            )

        console.print(table)

    asyncio.run(_update())


@app.command()
def config(
    show: Annotated[
        bool,
        typer.Option("--show", "-s", help="Show current configuration"),
    ] = False,
) -> None:
    """Manage updt configuration."""
    config = UpdtConfig()

    if show:
        console.print("[bold]Current Configuration:[/bold]\n")
        console.print(f"Log Level: {config.log_level}")
        console.print(f"Log Format: {config.log_format}")
        console.print(f"Default Mode: {config.default_mode}")
        console.print(f"Dry Run: {config.dry_run}")
        console.print(f"Max Concurrent Updates: {config.max_concurrent_updates}")
        console.print(f"Timeout: {config.timeout}s")
        console.print("\n[bold]Enabled Ecosystems:[/bold]")

        for name, enabled in config.ecosystems.model_dump().items():
            status = "✓" if enabled else "✗"
            color = "green" if enabled else "red"
            console.print(f"  [{color}]{status}[/{color}] {name}")


if __name__ == "__main__":
    app()
