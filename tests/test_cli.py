"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from updt.cli import app
from updt.models.update import UpdateInfo, UpdateStatus

runner = CliRunner()


def test_cli_help():
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "updt" in result.stdout.lower()


def test_cli_version():
    """Test CLI version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0


def test_list_plugins_command():
    """Test list-plugins command."""
    result = runner.invoke(app, ["list-plugins"])
    assert result.exit_code == 0
    assert "plugins" in result.stdout.lower()


@patch("updt.cli.UpdateManager")
def test_check_command_basic(mock_manager_class):
    """Test basic check command."""
    mock_manager = AsyncMock()
    mock_manager.initialize = AsyncMock()
    mock_manager.check_all_updates = AsyncMock(return_value=[])
    mock_manager_class.return_value = mock_manager
    
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0


@patch("updt.cli.UpdateManager")
def test_check_command_with_project(mock_manager_class, tmp_path):
    """Test check command with project path."""
    mock_manager = AsyncMock()
    mock_manager.initialize = AsyncMock()
    mock_manager.check_all_updates = AsyncMock(return_value=[])
    mock_manager_class.return_value = mock_manager
    
    project_path = tmp_path / "project"
    project_path.mkdir()
    
    result = runner.invoke(app, ["check", "--project", str(project_path)])
    assert result.exit_code == 0


@patch("updt.cli.UpdateManager")
def test_check_command_with_updates(mock_manager_class):
    """Test check command with available updates."""
    mock_update = UpdateInfo(
        ecosystem="test",
        package="test-pkg",
        current_version="1.0.0",
        latest_version="2.0.0",
        status=UpdateStatus.AVAILABLE,
    )
    
    mock_manager = AsyncMock()
    mock_manager.initialize = AsyncMock()
    mock_manager.check_all_updates = AsyncMock(return_value=[mock_update])
    mock_manager_class.return_value = mock_manager
    
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0


@patch("updt.cli.UpdateManager")
def test_update_command_basic(mock_manager_class):
    """Test basic update command."""
    mock_manager = AsyncMock()
    mock_manager.initialize = AsyncMock()
    mock_manager.check_all_updates = AsyncMock(return_value=[])
    mock_manager.perform_updates = AsyncMock(return_value=[])
    mock_manager_class.return_value = mock_manager
    
    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0


@patch("updt.cli.UpdateManager")
def test_update_command_dry_run(mock_manager_class):
    """Test update command with dry-run flag."""
    from updt.models.update import UpdateResult
    
    mock_update = UpdateInfo(
        ecosystem="test",
        package="test-pkg",
        current_version="1.0.0",
        latest_version="2.0.0",
        status=UpdateStatus.AVAILABLE,
    )
    
    mock_result = UpdateResult(
        update_info=mock_update,
        status=UpdateStatus.SKIPPED,
        message="Dry run",
        duration=0.0,
    )
    
    mock_manager = AsyncMock()
    mock_manager.initialize = AsyncMock()
    mock_manager.check_all_updates = AsyncMock(return_value=[mock_update])
    mock_manager.perform_updates = AsyncMock(return_value=[mock_result])
    mock_manager_class.return_value = mock_manager
    
    result = runner.invoke(app, ["update", "--dry-run"])
    assert result.exit_code == 0
    assert "dry" in result.stdout.lower() or "skip" in result.stdout.lower()


def test_config_show_command():
    """Test config show command."""
    result = runner.invoke(app, ["config", "--show"])
    assert result.exit_code == 0


@patch("updt.cli.SystemProfile")
def test_profile_command_basic(mock_profile_class):
    """Test basic profile command."""
    mock_profile = AsyncMock()
    mock_profile.generate = AsyncMock(return_value={"ecosystems": {}})
    mock_profile_class.return_value = mock_profile
    
    result = runner.invoke(app, ["profile"])
    assert result.exit_code == 0


@patch("updt.cli.SystemProfile")
def test_profile_command_json(mock_profile_class, tmp_path):
    """Test profile command with JSON output."""
    mock_profile = AsyncMock()
    mock_profile.generate = AsyncMock(return_value={"ecosystems": {}})
    mock_profile.export_to_file = AsyncMock()
    mock_profile_class.return_value = mock_profile
    
    output_file = tmp_path / "profile.json"
    
    result = runner.invoke(app, ["profile", "--output", str(output_file), "--format", "json"])
    assert result.exit_code == 0


@patch("updt.cli.SystemProfile")
def test_profile_command_markdown(mock_profile_class, tmp_path):
    """Test profile command with Markdown output."""
    mock_profile = AsyncMock()
    mock_profile.generate = AsyncMock(return_value={"ecosystems": {}})
    mock_profile.export_to_file = AsyncMock()
    mock_profile_class.return_value = mock_profile
    
    output_file = tmp_path / "profile.md"
    
    result = runner.invoke(app, ["profile", "--output", str(output_file), "--format", "markdown"])
    assert result.exit_code == 0


def test_tui_command_import():
    """Test that TUI command is importable."""
    from updt.cli import app
    
    # Just test that the command exists
    commands = [cmd.name for cmd in app.registered_commands]
    assert "tui" in commands
