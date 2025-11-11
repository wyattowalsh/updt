"""Pipx package manager plugin."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class PipxPlugin(PluginBase):
    """Plugin for Pipx - Install and run Python applications in isolated environments."""

    async def is_available(self) -> bool:
        """Check if pipx is available."""
        try:
            stdout, _, exit_code = await self.run_command(["pipx", "--version"], timeout=10)
            return exit_code == 0 and stdout.strip()
        except Exception as e:
            logger.debug(f"Pipx not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Pipx updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # List all installed pipx packages
            logger.info("Checking pipx packages for updates...")
            stdout, _, exit_code = await self.run_command(
                ["pipx", "list", "--json"],
                timeout=60,
            )

            if exit_code == 0 and stdout:
                try:
                    data = json.loads(stdout)
                    venvs = data.get("venvs", {})

                    for pkg_name, pkg_info in venvs.items():
                        metadata = pkg_info.get("metadata", {})
                        main_package = metadata.get("main_package", {})
                        current_version = main_package.get("package_version")

                        # Check if update is available
                        # pipx doesn't provide a direct way to check for updates
                        # We mark packages as potentially updatable
                        if current_version:
                            updates.append(
                                UpdateInfo(
                                    ecosystem="pipx",
                                    package=pkg_name,
                                    current_version=current_version,
                                    latest_version=None,  # Would need to check PyPI
                                    is_global=True,
                                    status=UpdateStatus.PENDING,
                                    message="Use 'pipx upgrade' to check for updates",
                                )
                            )

                except json.JSONDecodeError:
                    logger.warning("Failed to parse pipx list output")

            # Try to get outdated packages using upgrade with dry-run
            stdout2, _, exit_code2 = await self.run_command(
                ["pipx", "upgrade-all", "--dry-run"],
                timeout=120,
            )

            if exit_code2 == 0 and stdout2:
                # Parse output for packages that would be upgraded
                for line in stdout2.split("\n"):
                    if "upgraded from" in line.lower() or "would upgrade" in line.lower():
                        # Extract package name and versions
                        # Format varies, but typically: "Would upgrade package from x.y.z to a.b.c"
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.lower() in ["upgrade", "upgraded"]:
                                if i + 1 < len(parts):
                                    pkg_name = parts[i + 1]
                                    # Try to find current and latest versions
                                    for j, p in enumerate(parts):
                                        if p.lower() == "from" and j + 1 < len(parts):
                                            current = parts[j + 1]
                                        if p.lower() == "to" and j + 1 < len(parts):
                                            latest = parts[j + 1]

                                    # Update the status if we found this package
                                    for update in updates:
                                        if update.package == pkg_name:
                                            if 'latest' in locals():
                                                update.latest_version = latest
                                            update.status = UpdateStatus.AVAILABLE
                                            break

            logger.info(f"Found {len(updates)} pipx packages")

        except Exception as e:
            logger.exception(f"Error checking pipx packages: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Pipx package update."""
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
            logger.info(f"Updating {update_info.package} via pipx...")
            stdout, stderr, exit_code = await self.run_command(
                ["pipx", "upgrade", update_info.package],
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
registry.register(PipxPlugin)
