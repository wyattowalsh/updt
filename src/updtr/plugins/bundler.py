"""Bundler (Ruby) dependency manager plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class BundlerPlugin(PluginBase):
    """Plugin for Bundler - Ruby dependency manager."""

    async def is_available(self) -> bool:
        """Check if bundler is available."""
        try:
            stdout, _, exit_code = await self.run_command(["bundle", "--version"], timeout=10)
            return exit_code == 0 and "Bundler" in stdout
        except Exception as e:
            logger.debug(f"Bundler not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Bundler updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check project dependencies
        if project_path:
            gemfile = project_path / "Gemfile"

            if gemfile.exists():
                try:
                    logger.info(f"Checking Bundler project in {project_path}")

                    # Run bundle outdated
                    stdout, _, exit_code = await self.run_command(
                        ["bundle", "outdated", "--parseable"],
                        cwd=project_path,
                        timeout=120,
                    )

                    if exit_code == 0 and stdout:
                        # Parse parseable output
                        # Format: "gem_name (newest version, installed version, requested version)"
                        for line in stdout.strip().split("\n"):
                            if line.strip():
                                # Parse: "package_name (newest X, installed Y, requested Z)"
                                if "(" in line:
                                    parts = line.split("(")
                                    package = parts[0].strip()

                                    if len(parts) > 1:
                                        version_info = parts[1].rstrip(")").split(",")

                                        # Extract versions
                                        current = None
                                        latest = None

                                        for info in version_info:
                                            info = info.strip()
                                            if info.startswith("newest"):
                                                latest = info.split()[-1]
                                            elif info.startswith("installed"):
                                                current = info.split()[-1]

                                        if package and latest:
                                            updates.append(
                                                UpdateInfo(
                                                    ecosystem="bundler",
                                                    package=package,
                                                    current_version=current,
                                                    latest_version=latest,
                                                    is_global=False,
                                                    project_path=str(project_path),
                                                    status=UpdateStatus.AVAILABLE,
                                                )
                                            )

                except Exception as e:
                    logger.exception(f"Error checking Bundler project: {e}")

        logger.info(f"Found {len(updates)} bundler updates")
        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Bundler package update."""
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
            logger.info(f"Updating {update_info.package} via bundler...")
            project_path = Path(update_info.project_path) if update_info.project_path else None

            stdout, stderr, exit_code = await self.run_command(
                ["bundle", "update", update_info.package],
                cwd=project_path,
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
registry.register(BundlerPlugin)
