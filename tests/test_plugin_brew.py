"""Tests for Homebrew plugin."""

import pytest
from unittest.mock import AsyncMock, patch

from updt.models.update import UpdateStatus
from updt.plugins.brew import BrewPlugin


@pytest.fixture
def brew_plugin():
    """Create a Brew plugin instance."""
    return BrewPlugin()


@pytest.mark.asyncio
async def test_brew_plugin_name(brew_plugin):
    """Test plugin name."""
    assert brew_plugin.name == "brew"


@pytest.mark.asyncio
async def test_brew_plugin_is_available_true(brew_plugin):
    """Test is_available when brew is installed."""
    with patch.object(brew_plugin, "run_command", return_value=("Homebrew 4.0.0", "", 0)):
        result = await brew_plugin.is_available()
        assert result is True


@pytest.mark.asyncio
async def test_brew_plugin_is_available_false(brew_plugin):
    """Test is_available when brew is not installed."""
    with patch.object(brew_plugin, "run_command", return_value=("", "command not found", 127)):
        result = await brew_plugin.is_available()
        assert result is False


@pytest.mark.asyncio
async def test_brew_plugin_check_updates_no_updates(brew_plugin):
    """Test check_updates with no updates available."""
    with patch.object(brew_plugin, "run_command", side_effect=[
        ("Homebrew 4.0.0", "", 0),  # is_available
        ("", "", 0),  # outdated formulae
        ("", "", 0),  # outdated casks
    ]):
        updates = await brew_plugin.check_updates()
        assert isinstance(updates, list)
        assert len(updates) == 0


@pytest.mark.asyncio
async def test_brew_plugin_check_updates_with_formulae(brew_plugin):
    """Test check_updates with outdated formulae."""
    outdated_output = "python 3.11.0 < 3.12.0"
    
    with patch.object(brew_plugin, "run_command", side_effect=[
        ("Homebrew 4.0.0", "", 0),  # is_available
        (outdated_output, "", 0),  # outdated formulae
        ("", "", 0),  # outdated casks
    ]):
        updates = await brew_plugin.check_updates()
        assert len(updates) > 0
        assert updates[0].ecosystem == "brew"
        assert updates[0].status == UpdateStatus.AVAILABLE


@pytest.mark.asyncio
async def test_brew_plugin_check_updates_with_casks(brew_plugin):
    """Test check_updates with outdated casks."""
    outdated_cask = "docker 4.0.0 4.1.0"
    
    with patch.object(brew_plugin, "run_command", side_effect=[
        ("Homebrew 4.0.0", "", 0),  # is_available
        ("", "", 0),  # outdated formulae
        (outdated_cask, "", 0),  # outdated casks
    ]):
        updates = await brew_plugin.check_updates()
        assert len(updates) > 0
        assert updates[0].ecosystem == "brew"


@pytest.mark.asyncio
async def test_brew_plugin_perform_update_dry_run(brew_plugin, sample_update_info):
    """Test perform_update in dry-run mode."""
    sample_update_info.ecosystem = "brew"
    sample_update_info.package = "python"
    
    result = await brew_plugin.perform_update(sample_update_info, dry_run=True)
    
    assert result.status == UpdateStatus.SKIPPED
    assert "dry run" in result.message.lower()


@pytest.mark.asyncio
async def test_brew_plugin_perform_update_success(brew_plugin, sample_update_info):
    """Test perform_update successfully."""
    sample_update_info.ecosystem = "brew"
    sample_update_info.package = "python"
    
    with patch.object(brew_plugin, "run_command", return_value=("", "", 0)):
        result = await brew_plugin.perform_update(sample_update_info, dry_run=False)
        
        assert result.status == UpdateStatus.SUCCESS
