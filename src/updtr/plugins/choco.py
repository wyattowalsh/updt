"""Chocolatey package manager plugin for Windows."""

from pathlib import Path
from loguru import logger
from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class ChocoPlugin(PluginBase):
    """Plugin for Chocolatey package manager (Windows)."""

    async def is_available(self) -> bool:
        """Check if Chocolatey is installed."""
        stdout, _, exit_code = await self.run_command(
            ["choco", "--version"], timeout=10
        )
        return exit_code == 0

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for outdated Chocolatey packages."""
        if not await self.is_available():
            return []

        updates = []
        stdout, _, exit_code = await self.run_command(
            ["choco", "outdated", "--limit-output"], timeout=120
        )

        if exit_code == 0 and stdout:
            for line in stdout.strip().split("\n"):
                if not line or line.startswith("Chocolatey"):
                    continue
                parts = line.split("|")
                if len(parts) >= 3:
                    package_name = parts[0]
                    current_version = parts[1]
                    latest_version = parts[2]
                    
                    updates.append(
                        UpdateInfo(
                            ecosystem="choco",
                            package=package_name,
                            current_version=current_version,
                            latest_version=latest_version,
                            is_global=True,
                            status=UpdateStatus.AVAILABLE,
                        )
                    )

        return updates

    async def perform_update(
        self, update_info: UpdateInfo, dry_run: bool = False
    ) -> UpdateResult:
        """Perform an update for a specific package."""
        cmd = ["choco", "upgrade", update_info.package, "-y"]
        
        if dry_run:
            cmd.append("--what-if")

        stdout, stderr, exit_code = await self.run_command(cmd, timeout=600)

        status = UpdateStatus.SUCCESS if exit_code == 0 else UpdateStatus.FAILED
        message = f"Updated {update_info.package}" if exit_code == 0 else f"Failed to update {update_info.package}"

        return UpdateResult(
            update_info=update_info,
            status=status,
            message=message,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )


registry.register(ChocoPlugin)
