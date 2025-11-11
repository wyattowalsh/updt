"""NVM (Node Version Manager) plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class NvmPlugin(PluginBase):
    """Plugin for NVM - Node Version Manager."""

    async def is_available(self) -> bool:
        """Check if nvm is available."""
        try:
            # NVM is typically a shell function, so we check for the installation
            stdout, _, exit_code = await self.run_command(
                ["bash", "-c", "source ~/.nvm/nvm.sh && nvm --version"],
                timeout=10,
            )
            return exit_code == 0 and stdout.strip()
        except Exception as e:
            logger.debug(f"NVM not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available NVM and Node.js version updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # Check installed Node versions
            logger.info("Checking NVM for Node.js version updates...")
            stdout, _, exit_code = await self.run_command(
                ["bash", "-c", "source ~/.nvm/nvm.sh && nvm list"],
                timeout=30,
            )

            if exit_code == 0 and stdout:
                # Parse installed versions
                installed_versions = []
                for line in stdout.split("\n"):
                    line = line.strip()
                    if line and ("v" in line or "node" in line.lower()):
                        # Extract version number
                        if "->" in line:
                            # Current version
                            parts = line.split("->")
                            if len(parts) > 1:
                                version = parts[1].strip().split()[0]
                                installed_versions.append(version)
                        elif line.startswith("v"):
                            version = line.split()[0]
                            installed_versions.append(version)

                # Check for latest LTS version
                stdout2, _, exit_code2 = await self.run_command(
                    ["bash", "-c", "source ~/.nvm/nvm.sh && nvm list-remote --lts | tail -1"],
                    timeout=60,
                )

                if exit_code2 == 0 and stdout2:
                    latest_lts = stdout2.strip().split()[0] if stdout2.strip() else None

                    if latest_lts and installed_versions:
                        # Check if latest LTS is installed
                        if latest_lts not in installed_versions:
                            current = installed_versions[0] if installed_versions else None
                            updates.append(
                                UpdateInfo(
                                    ecosystem="nvm",
                                    package="node-lts",
                                    current_version=current,
                                    latest_version=latest_lts,
                                    is_global=True,
                                    status=UpdateStatus.AVAILABLE,
                                    message="Latest LTS version available",
                                )
                            )

                # Check for NVM itself
                cmd = (
                    "cd ~/.nvm && git fetch --tags && "
                    "git describe --tags `git rev-list --tags --max-count=1`"
                )
                stdout3, _, exit_code3 = await self.run_command(
                    ["bash", "-c", cmd],
                    timeout=30,
                )

                if exit_code3 == 0 and stdout3:
                    latest_nvm = stdout3.strip()
                    current_nvm, _, _ = await self.run_command(
                        ["bash", "-c", "source ~/.nvm/nvm.sh && nvm --version"],
                        timeout=10,
                    )
                    current_nvm = current_nvm.strip()

                    if latest_nvm and current_nvm and latest_nvm != current_nvm:
                        updates.append(
                            UpdateInfo(
                                ecosystem="nvm",
                                package="nvm",
                                current_version=current_nvm,
                                latest_version=latest_nvm,
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                                message="NVM version manager update available",
                            )
                        )

            logger.info(f"Found {len(updates)} NVM updates")

        except Exception as e:
            logger.exception(f"Error checking NVM: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform an NVM update."""
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
            if update_info.package == "nvm":
                logger.info("Updating NVM itself...")
                cmd = (
                    "cd ~/.nvm && git fetch --tags && "
                    "git checkout `git describe --tags $(git rev-list --tags --max-count=1)`"
                )
                stdout, stderr, exit_code = await self.run_command(
                    ["bash", "-c", cmd],
                    timeout=120,
                )
            else:
                # Install new Node version
                logger.info(f"Installing Node.js {update_info.latest_version} via NVM...")
                cmd = f"source ~/.nvm/nvm.sh && nvm install {update_info.latest_version}"
                stdout, stderr, exit_code = await self.run_command(
                    ["bash", "-c", cmd],
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
registry.register(NvmPlugin)
