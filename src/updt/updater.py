"""Core update manager."""

import asyncio
from pathlib import Path

from loguru import logger

from .models.config import UpdtConfig
from .models.update import UpdateInfo, UpdateResult, UpdateStatus
from .plugins import PluginBase, PluginRegistry
from .plugins.registry import registry


class UpdateManager:
    """Manages update detection and execution across all plugins."""

    def __init__(self, config: UpdtConfig, plugin_registry: PluginRegistry | None = None) -> None:
        """Initialize the update manager.

        Args:
            config: Application configuration
            plugin_registry: Plugin registry (uses global registry if None)
        """
        self.config = config
        self.registry = plugin_registry or registry
        self._plugins: list[PluginBase] = []

    async def initialize(self) -> None:
        """Initialize all enabled plugins."""
        logger.info("Initializing plugins...")

        for name, plugin_class in self.registry.get_all().items():
            # Check if this ecosystem is enabled in config
            enabled = getattr(self.config.ecosystems, name, False)
            if not enabled:
                logger.debug(f"Skipping disabled plugin: {name}")
                continue

            # Create plugin instance
            plugin = plugin_class(config=self.config.model_dump())

            # Check if plugin is available
            if await plugin.is_available():
                self._plugins.append(plugin)
                logger.info(f"Initialized plugin: {name}")
            else:
                logger.debug(f"Plugin not available: {name}")

        logger.info(f"Initialized {len(self._plugins)} plugins")

    async def check_all_updates(
        self,
        project_path: Path | None = None,
    ) -> list[UpdateInfo]:
        """Check for updates across all enabled plugins.

        Args:
            project_path: Optional path to project directory

        Returns:
            List of all available updates
        """
        logger.info("Checking for updates across all ecosystems...")

        # Run all plugin checks concurrently
        tasks = [plugin.check_updates(project_path) for plugin in self._plugins]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_updates: list[UpdateInfo] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                plugin_name = self._plugins[i].name
                logger.error(f"Error checking updates for {plugin_name}: {result}")
            else:
                all_updates.extend(result)

        logger.info(f"Found {len(all_updates)} total updates")
        return all_updates

    async def perform_updates(
        self,
        updates: list[UpdateInfo],
        dry_run: bool = False,
    ) -> list[UpdateResult]:
        """Perform updates with concurrency control.

        Args:
            updates: List of updates to perform
            dry_run: If True, simulate updates without performing them

        Returns:
            List of update results
        """
        logger.info(f"Performing {len(updates)} updates (dry_run={dry_run})...")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config.max_concurrent_updates)

        async def update_with_semaphore(update: UpdateInfo) -> UpdateResult:
            """Perform update with semaphore."""
            async with semaphore:
                # Find the appropriate plugin
                plugin = next(
                    (p for p in self._plugins if p.name == update.ecosystem),
                    None,
                )
                if not plugin:
                    logger.error(f"No plugin found for {update.ecosystem}")
                    return UpdateResult(
                        update_info=update,
                        status=UpdateStatus.FAILED,
                        message=f"No plugin available for {update.ecosystem}",
                    )

                return await plugin.perform_update(update, dry_run=dry_run)

        # Run updates with concurrency control
        tasks = [update_with_semaphore(update) for update in updates]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        final_results: list[UpdateResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                update = updates[i]
                logger.error(f"Error updating {update.package}: {result}")
                final_results.append(
                    UpdateResult(
                        update_info=update,
                        status=UpdateStatus.FAILED,
                        message=f"Error: {str(result)}",
                    )
                )
            else:
                final_results.append(result)

        # Log summary
        success_count = sum(1 for r in final_results if r.status == UpdateStatus.SUCCESS)
        failed_count = sum(1 for r in final_results if r.status == UpdateStatus.FAILED)
        skipped_count = sum(1 for r in final_results if r.status == UpdateStatus.SKIPPED)

        logger.info(
            f"Update summary: {success_count} succeeded, {failed_count} failed, "
            f"{skipped_count} skipped"
        )

        return final_results
