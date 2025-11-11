"""Scoop package manager plugin for Windows."""

import json
from pathlib import Path
from loguru import logger
from ..models.update import UpdateInfo, UpdateResult, UpdateStatus
from .base import PluginBase
from .registry import registry


class ScoopPlugin(PluginBase):
    """Plugin for Scoop package manager (Windows)."""

    async def is_available(self) -> bool:
        """Check if Scoop is installed."""
        stdout, _, exit_code = await self.run_command(
            ["scoop", "--version"], timeout=10
        )
        return exit_code == 0

    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for outdated Scoop packages."""
        if not await self.is_available():
            return []

        # Update scoop buckets first
        await self.run_command(["scoop", "update"], timeout=60)

        updates = []
        stdout, _, exit_code = await self.run_command(
            ["scoop", "status"], timeout=60
        )

        if exit_code == 0 and stdout:
            # Parse scoop status output
            lines = stdout.strip().split("\n")
            in_outdated_section = False
            
            for line in lines:
                if "outdated" in line.lower():
                    in_outdated_section = True
                    continue
                
                if in_outdated_section and line.strip():
                    # Format: Name: current_version -> latest_version
                    parts = line.strip().split(":")
                    if len(parts) >= 2:
                        package_name = parts[0].strip()
                        versions = parts[1].strip().split("->")
                        if len(versions) == 2:
                            current_version = versions[0].strip()
                            latest_version = versions[1].strip()
                            
                            updates.append(
                                UpdateInfo(
                                    ecosystem="scoop",
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
            # Scoop doesn't have native dry-run, simulate
            message = f"Would update {update_info.package} from {update_info.current_version} to {update_info.latest_version}"
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.SKIPPED,
                message=message,
                stdout=message,
                stderr="",
                exit_code=0,
            )

        cmd = ["scoop", "update", update_info.package]
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


registry.register(ScoopPlugin)
