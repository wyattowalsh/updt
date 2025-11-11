"""Tests for plugin system."""

import pytest

from updtr.plugins.base import PluginBase
from updtr.plugins.registry import PluginRegistry


class TestPlugin(PluginBase):
    """Test plugin implementation."""

    async def is_available(self) -> bool:
        """Check availability."""
        return True

    async def check_updates(self, project_path=None):  # type: ignore
        """Check updates."""
        return []

    async def perform_update(self, update_info, dry_run=False):  # type: ignore
        """Perform update."""
        from updtr.models.update import UpdateResult, UpdateStatus

        return UpdateResult(
            update_info=update_info,
            status=UpdateStatus.SUCCESS,
            message="Test",
        )


def test_plugin_registry() -> None:
    """Test plugin registry."""
    registry = PluginRegistry()
    registry.register(TestPlugin)

    assert "test" in registry.list_names()
    assert registry.get("test") == TestPlugin


def test_plugin_base_name() -> None:
    """Test plugin name generation."""
    plugin = TestPlugin()
    assert plugin.name == "test"


@pytest.mark.asyncio
async def test_plugin_run_command() -> None:
    """Test running commands."""
    plugin = TestPlugin()
    stdout, stderr, exit_code = await plugin.run_command(["echo", "test"], timeout=5)
    assert "test" in stdout
    assert exit_code == 0
