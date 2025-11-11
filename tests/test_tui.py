"""Tests for TUI application."""

import pytest
from unittest.mock import AsyncMock, patch

from updtr.tui.app import UpdtTUI


def test_tui_initialization():
    """Test TUI initialization."""
    tui = UpdtTUI()
    assert tui is not None
    assert tui.title == "updtr - Universal Package Dependency Tracker"


def test_tui_has_required_methods():
    """Test that TUI has required methods."""
    tui = UpdtTUI()
    assert hasattr(tui, "compose")
    assert hasattr(tui, "on_mount")
    assert hasattr(tui, "action_check_updates")
    assert hasattr(tui, "action_perform_updates")
    assert hasattr(tui, "action_quit")


@pytest.mark.asyncio
async def test_tui_check_updates_action():
    """Test TUI check updates action."""
    tui = UpdtTUI()
    
    with patch.object(tui, "manager", AsyncMock()):
        tui.manager.check_all_updates = AsyncMock(return_value=[])
        await tui.action_check_updates()


@pytest.mark.asyncio
async def test_tui_perform_updates_action():
    """Test TUI perform updates action."""
    tui = UpdtTUI()
    tui.updates = []
    
    with patch.object(tui, "manager", AsyncMock()):
        tui.manager.perform_updates = AsyncMock(return_value=[])
        await tui.action_perform_updates()
