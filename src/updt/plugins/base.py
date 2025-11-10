"""Base plugin interface for package managers."""

import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from loguru import logger

from ..models.update import UpdateInfo, UpdateResult


class PluginBase(ABC):
    """Base class for all package manager plugins."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize plugin.

        Args:
            config: Plugin-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__.replace("Plugin", "").lower()

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if this package manager is available on the system.

        Returns:
            True if the package manager is installed and accessible
        """
        pass

    @abstractmethod
    async def check_updates(self, project_path: Path | None = None) -> list[UpdateInfo]:
        """Check for available updates.

        Args:
            project_path: Optional path to project directory for project-specific updates

        Returns:
            List of available updates
        """
        pass

    @abstractmethod
    async def perform_update(
        self,
        update_info: UpdateInfo,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform an update operation.

        Args:
            update_info: Information about the update to perform
            dry_run: If True, simulate the update without actually performing it

        Returns:
            Result of the update operation
        """
        pass

    async def run_command(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout: int = 300,
    ) -> tuple[str, str, int]:
        """Run a command asynchronously.

        Args:
            command: Command and arguments to run
            cwd: Working directory for the command
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, exit_code)
        """
        try:
            logger.debug(f"Running command: {' '.join(command)}", cwd=str(cwd))
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
            exit_code = process.returncode or 0

            logger.debug(
                "Command finished",
                exit_code=exit_code,
                stdout_len=len(stdout),
                stderr_len=len(stderr),
            )

            return stdout, stderr, exit_code

        except TimeoutError:
            logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
            raise
        except Exception:
            logger.exception(f"Error running command: {' '.join(command)}")
            raise

    def __repr__(self) -> str:
        """String representation of plugin."""
        return f"<{self.__class__.__name__}>"
