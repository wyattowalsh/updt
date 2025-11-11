"""Cargo (Rust) package manager plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class CargoPlugin(PluginBase):
    """Plugin for Cargo (Rust) package manager."""

    async def is_available(self) -> bool:
        """Check if cargo is available."""
        try:
            stdout, _, exit_code = await self.run_command(["cargo", "--version"], timeout=10)
            return exit_code == 0 and "cargo" in stdout
        except Exception as e:
            logger.debug(f"Cargo not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Cargo updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check for cargo-update plugin to manage installed binaries
        try:
            stdout, _, exit_code = await self.run_command(
                ["cargo", "install", "--list"],
                timeout=30,
            )
            if exit_code == 0:
                logger.info("Cargo binaries found - install cargo-update for update checking")
                # Note: cargo install-update --list would show updates if cargo-update is installed
        except Exception as e:
            logger.exception(f"Error checking Cargo binaries: {e}")

        # Check project dependencies if Cargo.toml exists
        if project_path:
            cargo_toml = project_path / "Cargo.toml"
            if cargo_toml.exists():
                try:
                    # cargo outdated would show outdated dependencies if installed
                    logger.info(f"Found Cargo.toml in {project_path}")
                    logger.info("Install cargo-outdated for dependency update checking")
                except Exception as e:
                    logger.exception(f"Error checking Cargo project: {e}")

        logger.info(f"Found {len(updates)} Cargo updates")
        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Cargo package update."""
        start_time = datetime.now()

        if dry_run:
            logger.info(f"[DRY RUN] Would update {update_info.package}")
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.SKIPPED,
                message="Dry run - no actual update performed",
                timestamp=start_time,
                duration=0.0,
            )

        try:
            logger.info(f"Updating {update_info.package} via Cargo...")
            stdout, stderr, exit_code = await self.run_command(
                ["cargo", "install", "--force", update_info.package],
                timeout=600,
            )

            duration = (datetime.now() - start_time).total_seconds()

            if exit_code == 0:
                return UpdateResult(
                    update_info=update_info,
                    status=UpdateStatus.SUCCESS,
                    message=f"Successfully updated {update_info.package}",
                    timestamp=start_time,
                    duration=duration,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                )
            else:
                return UpdateResult(
                    update_info=update_info,
                    status=UpdateStatus.FAILED,
                    message=f"Failed to update {update_info.package}",
                    timestamp=start_time,
                    duration=duration,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.exception(f"Error updating {update_info.package}: {e}")
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.FAILED,
                message=f"Error: {str(e)}",
                timestamp=start_time,
                duration=duration,
            )


# Register the plugin
registry.register(CargoPlugin)
