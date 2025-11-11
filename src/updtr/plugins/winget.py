"""Windows Package Manager (winget) plugin."""

import json
from pathlib import Path
from loguru import logger
from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class WingetPlugin(PluginBase):
    """Plugin for Windows Package Manager (winget)."""

    async def is_available(self) -> bool:
        """Check if winget is installed."""
        stdout, _, exit_code = await self.run_command(
            ["winget", "--version"], timeout=10
        )
        return exit_code == 0

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for outdated packages via winget."""
        if not await self.is_available():
            return []

        updates = []
        # Use winget upgrade --include-unknown to list all available upgrades
        stdout, _, exit_code = await self.run_command(
            ["winget", "upgrade", "--include-unknown"], timeout=120
        )

        if exit_code == 0 and stdout:
            lines = stdout.strip().split("\n")
            # Skip header lines
            for line in lines:
                # Look for upgrade lines (they contain version info)
                if "<" in line and ">" not in line:
                    # Format varies, try to parse columns
                    parts = line.split()
                    if len(parts) >= 4:
                        package_name = parts[0]
                        # Try to find version numbers
                        versions = [p for p in parts if any(c.isdigit() for c in p)]
                        if len(versions) >= 2:
                            current_version = versions[0]
                            latest_version = versions[1]
                            
                            updates.append(
                                UpdateInfo(
                                    ecosystem="winget",
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
        if dry_run:
            # winget doesn't have native dry-run for upgrade
            message = f"Would update {update_info.package} from {update_info.current_version} to {update_info.latest_version}"
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.SKIPPED,
                message=message,
                stdout=message,
                stderr="",
                exit_code=0,
            )

        cmd = ["winget", "upgrade", "--id", update_info.package, "--silent", "--accept-package-agreements", "--accept-source-agreements"]
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


registry.register(WingetPlugin)
