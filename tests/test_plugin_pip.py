"""Tests for Pip plugin."""

import pytest
from unittest.mock import patch

from updt.models.update import UpdateStatus
from updt.plugins.pip import PipPlugin


@pytest.fixture
def pip_plugin():
    """Create a Pip plugin instance."""
    return PipPlugin()


@pytest.mark.asyncio
async def test_pip_plugin_name(pip_plugin):
    """Test plugin name."""
    assert pip_plugin.name == "pip"


@pytest.mark.asyncio
async def test_pip_plugin_is_available_true(pip_plugin):
    """Test is_available when pip is installed."""
    with patch.object(pip_plugin, "run_command", return_value=("pip 23.0.0", "", 0)):
        result = await pip_plugin.is_available()
        assert result is True


@pytest.mark.asyncio
async def test_pip_plugin_is_available_false(pip_plugin):
    """Test is_available when pip is not installed."""
    with patch.object(pip_plugin, "run_command", return_value=("", "command not found", 127)):
        result = await pip_plugin.is_available()
        assert result is False


@pytest.mark.asyncio
async def test_pip_plugin_check_updates_no_updates(pip_plugin):
    """Test check_updates with no outdated packages."""
    with patch.object(pip_plugin, "run_command", side_effect=[
        ("pip 23.0.0", "", 0),  # is_available
        ("", "", 0),  # list --outdated
    ]):
        updates = await pip_plugin.check_updates()
        assert isinstance(updates, list)
        assert len(updates) == 0


@pytest.mark.asyncio
async def test_pip_plugin_check_updates_with_outdated(pip_plugin):
    """Test check_updates with outdated packages."""
    outdated_output = "requests  2.28.0  2.31.0  wheel"
    
    with patch.object(pip_plugin, "run_command", side_effect=[
        ("pip 23.0.0", "", 0),  # is_available
        (outdated_output, "", 0),  # list --outdated
    ]):
        updates = await pip_plugin.check_updates()
        assert len(updates) > 0
        assert updates[0].ecosystem == "pip"
        assert updates[0].package == "requests"
        assert updates[0].status == UpdateStatus.AVAILABLE


@pytest.mark.asyncio
async def test_pip_plugin_perform_update_dry_run(pip_plugin, sample_update_info):
    """Test perform_update in dry-run mode."""
    sample_update_info.ecosystem = "pip"
    sample_update_info.package = "requests"
    
    result = await pip_plugin.perform_update(sample_update_info, dry_run=True)
    
    assert result.status == UpdateStatus.SKIPPED
    assert "dry run" in result.message.lower()


@pytest.mark.asyncio
async def test_pip_plugin_perform_update_success(pip_plugin, sample_update_info):
    """Test perform_update successfully."""
    sample_update_info.ecosystem = "pip"
    sample_update_info.package = "requests"
    
    with patch.object(pip_plugin, "run_command", return_value=("", "", 0)):
        result = await pip_plugin.perform_update(sample_update_info, dry_run=False)
        
        assert result.status == UpdateStatus.SUCCESS
