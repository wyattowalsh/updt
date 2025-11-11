"""DNF (Dandified YUM) plugin for Fedora/RHEL systems."""

import json
import re
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class DnfPlugin(PluginBase):
    """Plugin for DNF package manager (Fedora, RHEL, CentOS, etc.)."""

    async def is_available(self) -> bool:
        """Check if dnf is available."""
        try:
            stdout, _, exit_code = await self.run_command(["dnf", "--version"], timeout=10)
            return exit_code == 0 and "dnf" in stdout.lower()
        except Exception as e:
            logger.debug(f"dnf not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available updates via dnf."""
        if not await self.is_available():
            return []

        updates = []
        try:
            # Check for updates
            stdout, _, exit_code = await self.run_command(
                ["dnf", "check-update", "--quiet"], timeout=120
            )

            # dnf check-update returns 100 if updates are available, 0 if not
            if exit_code in (0, 100) and stdout:
                for line in stdout.splitlines():
                    # Skip empty lines and headers
                    line = line.strip()
                    if not line or line.startswith(("Last", "Security", "Obsoleting")):
                        continue

                    # Format: package.arch version repo
                    parts = line.split()
                    if len(parts) >= 2:
                        package_arch = parts[0]
                        latest = parts[1]

                        # Remove architecture suffix
                        package = package_arch.rsplit(".", 1)[0]

                        # Get current version
                        current_stdout, _, _ = await self.run_command(
                            ["rpm", "-q", package, "--queryformat", "%{VERSION}-%{RELEASE}"],
                            timeout=10,
                        )
                        current = current_stdout.strip() if current_stdout else "unknown"

                        updates.append(
                            UpdateInfo(
                                ecosystem="dnf",
                                package=package,
                                current_version=current,
                                latest_version=latest,
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                            )
                        )

            logger.info(f"Found {len(updates)} dnf updates")
        except Exception as e:
            logger.error(f"Error checking dnf updates: {e}")

        return updates

    async def perform_update(
        self, update_info: UpdateInfo, dry_run: bool = False
    ) -> UpdateResult:
        """Perform a dnf update."""
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
                ["sudo", "-n", "dnf", "upgrade", "-y", update_info.package], timeout=600
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


registry.register(DnfPlugin)
