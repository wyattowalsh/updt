"""Pip package manager plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class PipPlugin(PluginBase):
    """Plugin for Pip package manager."""

    async def is_available(self) -> bool:
        """Check if pip is available."""
        try:
            stdout, _, exit_code = await self.run_command(["pip", "--version"], timeout=10)
            return exit_code == 0 and "pip" in stdout
        except Exception as e:
            logger.debug(f"Pip not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Pip updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check for outdated packages
        try:
            stdout, _, exit_code = await self.run_command(
                ["pip", "list", "--outdated", "--format=columns"],
                timeout=60,
            )

            if exit_code == 0 and stdout:
                # Parse pip list --outdated output
                # Package    Version  Latest   Type
                lines = stdout.strip().split("\n")
                for line in lines[2:]:  # Skip header lines
                    parts = line.split()
                    if len(parts) >= 3:
                        package, current, latest = parts[0], parts[1], parts[2]
                        updates.append(
                            UpdateInfo(
                                ecosystem="pip",
                                package=package,
                                current_version=current,
                                latest_version=latest,
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                            )
                        )

            logger.info(f"Found {len(updates)} Pip updates")

        except Exception as e:
            logger.exception(f"Error checking Pip packages: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Pip package update."""
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
            logger.info(f"Updating {update_info.package} via Pip...")
            stdout, stderr, exit_code = await self.run_command(
                ["pip", "install", "--upgrade", update_info.package],
                timeout=300,
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
registry.register(PipPlugin)
