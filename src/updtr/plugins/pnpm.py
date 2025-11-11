"""PNPM package manager plugin."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class PnpmPlugin(PluginBase):
    """Plugin for PNPM - Fast, disk space efficient package manager."""

    async def is_available(self) -> bool:
        """Check if pnpm is available."""
        try:
            stdout, _, exit_code = await self.run_command(["pnpm", "--version"], timeout=10)
            return exit_code == 0 and stdout.strip()
        except Exception as e:
            logger.debug(f"PNPM not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available PNPM updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check global packages
        try:
            stdout, _, exit_code = await self.run_command(
                ["pnpm", "list", "-g", "--depth=0"],
                timeout=60,
            )
            if exit_code == 0:
                logger.debug("PNPM global packages listed")
        except Exception as e:
            logger.exception(f"Error checking global PNPM packages: {e}")

        # Check project dependencies
        if project_path:
            package_json = project_path / "package.json"
            pnpm_lock = project_path / "pnpm-lock.yaml"

            if package_json.exists() and pnpm_lock.exists():
                try:
                    logger.info(f"Checking PNPM project in {project_path}")
                    stdout, _, exit_code = await self.run_command(
                        ["pnpm", "outdated", "--format=json"],
                        cwd=project_path,
                        timeout=60,
                    )

                    if exit_code == 0 and stdout.strip():
                        try:
                            # PNPM outdated returns array of outdated packages
                            outdated = json.loads(stdout)

                            for pkg in outdated:
                                package = pkg.get("packageName") or pkg.get("name")
                                current = pkg.get("current")
                                latest = pkg.get("latest")

                                if package:
                                    updates.append(
                                        UpdateInfo(
                                            ecosystem="pnpm",
                                            package=package,
                                            current_version=current,
                                            latest_version=latest,
                                            is_global=False,
                                            project_path=str(project_path),
                                            status=UpdateStatus.AVAILABLE,
                                        )
                                    )
                        except json.JSONDecodeError:
                            # Try parsing line by line if not valid JSON
                            for line in stdout.strip().split("\n"):
                                if line.strip() and not line.startswith("{"):
                                    # Parse text format: package current -> latest
                                    parts = line.split()
                                    if len(parts) >= 3:
                                        package, current = parts[0], parts[1]
                                        latest = parts[-1]
                                        updates.append(
                                            UpdateInfo(
                                                ecosystem="pnpm",
                                                package=package,
                                                current_version=current,
                                                latest_version=latest,
                                                is_global=False,
                                                project_path=str(project_path),
                                                status=UpdateStatus.AVAILABLE,
                                            )
                                        )

                except Exception as e:
                    logger.exception(f"Error checking project PNPM packages: {e}")

        logger.info(f"Found {len(updates)} PNPM updates")
        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a PNPM package update."""
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
                logger.info(f"Updating global PNPM package {update_info.package}...")
                stdout, stderr, exit_code = await self.run_command(
                    ["pnpm", "update", "-g", update_info.package],
                    timeout=300,
                )
            else:
                logger.info(f"Updating project PNPM package {update_info.package}...")
                project_path = Path(update_info.project_path) if update_info.project_path else None
                stdout, stderr, exit_code = await self.run_command(
                    ["pnpm", "update", update_info.package],
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
registry.register(PnpmPlugin)
