"""Poetry package manager plugin."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class PoetryPlugin(PluginBase):
    """Plugin for Poetry package manager."""

    async def is_available(self) -> bool:
        """Check if poetry is available."""
        try:
            stdout, _, exit_code = await self.run_command(["poetry", "--version"], timeout=10)
            return exit_code == 0 and "Poetry" in stdout
        except Exception as e:
            logger.debug(f"Poetry not available: {e}")
            return False

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available Poetry updates."""
        if not await self.is_available():
            return []

        updates: list[UpdateInfo] = []

        # Check project dependencies if pyproject.toml exists with poetry config
        if project_path:
            pyproject_path = project_path / "pyproject.toml"
            poetry_lock = project_path / "poetry.lock"

            if pyproject_path.exists() and poetry_lock.exists():
                try:
                    logger.info(f"Checking Poetry project in {project_path}")
                    stdout, _, exit_code = await self.run_command(
                        ["poetry", "show", "--outdated"],
                        cwd=project_path,
                        timeout=60,
                    )

                    if exit_code == 0 and stdout:
                        # Parse poetry show --outdated output
                        # Format: package current latest description
                        for line in stdout.strip().split("\n"):
                            if not line.strip() or line.startswith("!"):
                                continue

                            parts = line.split()
                            if len(parts) >= 3:
                                package, current, latest = parts[0], parts[1], parts[2]
                                updates.append(
                                    UpdateInfo(
                                        ecosystem="poetry",
                                        package=package,
                                        current_version=current,
                                        latest_version=latest,
                                        is_global=False,
                                        project_path=str(project_path),
                                        status=UpdateStatus.AVAILABLE,
                                    )
                                )

                except Exception as e:
                    logger.exception(f"Error checking Poetry project: {e}")

        logger.info(f"Found {len(updates)} Poetry updates")
        return updates

    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform a Poetry package update."""
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
            logger.info(f"Updating {update_info.package} via Poetry...")
            project_path = Path(update_info.project_path) if update_info.project_path else None

            stdout, stderr, exit_code = await self.run_command(
                ["poetry", "update", update_info.package],
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
registry.register(PoetryPlugin)
