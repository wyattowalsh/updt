"""Flatpak plugin for Linux desktop applications."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class FlatpakPlugin(PluginBase):
    """Plugin for Flatpak package manager."""

    async def is_available(self) -> bool:
        """Check if flatpak is available."""
        try:
            stdout, _, exit_code = await self.run_command(["flatpak", "--version"], timeout=10)
            return exit_code == 0 and "flatpak" in stdout.lower()
        except Exception as e:
            logger.debug(f"flatpak not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available updates via flatpak."""
        if not await self.is_available():
            return []

        updates = []
        try:
            # Get list of outdated packages
            stdout, _, exit_code = await self.run_command(
                ["flatpak", "remote-ls", "--updates", "--columns=application,version,branch"],
                timeout=60,
            )

            if exit_code == 0 and stdout:
                for line in stdout.splitlines():
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        app_id = parts[0]
                        latest = parts[1] if len(parts) > 1 else "unknown"

                        # Get current version
                        current_stdout, _, _ = await self.run_command(
                            ["flatpak", "info", app_id], timeout=10
                        )

                        current = "unknown"
                        if current_stdout:
                            for info_line in current_stdout.splitlines():
                                if info_line.strip().startswith("Version:"):
                                    current = info_line.split(":", 1)[1].strip()
                                    break

                        updates.append(
                            UpdateInfo(
                                ecosystem="flatpak",
                                package=app_id,
                                current_version=current,
                                latest_version=latest,
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                            )
                        )

            logger.info(f"Found {len(updates)} flatpak updates")
        except Exception as e:
            logger.error(f"Error checking flatpak updates: {e}")

        return updates

    async def perform_update(
        self, update_info: UpdateInfo, dry_run: bool = False
    ) -> UpdateResult:
        """Perform a flatpak update."""
        start_time = datetime.now()

        try:
            if dry_run:
                return UpdateResult(
                    update_info=update_info,
                    status=UpdateStatus.SKIPPED,
                    message=f"[DRY RUN] Would update {update_info.package}",
                    timestamp=start_time,
                    duration=(datetime.now() - start_time).total_seconds(),
                )

            # Perform update
            stdout, stderr, exit_code = await self.run_command(
                ["flatpak", "update", "-y", update_info.package], timeout=600
            )

            if exit_code == 0:
                return UpdateResult(
                    update_info=update_info,
                    status=UpdateStatus.SUCCESS,
                    message=f"Successfully updated {update_info.package}",
                    timestamp=start_time,
                    duration=(datetime.now() - start_time).total_seconds(),
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
                    duration=(datetime.now() - start_time).total_seconds(),
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                )

        except Exception as e:
            logger.exception(f"Error updating {update_info.package}")
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.FAILED,
                message=f"Error: {str(e)}",
                timestamp=start_time,
                duration=(datetime.now() - start_time).total_seconds(),
            )


registry.register(FlatpakPlugin)
