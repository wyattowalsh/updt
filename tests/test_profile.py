"""Tests for system profiling functionality."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from updt.models.update import UpdateInfo, UpdateStatus
from updt.profile import SystemProfile


@pytest.fixture
def mock_manager():
    """Create a mock UpdateManager."""
    manager = AsyncMock()
    manager.check_all_updates = AsyncMock(return_value=[
        UpdateInfo(
            ecosystem="test",
            package="test-pkg",
            current_version="1.0.0",
            latest_version="2.0.0",
            status=UpdateStatus.AVAILABLE,
        )
    ])
    return manager


@pytest.mark.asyncio
async def test_system_profile_initialization():
    """Test SystemProfile initialization."""
    profile = SystemProfile()
    assert profile is not None


@pytest.mark.asyncio
@patch("updt.profile.UpdateManager")
async def test_system_profile_generate(mock_manager_class, mock_manager):
    """Test profile generation."""
    mock_manager_class.return_value = mock_manager
    
    profile = SystemProfile()
    result = await profile.generate()
    
    assert isinstance(result, dict)
    assert "timestamp" in result
    assert "hostname" in result


@pytest.mark.asyncio
@patch("updt.profile.UpdateManager")
async def test_system_profile_generate_with_project(mock_manager_class, mock_manager, tmp_path):
    """Test profile generation with project path."""
    mock_manager_class.return_value = mock_manager
    
    profile = SystemProfile()
    result = await profile.generate(project_path=tmp_path)
    
    assert isinstance(result, dict)


@pytest.mark.asyncio
@patch("updt.profile.UpdateManager")
async def test_system_profile_export_json(mock_manager_class, mock_manager, tmp_path):
    """Test exporting profile to JSON."""
    mock_manager_class.return_value = mock_manager
    
    profile = SystemProfile()
    output_file = tmp_path / "profile.json"
    
    await profile.export_to_file(output_file, format="json")
    
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert isinstance(data, dict)


@pytest.mark.asyncio
@patch("updt.profile.UpdateManager")
async def test_system_profile_export_markdown(mock_manager_class, mock_manager, tmp_path):
    """Test exporting profile to Markdown."""
    mock_manager_class.return_value = mock_manager
    
    profile = SystemProfile()
    output_file = tmp_path / "profile.md"
    
    await profile.export_to_file(output_file, format="markdown")
    
    assert output_file.exists()
    content = output_file.read_text()
    assert "# " in content or "## " in content  # Markdown headers


@pytest.mark.asyncio
@patch("updt.profile.UpdateManager")
async def test_system_profile_export_text(mock_manager_class, mock_manager, tmp_path):
    """Test exporting profile to text."""
    mock_manager_class.return_value = mock_manager
    
    profile = SystemProfile()
    output_file = tmp_path / "profile.txt"
    
    await profile.export_to_file(output_file, format="text")
    
    assert output_file.exists()
    content = output_file.read_text()
    assert len(content) > 0
