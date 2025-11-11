"""Conda package manager plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class CondaPlugin(PluginBase):
    """Plugin for Conda package manager."""

    async def is_available(self) -> bool:
        """Check if conda is available."""
        try:
            stdout, _, exit_code = await self.run_command(["conda", "--version"], timeout=10)
            return exit_code == 0 and "conda" in stdout
        except Exception as e:
            logger.debug(f"Conda not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Conda updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # Check for outdated packages in current environment
            logger.info("Checking Conda packages for updates...")
            stdout, _, exit_code = await self.run_command(
                ["conda", "list", "--json"],
                timeout=60,
            )

            if exit_code == 0 and stdout:
                import json

                try:
                    packages = json.loads(stdout)
                    # Get current environment name
                    env_stdout, _, env_exit = await self.run_command(
                        ["conda", "info", "--json"],
                        timeout=30,
                    )

                    env_name = "base"
                    if env_exit == 0:
                        env_info = json.loads(env_stdout)
                        env_name = env_info.get("active_prefix_name", "base")

                    # Check outdated packages
                    for package in packages:
                        pkg_name = package.get("name")
                        if pkg_name:
                            # Note: conda doesn't have a built-in "outdated" command
                            # We log the installed packages
                            logger.debug(f"Conda package: {pkg_name} in {env_name} environment")

                    # Alternative: check conda itself for updates
                    stdout2, _, exit_code2 = await self.run_command(
                        ["conda", "update", "--dry-run", "--all", "--json"],
                        timeout=120,
                    )

                    if exit_code2 == 0 and stdout2:
                        try:
                            update_info = json.loads(stdout2)
                            actions = update_info.get("actions", {})

                            # Check for packages that will be updated
                            for action_type in ["LINK", "FETCH"]:
                                if action_type in actions:
                                    for pkg in actions[action_type]:
                                        pkg_name = pkg.get("name")
                                        pkg_version = pkg.get("version")

                                        if pkg_name and pkg_version:
                                            updates.append(
                                                UpdateInfo(
                                                    ecosystem="conda",
                                                    package=pkg_name,
                                                    current_version=None,  # Not easily available
                                                    latest_version=pkg_version,
                                                    is_global=True,
                                                    status=UpdateStatus.AVAILABLE,
                                                    metadata={"environment": env_name},
                                                )
                                            )
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse conda update output")

                except json.JSONDecodeError:
                    logger.warning("Failed to parse conda list output")

            logger.info(f"Found {len(updates)} Conda updates")

        except Exception as e:
            logger.exception(f"Error checking Conda packages: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Conda package update."""
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
            logger.info(f"Updating {update_info.package} via Conda...")
            stdout, stderr, exit_code = await self.run_command(
                ["conda", "update", "-y", update_info.package],
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
registry.register(CondaPlugin)
