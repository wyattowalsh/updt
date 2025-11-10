"""Homebrew package manager plugin."""

import re
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class BrewPlugin(PluginBase):
    """Plugin for Homebrew package manager."""

    async def is_available(self) -> bool:
        """Check if brew is available."""
        try:
            stdout, _, exit_code = await self.run_command(["brew", "--version"], timeout=10)
            return exit_code == 0 and "Homebrew" in stdout
        except Exception as e:
            logger.debug(f"Brew not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Homebrew updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # Update brew itself
            logger.info("Updating Homebrew package index...")
            await self.run_command(["brew", "update"], timeout=120)

            # Check for outdated packages
            stdout, stderr, exit_code = await self.run_command(
                ["brew", "outdated", "--verbose"],
                timeout=60,
            )

            if exit_code == 0 and stdout:
                for line in stdout.strip().split("\n"):
                    if not line.strip():
                        continue

                    # Parse brew outdated output: "package (current) < latest"
                    match = re.match(r"(\S+)\s+\(([^)]+)\)\s+<\s+(\S+)", line)
                    if match:
                        package, current, latest = match.groups()
                        updates.append(
                            UpdateInfo(
                                ecosystem="brew",
                                package=package,
                                current_version=current,
                                latest_version=latest,
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                            )
                        )

            logger.info(f"Found {len(updates)} Homebrew updates")

        except Exception as e:
            logger.exception(f"Error checking Homebrew updates: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Homebrew package update."""
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
            logger.info(f"Updating {update_info.package} via Homebrew...")
            stdout, stderr, exit_code = await self.run_command(
                ["brew", "upgrade", update_info.package],
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
registry.register(BrewPlugin)
