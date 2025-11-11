"""Integration tests for end-to-end workflows."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from updtr.models.config import UpdtConfig
from updtr.models.update import UpdateInfo, UpdateStatus
from updtr.plugins.registry import PluginRegistry
from updtr.updater import UpdateManager
from updtr.profile import SystemProfile


@pytest.mark.asyncio
async def test_end_to_end_check_and_update_workflow(mock_plugin_registry):
    """Test complete workflow: check updates -> perform updates."""
    config = UpdtConfig()
    manager = UpdateManager(config, plugin_registry=mock_plugin_registry)
    
    # Initialize
    await manager.initialize()
    
    # Check for updates
    updates = await manager.check_all_updates()
    assert isinstance(updates, list)
    
    # Perform updates (dry-run)
    if updates:
        results = await manager.perform_updates(updates, dry_run=True)
        assert len(results) == len(updates)
        for result in results:
            assert result.status in [UpdateStatus.SUCCESS, UpdateStatus.SKIPPED, UpdateStatus.FAILED]


@pytest.mark.asyncio
async def test_end_to_end_profile_generation():
    """Test complete profile generation workflow."""
    with patch("updtr.profile.UpdateManager") as mock_manager_class:
        mock_manager = AsyncMock()
        mock_manager.initialize = AsyncMock()
        mock_manager.check_all_updates = AsyncMock(return_value=[
            UpdateInfo(
                ecosystem="test",
                package="test-pkg",
                current_version="1.0.0",
                latest_version="2.0.0",
                status=UpdateStatus.AVAILABLE,
            )
        ])
        mock_manager_class.return_value = mock_manager
        
        profile = SystemProfile()
        result = await profile.generate()
        
        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "hostname" in result


@pytest.mark.asyncio
async def test_end_to_end_project_scoped_workflow(tmp_project_dir, mock_plugin_registry):
    """Test workflow with project-scoped updates."""
    config = UpdtConfig()
    manager = UpdateManager(config, plugin_registry=mock_plugin_registry)
    
    await manager.initialize()
    
    # Check updates for specific project
    updates = await manager.check_all_updates(project_path=tmp_project_dir)
    assert isinstance(updates, list)


@pytest.mark.asyncio
async def test_end_to_end_concurrent_updates(mock_plugin_registry):
    """Test concurrent update execution."""
    config = UpdtConfig(max_concurrent_updates=3)
    manager = UpdateManager(config, plugin_registry=mock_plugin_registry)
    
    await manager.initialize()
    
    # Create multiple updates
    updates = [
        UpdateInfo(
            ecosystem="mock",
            package=f"pkg-{i}",
            current_version="1.0.0",
            latest_version="2.0.0",
            status=UpdateStatus.AVAILABLE,
        )
        for i in range(5)
    ]
    
    results = await manager.perform_updates(updates, dry_run=True)
    assert len(results) == len(updates)


@pytest.mark.asyncio
async def test_end_to_end_error_handling(mock_plugin_registry):
    """Test error handling in complete workflow."""
    config = UpdtConfig()
    manager = UpdateManager(config, plugin_registry=mock_plugin_registry)
    
    await manager.initialize()
    
    # Create an update that might fail
    update = UpdateInfo(
        ecosystem="nonexistent",
        package="fake-pkg",
        current_version="1.0.0",
        latest_version="2.0.0",
        status=UpdateStatus.AVAILABLE,
    )
    
    # Should handle gracefully
    results = await manager.perform_updates([update], dry_run=False)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_end_to_end_export_profile(tmp_path):
    """Test complete profile export workflow."""
    with patch("updtr.profile.UpdateManager") as mock_manager_class:
        mock_manager = AsyncMock()
        mock_manager.initialize = AsyncMock()
        mock_manager.check_all_updates = AsyncMock(return_value=[])
        mock_manager_class.return_value = mock_manager
        
        profile = SystemProfile()
        output_file = tmp_path / "profile.json"
        
        await profile.export_to_file(output_file, format="json")
        
        assert output_file.exists()


@pytest.mark.asyncio
async def test_end_to_end_multiple_plugin_types(mock_plugin_registry):
    """Test workflow with multiple plugin types."""
    config = UpdtConfig()
    manager = UpdateManager(config, plugin_registry=mock_plugin_registry)
    
    await manager.initialize()
    
    # Should handle plugins from different ecosystems
    updates = await manager.check_all_updates()
    assert isinstance(updates, list)


@pytest.mark.asyncio
async def test_end_to_end_logging_configuration():
    """Test that logging is properly configured throughout workflow."""
    from updtr.logging import setup_logging
    
    config = UpdtConfig(log_level="DEBUG", log_format="jsonl")
    logger = setup_logging(config)
    
    assert logger is not None
    
    # Test workflow with logging
    with patch("updtr.updater.registry") as mock_registry:
        mock_registry.list_all.return_value = []
        manager = UpdateManager(config)
        await manager.initialize()
