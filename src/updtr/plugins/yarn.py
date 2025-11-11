"""Yarn package manager plugin."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class YarnPlugin(PluginBase):
    """Plugin for Yarn package manager."""

    async def is_available(self) -> bool:
        """Check if yarn is available."""
        try:
            stdout, _, exit_code = await self.run_command(["yarn", "--version"], timeout=10)
            return exit_code == 0 and stdout.strip()
        except Exception as e:
            logger.debug(f"Yarn not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Yarn updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check global packages
        try:
            stdout, _, exit_code = await self.run_command(
                ["yarn", "global", "list", "--depth=0"],
                timeout=60,
            )
            if exit_code == 0:
                logger.debug("Yarn global packages listed - manual update check needed")
        except Exception as e:
            logger.exception(f"Error checking global Yarn packages: {e}")

        # Check project dependencies
        if project_path:
            package_json = project_path / "package.json"
            yarn_lock = project_path / "yarn.lock"

            if package_json.exists() and yarn_lock.exists():
                try:
                    logger.info(f"Checking Yarn project in {project_path}")
                    stdout, _, exit_code = await self.run_command(
                        ["yarn", "outdated", "--json"],
                        cwd=project_path,
                        timeout=60,
                    )

                    if exit_code == 0 and stdout.strip():
                        # Parse JSON lines output
                        for line in stdout.strip().split("\n"):
                            if not line.strip():
                                continue
                            try:
                                data = json.loads(line)
                                if data.get("type") == "table":
                                    for row in data.get("data", {}).get("body", []):
                                        if len(row) >= 3:
                                            package = row[0]
                                            current = row[1]
                                            latest = row[3] if len(row) > 3 else row[2]

                                            updates.append(
                                                UpdateInfo(
                                                    ecosystem="yarn",
                                                    package=package,
                                                    current_version=current,
                                                    latest_version=latest,
                                                    is_global=False,
                                                    project_path=str(project_path),
                                                    status=UpdateStatus.AVAILABLE,
                                                )
                                            )
                            except json.JSONDecodeError:
                                continue

                except Exception as e:
                    logger.exception(f"Error checking project Yarn packages: {e}")

        logger.info(f"Found {len(updates)} Yarn updates")
        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Yarn package update."""
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
            if update_info.is_global:
                logger.info(f"Updating global Yarn package {update_info.package}...")
                stdout, stderr, exit_code = await self.run_command(
                    ["yarn", "global", "upgrade", update_info.package],
                    timeout=300,
                )
            else:
                logger.info(f"Updating project Yarn package {update_info.package}...")
                project_path = Path(update_info.project_path) if update_info.project_path else None
                stdout, stderr, exit_code = await self.run_command(
                    ["yarn", "upgrade", update_info.package],
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
registry.register(YarnPlugin)
