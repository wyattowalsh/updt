"""Tests for NPM plugin."""

import pytest
from unittest.mock import AsyncMock, patch

from updt.models.update import UpdateStatus
from updt.plugins.npm import NpmPlugin


@pytest.fixture
def npm_plugin():
    """Create an NPM plugin instance."""
    return NpmPlugin()


@pytest.mark.asyncio
async def test_npm_plugin_name(npm_plugin):
    """Test plugin name."""
    assert npm_plugin.name == "npm"


@pytest.mark.asyncio
async def test_npm_plugin_is_available_true(npm_plugin):
    """Test is_available when npm is installed."""
    with patch.object(npm_plugin, "run_command", return_value=("9.0.0", "", 0)):
        result = await npm_plugin.is_available()
        assert result is True


@pytest.mark.asyncio
async def test_npm_plugin_is_available_false(npm_plugin):
    """Test is_available when npm is not installed."""
    with patch.object(npm_plugin, "run_command", return_value=("", "command not found", 127)):
        result = await npm_plugin.is_available()
        assert result is False


@pytest.mark.asyncio
async def test_npm_plugin_check_updates_global(npm_plugin):
    """Test check_updates for global packages."""
    outdated_json = '{"lodash": {"current": "4.17.20", "wanted": "4.17.21", "latest": "4.17.21"}}'
    
    with patch.object(npm_plugin, "run_command", side_effect=[
        ("9.0.0", "", 0),  # is_available
        (outdated_json, "", 0),  # global outdated
        ("", "", 0),  # local outdated
    ]):
        updates = await npm_plugin.check_updates()
        assert len(updates) > 0
        assert updates[0].ecosystem == "npm"
        assert updates[0].is_global is True


@pytest.mark.asyncio
async def test_npm_plugin_check_updates_local(npm_plugin, tmp_path):
    """Test check_updates for local packages."""
    outdated_json = '{"react": {"current": "17.0.0", "wanted": "18.0.0", "latest": "18.0.0"}}'
    
    # Create package.json
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "package.json").write_text('{"name": "test"}')
    
    with patch.object(npm_plugin, "run_command", side_effect=[
        ("9.0.0", "", 0),  # is_available
        ("", "", 0),  # global outdated
        (outdated_json, "", 0),  # local outdated
    ]):
        updates = await npm_plugin.check_updates(project_path=project_dir)
        assert len(updates) > 0
        assert updates[0].is_global is False


@pytest.mark.asyncio
async def test_npm_plugin_perform_update_dry_run(npm_plugin, sample_update_info):
    """Test perform_update in dry-run mode."""
    sample_update_info.ecosystem = "npm"
    sample_update_info.package = "lodash"
    
    result = await npm_plugin.perform_update(sample_update_info, dry_run=True)
    
    assert result.status == UpdateStatus.SKIPPED
    assert "dry run" in result.message.lower()


@pytest.mark.asyncio
async def test_npm_plugin_perform_update_success(npm_plugin, sample_update_info):
    """Test perform_update successfully."""
    sample_update_info.ecosystem = "npm"
    sample_update_info.package = "lodash"
    sample_update_info.is_global = True
    
    with patch.object(npm_plugin, "run_command", return_value=("", "", 0)):
        result = await npm_plugin.perform_update(sample_update_info, dry_run=False)
        
        assert result.status == UpdateStatus.SUCCESS
