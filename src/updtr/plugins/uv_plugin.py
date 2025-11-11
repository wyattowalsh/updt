"""UV package manager plugin."""

import re
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class UvPlugin(PluginBase):
    """Plugin for UV package manager."""

    async def is_available(self) -> bool:
        """Check if uv is available."""
        try:
            stdout, _, exit_code = await self.run_command(["uv", "--version"], timeout=10)
            return exit_code == 0 and "uv" in stdout
        except Exception as e:
            logger.debug(f"UV not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available UV updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check global tools
        try:
            stdout, _, exit_code = await self.run_command(["uv", "tool", "list"], timeout=30)
            if exit_code == 0 and stdout:
                for line in stdout.strip().split("\n"):
                    # Parse: "package v1.0.0"
                    match = re.match(r"(\S+)\s+v?([0-9.]+)", line)
                    if match:
                        package, version = match.groups()
                        # Note: UV doesn't have built-in update check for tools yet
                        # This is a placeholder structure
                        updates.append(
                            UpdateInfo(
                                ecosystem="uv",
                                package=package,
                                current_version=version,
                                latest_version=None,  # Would need to check PyPI
                                is_global=True,
                                status=UpdateStatus.PENDING,
                                message="Update check not implemented yet",
                            )
                        )
        except Exception as e:
            logger.exception(f"Error checking UV tools: {e}")

        # Check project dependencies if project_path provided
        if project_path:
            pyproject_path = project_path / "pyproject.toml"
            if pyproject_path.exists():
                try:
                    # uv can check outdated deps in a project
                    stdout, _, exit_code = await self.run_command(
                        ["uv", "pip", "list", "--outdated"],
                        cwd=project_path,
                        timeout=60,
                    )
                    # Parse output similar to pip list --outdated
                    # Package  Version  Latest  Type
                    if exit_code == 0 and stdout:
                        lines = stdout.strip().split("\n")
                        for line in lines[2:]:  # Skip header
                            parts = line.split()
                            if len(parts) >= 3:
                                package, current, latest = parts[0], parts[1], parts[2]
                                updates.append(
                                    UpdateInfo(
                                        ecosystem="uv",
                                        package=package,
                                        current_version=current,
                                        latest_version=latest,
                                        is_global=False,
                                        project_path=str(project_path),
                                        status=UpdateStatus.AVAILABLE,
                                    )
                                )
                except Exception as e:
                    logger.exception(f"Error checking project dependencies: {e}")

        logger.info(f"Found {len(updates)} UV updates")
        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a UV package update."""
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
                # Update global tool
                logger.info(f"Updating global tool {update_info.package}...")
                stdout, stderr, exit_code = await self.run_command(
                    ["uv", "tool", "upgrade", update_info.package],
                    timeout=300,
                )
            else:
                # Update project dependency
                logger.info(f"Updating project dependency {update_info.package}...")
                project_path = Path(update_info.project_path) if update_info.project_path else None
                stdout, stderr, exit_code = await self.run_command(
                    ["uv", "pip", "install", "--upgrade", update_info.package],
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
registry.register(UvPlugin)
