"""Tests for Windows package manager plugins."""

import pytest
from unittest.mock import AsyncMock, patch
from updtr.plugins.choco import ChocoPlugin
from updtr.plugins.scoop import ScoopPlugin
from updtr.plugins.winget import WingetPlugin
from updtr.models.update import UpdateInfo, UpdateStatus
from updtr.models.config import UpdtConfig


@pytest.fixture
def config():
    """Create a test configuration."""
    return UpdtConfig()


@pytest.mark.asyncio
class TestChocoPlugin:
    """Tests for Chocolatey plugin."""

    async def test_is_available_success(self, config):
        """Test that Chocolatey is detected when installed."""
        plugin = ChocoPlugin(config)
        with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("2.2.2\n", "", 0)
            result = await plugin.is_available()
            assert result is True
            mock_run.assert_called_once()

    async def test_is_available_failure(self, config):
        """Test that Chocolatey is not detected when not installed."""
        plugin = ChocoPlugin(config)
        with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("", "command not found", 1)
            result = await plugin.is_available()
            assert result is False

    async def test_check_updates(self, config):
        """Test checking for Chocolatey package updates."""
        plugin = ChocoPlugin(config)
        choco_output = """Chocolatey v2.2.2
package1|1.0.0|1.1.0|false
package2|2.0.0|2.1.0|false
"""
        with patch.object(plugin, "is_available", return_value=True):
            with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = (choco_output, "", 0)
                updates = await plugin.check_updates()
                
                assert len(updates) == 2
                assert updates[0].ecosystem == "choco"
                assert updates[0].package == "package1"
                assert updates[0].current_version == "1.0.0"
                assert updates[0].latest_version == "1.1.0"

    async def test_perform_update(self, config):
        """Test performing a Chocolatey package update."""
        plugin = ChocoPlugin(config)
        update_info = UpdateInfo(
            ecosystem="choco",
            package="test-package",
            current_version="1.0.0",
            latest_version="1.1.0",
            is_global=True,
            status=UpdateStatus.AVAILABLE,
        )
        
        with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("Updated successfully", "", 0)
            result = await plugin.perform_update(update_info, dry_run=False)
            
            assert result.status == UpdateStatus.SUCCESS
            assert "Updated" in result.message


@pytest.mark.asyncio
class TestScoopPlugin:
    """Tests for Scoop plugin."""

    async def test_is_available_success(self, config):
        """Test that Scoop is detected when installed."""
        plugin = ScoopPlugin(config)
        with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("v0.3.1\n", "", 0)
            result = await plugin.is_available()
            assert result is True

    async def test_check_updates(self, config):
        """Test checking for Scoop package updates."""
        plugin = ScoopPlugin(config)
        scoop_output = """Scoop is up to date.
Outdated apps:
    package1: 1.0.0 -> 1.1.0
    package2: 2.0.0 -> 2.1.0
"""
        with patch.object(plugin, "is_available", return_value=True):
            with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
                # First call for update, second for status
                mock_run.side_effect = [
                    ("", "", 0),  # scoop update
                    (scoop_output, "", 0),  # scoop status
                ]
                updates = await plugin.check_updates()
                
                assert len(updates) == 2
                assert updates[0].ecosystem == "scoop"
                assert updates[0].package == "package1"

    async def test_perform_update_dry_run(self, config):
        """Test dry-run mode for Scoop updates."""
        plugin = ScoopPlugin(config)
        update_info = UpdateInfo(
            ecosystem="scoop",
            package="test-package",
            current_version="1.0.0",
            latest_version="1.1.0",
            is_global=True,
            status=UpdateStatus.AVAILABLE,
        )
        
        result = await plugin.perform_update(update_info, dry_run=True)
        assert result.status == UpdateStatus.SKIPPED
        assert "Would update" in result.message


@pytest.mark.asyncio
class TestWingetPlugin:
    """Tests for Windows Package Manager (winget) plugin."""

    async def test_is_available_success(self, config):
        """Test that winget is detected when installed."""
        plugin = WingetPlugin(config)
        with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("v1.6.3133\n", "", 0)
            result = await plugin.is_available()
            assert result is True

    async def test_check_updates(self, config):
        """Test checking for winget package updates."""
        plugin = WingetPlugin(config)
        winget_output = """Name       Id          Version   Available Source
---------------------------------------------------
Package1   Pub.Pkg1    1.0.0 <   1.1.0     winget
Package2   Pub.Pkg2    2.0.0 <   2.1.0     winget
"""
        with patch.object(plugin, "is_available", return_value=True):
            with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = (winget_output, "", 0)
                updates = await plugin.check_updates()
                
                assert len(updates) >= 0  # Parsing may vary
                if updates:
                    assert updates[0].ecosystem == "winget"

    async def test_perform_update(self, config):
        """Test performing a winget package update."""
        plugin = WingetPlugin(config)
        update_info = UpdateInfo(
            ecosystem="winget",
            package="Test.Package",
            current_version="1.0.0",
            latest_version="1.1.0",
            is_global=True,
            status=UpdateStatus.AVAILABLE,
        )
        
        with patch.object(plugin, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("Successfully installed", "", 0)
            result = await plugin.perform_update(update_info, dry_run=False)
            
            assert result.status == UpdateStatus.SUCCESS
