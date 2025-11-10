"""Mac App Store (mas) plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class MasPlugin(PluginBase):
    """Plugin for Mac App Store command line interface (mas)."""

    async def is_available(self) -> bool:
        """Check if mas is available."""
        try:
            stdout, _, exit_code = await self.run_command(["mas", "version"], timeout=10)
            return exit_code == 0 and stdout.strip()
        except Exception as e:
            logger.debug(f"mas not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Mac App Store updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        try:
            # Check for outdated apps
            logger.info("Checking Mac App Store for updates...")
            stdout, _, exit_code = await self.run_command(
                ["mas", "outdated"],
                timeout=60,
            )

            if exit_code == 0 and stdout:
                # Parse mas outdated output
                # Format: "APP_ID App Name (current_version) < latest_version"
                # or: "APP_ID App Name (current_version)"
                for line in stdout.strip().split("\n"):
                    if not line.strip():
                        continue

                    parts = line.split()
                    if len(parts) >= 2:
                        app_id = parts[0]
                        # Find version info in parentheses
                        if "(" in line and ")" in line:
                            # Extract app name and versions
                            before_paren = line.split("(")[0]
                            app_name_parts = before_paren.split()[1:]  # Skip app_id
                            app_name = " ".join(app_name_parts).strip()

                            # Extract versions
                            version_part = line.split("(")[1].split(")")[0]
                            current_version = version_part.strip()

                            # Check if there's a latest version indicated
                            latest_version = None
                            if "<" in line:
                                parts_after = line.split("<")
                                if len(parts_after) > 1:
                                    latest_version = parts_after[1].strip()

                            # If we have a latest version, it's an update
                            if latest_version:
                                updates.append(
                                    UpdateInfo(
                                        ecosystem="mas",
                                        package=app_name,
                                        current_version=current_version,
                                        latest_version=latest_version,
                                        is_global=True,
                                        status=UpdateStatus.AVAILABLE,
                                        metadata={"app_id": app_id},
                                    )
                                )
                            else:
                                # mas outdated shows all outdated by default
                                updates.append(
                                    UpdateInfo(
                                        ecosystem="mas",
                                        package=app_name,
                                        current_version=current_version,
                                        latest_version="latest",
                                        is_global=True,
                                        status=UpdateStatus.AVAILABLE,
                                        metadata={"app_id": app_id},
                                    )
                                )

            logger.info(f"Found {len(updates)} Mac App Store updates")

        except Exception as e:
            logger.exception(f"Error checking Mac App Store updates: {e}")

        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Mac App Store update."""
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
            # Get app ID from metadata
            app_id = update_info.metadata.get("app_id") if update_info.metadata else None

            if app_id:
                logger.info(f"Updating {update_info.package} (ID: {app_id}) via mas...")
                stdout, stderr, exit_code = await self.run_command(
                    ["mas", "upgrade", app_id],
                    timeout=1200,  # App updates can take a while
                )
            else:
                # If no app ID, try updating all
                logger.info("Updating Mac App Store apps...")
                stdout, stderr, exit_code = await self.run_command(
                    ["mas", "upgrade"],
                    timeout=1200,
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
registry.register(MasPlugin)
