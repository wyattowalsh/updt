"""APT (Advanced Package Tool) plugin for Debian/Ubuntu systems."""

import json
import re
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class AptPlugin(PluginBase):
    """Plugin for APT package manager (Debian, Ubuntu, etc.)."""

    async def is_available(self) -> bool:
        """Check if apt is available."""
        try:
            stdout, _, exit_code = await self.run_command(["apt", "--version"], timeout=10)
            return exit_code == 0 and "apt" in stdout.lower()
        except Exception as e:
            logger.debug(f"apt not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available updates via apt."""
        if not await self.is_available():
            return []

        updates = []
        try:
            # Update package index first
            _, _, exit_code = await self.run_command(
                ["sudo", "-n", "apt", "update"], timeout=120
            )
            if exit_code != 0:
                logger.warning("Could not update apt index (sudo required)")
                # Continue anyway to show outdated packages

            # List upgradable packages
            stdout, _, exit_code = await self.run_command(
                ["apt", "list", "--upgradable"], timeout=60
            )

            if exit_code == 0 and stdout:
                for line in stdout.splitlines():
                    # Format: package/suite version arch [upgradable from: oldversion]
                    match = re.match(
                        r"^([^/]+)/\S+\s+(\S+)\s+\S+\s+\[upgradable from:\s+(\S+)\]",
                        line.strip(),
                    )
                    if match:
                        package, latest, current = match.groups()
                        updates.append(
                            UpdateInfo(
                                ecosystem="apt",
                                package=package,
                                current_version=current,
                                latest_version=latest,
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                            )
                        )

            logger.info(f"Found {len(updates)} apt updates")
        except Exception as e:
            logger.error(f"Error checking apt updates: {e}")

        return updates

    async def perform_update(
        self, update_info: UpdateInfo, dry_run: bool = False
    ) -> UpdateResult:
        """Perform an apt update."""
        start_time = datetime.now()

        try:
            if dry_run:
                return UpdateResult(
                    update_info=update_info,
                    status=UpdateStatus.SKIPPED,
                    message=f"[DRY RUN] Would upgrade {update_info.package}",
                    timestamp=start_time,
                    duration=(datetime.now() - start_time).total_seconds(),
                )

            # Perform upgrade (requires sudo)
            stdout, stderr, exit_code = await self.run_command(
                ["sudo", "-n", "apt", "install", "-y", update_info.package], timeout=600
            )

            if exit_code == 0:
                return UpdateResult(
                    update_info=update_info,
                    status=UpdateStatus.SUCCESS,
                    message=f"Successfully upgraded {update_info.package}",
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
                    message=f"Failed to upgrade {update_info.package}",
                    timestamp=start_time,
                    duration=(datetime.now() - start_time).total_seconds(),
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                )

        except Exception as e:
            logger.exception(f"Error upgrading {update_info.package}")
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.FAILED,
                message=f"Error: {str(e)}",
                timestamp=start_time,
                duration=(datetime.now() - start_time).total_seconds(),
            )


registry.register(AptPlugin)
