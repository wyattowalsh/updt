"""RVM (Ruby Version Manager) plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class RvmPlugin(PluginBase):
    """Plugin for RVM - Ruby Version Manager."""

    async def is_available(self) -> bool:
        """Check if rvm is available."""
        try:
            stdout, _, exit_code = await self.run_command(
                ["bash", "-c", "source ~/.rvm/scripts/rvm && rvm --version"],
                timeout=10,
            )
            return exit_code == 0 and "rvm" in stdout.lower()
        except Exception as e:
            logger.debug(f"RVM not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available RVM and Ruby version updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # Check installed Ruby versions
            logger.info("Checking RVM for Ruby version updates...")
            stdout, _, exit_code = await self.run_command(
                ["bash", "-c", "source ~/.rvm/scripts/rvm && rvm list"],
                timeout=30,
            )

            installed_versions = []
            if exit_code == 0 and stdout:
                # Parse installed versions
                for line in stdout.split("\n"):
                    line = line.strip()
                    if line and ("ruby" in line.lower() or line.startswith("=")):
                        # Extract version
                        if "=>" in line:
                            # Current version
                            parts = line.split("=>")
                            if len(parts) > 1:
                                version = parts[1].strip().split()[0]
                                installed_versions.append(version)
                        elif "ruby-" in line:
                            version = line.split()[0].replace("=", "").strip()
                            installed_versions.append(version)

            # Check for latest stable Ruby version
            cmd = (
                "source ~/.rvm/scripts/rvm && rvm list known | "
                "grep 'ruby-' | grep -v preview | tail -1"
            )
            stdout2, _, exit_code2 = await self.run_command(
                ["bash", "-c", cmd],
                timeout=30,
            )

            if exit_code2 == 0 and stdout2:
                latest_ruby = stdout2.strip().strip("[]").strip()

                if latest_ruby and installed_versions:
                    # Check if latest is installed
                    latest_installed = False
                    for version in installed_versions:
                        if latest_ruby in version:
                            latest_installed = True
                            break

                    if not latest_installed:
                        current = installed_versions[0] if installed_versions else None
                        updates.append(
                            UpdateInfo(
                                ecosystem="rvm",
                                package="ruby",
                                current_version=current,
                                latest_version=latest_ruby,
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                                message="Latest stable Ruby version available",
                            )
                        )

            # Check for RVM itself
            cmd = "source ~/.rvm/scripts/rvm && rvm get head --version 2>&1 | head -1"
            stdout3, _, exit_code3 = await self.run_command(
                ["bash", "-c", cmd],
                timeout=30,
            )

            if exit_code3 == 0 and "update" in stdout3.lower():
                current_version, _, _ = await self.run_command(
                    ["bash", "-c", "source ~/.rvm/scripts/rvm && rvm --version | head -1"],
                    timeout=10,
                )

                updates.append(
                    UpdateInfo(
                        ecosystem="rvm",
                        package="rvm",
                        current_version=current_version.strip() if current_version else None,
                        latest_version="latest",
                        is_global=True,
                        status=UpdateStatus.AVAILABLE,
                        message="RVM version manager update available",
                    )
                )

            logger.info(f"Found {len(updates)} RVM updates")

        except Exception as e:
            logger.exception(f"Error checking RVM: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform an RVM update."""
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
            if update_info.package == "rvm":
                logger.info("Updating RVM itself...")
                stdout, stderr, exit_code = await self.run_command(
                    ["bash", "-c", "source ~/.rvm/scripts/rvm && rvm get head"],
                    timeout=120,
                )
            else:
                # Install new Ruby version
                logger.info(f"Installing Ruby {update_info.latest_version} via RVM...")
                cmd = f"source ~/.rvm/scripts/rvm && rvm install {update_info.latest_version}"
                stdout, stderr, exit_code = await self.run_command(
                    ["bash", "-c", cmd],
                    timeout=1200,  # Ruby compilation can take a while
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
registry.register(RvmPlugin)
