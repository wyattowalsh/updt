"""NPM package manager plugin."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class NpmPlugin(PluginBase):
    """Plugin for NPM package manager."""

    async def is_available(self) -> bool:
        """Check if npm is available."""
        try:
            stdout, _, exit_code = await self.run_command(["npm", "--version"], timeout=10)
            return exit_code == 0 and stdout.strip()
        except Exception as e:
            logger.debug(f"NPM not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available NPM updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check global packages
        try:
            stdout, _, exit_code = await self.run_command(
                ["npm", "outdated", "-g", "--json"],
                timeout=60,
            )
            if exit_code == 0 and stdout.strip():
                try:
                    outdated = json.loads(stdout)
                    for package, info in outdated.items():
                        updates.append(
                            UpdateInfo(
                                ecosystem="npm",
                                package=package,
                                current_version=info.get("current"),
                                latest_version=info.get("latest"),
                                is_global=True,
                                status=UpdateStatus.AVAILABLE,
                            )
                        )
                except json.JSONDecodeError:
                    logger.warning("Failed to parse npm outdated output")
        except Exception as e:
            logger.exception(f"Error checking global NPM packages: {e}")

        # Check project dependencies
        if project_path:
            package_json = project_path / "package.json"
            if package_json.exists():
                try:
                    stdout, _, exit_code = await self.run_command(
                        ["npm", "outdated", "--json"],
                        cwd=project_path,
                        timeout=60,
                    )
                    if stdout.strip():
                        try:
                            outdated = json.loads(stdout)
                            for package, info in outdated.items():
                                updates.append(
                                    UpdateInfo(
                                        ecosystem="npm",
                                        package=package,
                                        current_version=info.get("current"),
                                        latest_version=info.get("latest"),
                                        is_global=False,
                                        project_path=str(project_path),
                                        status=UpdateStatus.AVAILABLE,
                                    )
                                )
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse npm outdated output")
                except Exception as e:
                    logger.exception(f"Error checking project NPM packages: {e}")

        logger.info(f"Found {len(updates)} NPM updates")
        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform an NPM package update."""
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
                logger.info(f"Updating global NPM package {update_info.package}...")
                stdout, stderr, exit_code = await self.run_command(
                    ["npm", "update", "-g", update_info.package],
                    timeout=300,
                )
            else:
                logger.info(f"Updating project NPM package {update_info.package}...")
                project_path = Path(update_info.project_path) if update_info.project_path else None
                stdout, stderr, exit_code = await self.run_command(
                    ["npm", "update", update_info.package],
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
registry.register(NpmPlugin)
