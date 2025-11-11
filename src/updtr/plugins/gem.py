"""RubyGems package manager plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class GemPlugin(PluginBase):
    """Plugin for RubyGems package manager."""

    async def is_available(self) -> bool:
        """Check if gem is available."""
        try:
            stdout, _, exit_code = await self.run_command(["gem", "--version"], timeout=10)
            return exit_code == 0 and stdout.strip()
        except Exception as e:
            logger.debug(f"Gem not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Gem updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # Check for outdated gems
            logger.info("Checking for outdated gems...")
            stdout, _, exit_code = await self.run_command(
                ["gem", "outdated"],
                timeout=120,
            )

            if exit_code == 0 and stdout:
                # Parse gem outdated output
                # Format: "gem_name (current version < latest version)"
                for line in stdout.strip().split("\n"):
                    if "(" in line and "<" in line:
                        # Extract package name and versions
                        parts = line.split("(")
                        if len(parts) >= 2:
                            package = parts[0].strip()
                            version_part = parts[1].rstrip(")")

                            if "<" in version_part:
                                version_parts = version_part.split("<")
                                current = version_parts[0].strip()
                                latest = (
                                    version_parts[1].strip() if len(version_parts) > 1 else None
                                )

                                updates.append(
                                    UpdateInfo(
                                        ecosystem="gem",
                                        package=package,
                                        current_version=current,
                                        latest_version=latest,
                                        is_global=True,
                                        status=UpdateStatus.AVAILABLE,
                                    )
                                )

            logger.info(f"Found {len(updates)} gem updates")

        except Exception as e:
            logger.exception(f"Error checking gems: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Gem package update."""
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
            logger.info(f"Updating {update_info.package} via gem...")
            stdout, stderr, exit_code = await self.run_command(
                ["gem", "update", update_info.package],
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
registry.register(GemPlugin)
