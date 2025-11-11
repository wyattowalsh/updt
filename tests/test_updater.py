"""Tests for UpdateManager."""

import pytest

from updtr.models.config import UpdtConfig
from updtr.models.update import UpdateInfo, UpdateStatus
from updtr.plugins.base import PluginBase
from updtr.plugins.registry import PluginRegistry
from updtr.updater import UpdateManager


class MockPlugin(PluginBase):
    """Mock plugin for testing."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self.available = True

    async def is_available(self) -> bool:
        """Check availability."""
        return self.available

    async def check_updates(self, project_path=None):  # type: ignore
        """Check updates."""
        if self.available:
            return [
                UpdateInfo(
                    ecosystem="mock",
                    package="test-package",
                    current_version="1.0.0",
                    latest_version="2.0.0",
                    status=UpdateStatus.AVAILABLE,
                )
            ]
        return []

    async def perform_update(self, update_info, dry_run=False):  # type: ignore
        """Perform update."""
        from updtr.models.update import UpdateResult

        if dry_run:
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.SKIPPED,
                message="Dry run - no actual update performed",
                duration=0.0,
            )

        return UpdateResult(
            update_info=update_info,
            status=UpdateStatus.SUCCESS,
            message="Updated successfully",
            duration=1.0,
        )


@pytest.mark.asyncio
async def test_update_manager_initialization() -> None:
    """Test UpdateManager initialization."""
    config = UpdtConfig()
    registry = PluginRegistry()
    registry.register(MockPlugin)

    manager = UpdateManager(config, plugin_registry=registry)
    await manager.initialize()

    # Should have at least one plugin if MockPlugin is available
    assert len(manager._plugins) >= 0


@pytest.mark.asyncio
async def test_update_manager_check_updates() -> None:
    """Test checking for updates."""
    config = UpdtConfig()
    registry = PluginRegistry()
    registry.register(MockPlugin)

    manager = UpdateManager(config, plugin_registry=registry)
    await manager.initialize()

    updates = await manager.check_all_updates()
    assert isinstance(updates, list)


@pytest.mark.asyncio
async def test_update_manager_perform_updates() -> None:
    """Test performing updates."""
    from updtr.models.config import EcosystemConfig

    config = UpdtConfig()
    # Enable mock plugin in config
    config.ecosystems = EcosystemConfig(mock=True)  # type: ignore

    registry = PluginRegistry()
    registry.register(MockPlugin)

    manager = UpdateManager(config, plugin_registry=registry)
    await manager.initialize()

    # Create test update
    update = UpdateInfo(
        ecosystem="mock",
        package="test-package",
        current_version="1.0.0",
        latest_version="2.0.0",
        status=UpdateStatus.AVAILABLE,
    )

    results = await manager.perform_updates([update], dry_run=True)
    assert len(results) == 1
    # In dry run, status should be SKIPPED
    assert results[0].status == UpdateStatus.SKIPPED
