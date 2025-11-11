"""Pyenv (Python Version Manager) plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class PyenvPlugin(PluginBase):
    """Plugin for Pyenv - Python Version Manager."""

    async def is_available(self) -> bool:
        """Check if pyenv is available."""
        try:
            stdout, _, exit_code = await self.run_command(["pyenv", "--version"], timeout=10)
            return exit_code == 0 and "pyenv" in stdout.lower()
        except Exception as e:
            logger.debug(f"Pyenv not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Pyenv and Python version updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # Check installed Python versions
            logger.info("Checking pyenv for Python version updates...")
            stdout, _, exit_code = await self.run_command(
                ["pyenv", "versions", "--bare"],
                timeout=30,
            )

            installed_versions = []
            if exit_code == 0 and stdout:
                installed_versions = [v.strip() for v in stdout.split("\n") if v.strip()]

            # Update pyenv's knowledge of available versions
            await self.run_command(["pyenv", "update"], timeout=60)

            # Check for latest stable Python version
            stdout2, _, exit_code2 = await self.run_command(
                ["pyenv", "install", "--list"],
                timeout=30,
            )

            if exit_code2 == 0 and stdout2:
                # Find latest stable 3.x version (not pre-release)
                latest_version = None
                for line in reversed(stdout2.split("\n")):
                    line = line.strip()
                    if line.startswith("3.") and not any(
                        x in line for x in ["a", "b", "rc", "dev"]
                    ):
                        latest_version = line
                        break

                if latest_version and latest_version not in installed_versions:
                    current = installed_versions[0] if installed_versions else None
                    updates.append(
                        UpdateInfo(
                            ecosystem="pyenv",
                            package="python",
                            current_version=current,
                            latest_version=latest_version,
                            is_global=True,
                            status=UpdateStatus.AVAILABLE,
                            message="Latest stable Python version available",
                        )
                    )

            logger.info(f"Found {len(updates)} pyenv updates")

        except Exception as e:
            logger.exception(f"Error checking pyenv: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Pyenv update."""
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
            # Install new Python version
            logger.info(f"Installing Python {update_info.latest_version} via pyenv...")
            stdout, stderr, exit_code = await self.run_command(
                ["pyenv", "install", update_info.latest_version or ""],
                timeout=1200,  # Python compilation can take a while
            )

            duration = (datetime.now() - start_time).total_seconds()

            if exit_code == 0:
                return UpdateResult(
                    update_info=update_info,
                    status=UpdateStatus.SUCCESS,
                    message=f"Successfully installed Python {update_info.latest_version}",
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
                    message=f"Failed to install {update_info.latest_version}",
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
registry.register(PyenvPlugin)
