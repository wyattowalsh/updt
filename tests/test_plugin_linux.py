"""Tests for Linux plugins (apt, dnf, flatpak)."""

import pytest
from unittest.mock import patch

from updtr.models.update import UpdateStatus
from updtr.plugins.apt import AptPlugin
from updtr.plugins.dnf import DnfPlugin
from updtr.plugins.flatpak import FlatpakPlugin


# APT Plugin Tests

@pytest.fixture
def apt_plugin():
    """Create an APT plugin instance."""
    return AptPlugin()


@pytest.mark.asyncio
async def test_apt_plugin_name(apt_plugin):
    """Test APT plugin name."""
    assert apt_plugin.name == "apt"


@pytest.mark.asyncio
async def test_apt_plugin_is_available_true(apt_plugin):
    """Test is_available when apt is installed."""
    with patch.object(apt_plugin, "run_command", return_value=("apt 2.0.0", "", 0)):
        result = await apt_plugin.is_available()
        assert result is True


@pytest.mark.asyncio
async def test_apt_plugin_is_available_false(apt_plugin):
    """Test is_available when apt is not installed."""
    with patch.object(apt_plugin, "run_command", return_value=("", "command not found", 127)):
        result = await apt_plugin.is_available()
        assert result is False


@pytest.mark.asyncio
async def test_apt_plugin_check_updates(apt_plugin):
    """Test check_updates for APT."""
    upgradable_output = "Listing...\ncurl/stable 7.68.0-1ubuntu2.14 amd64 [upgradable from: 7.68.0-1ubuntu2.13]"
    
    with patch.object(apt_plugin, "run_command", side_effect=[
        ("apt 2.0.0", "", 0),  # is_available
        (upgradable_output, "", 0),  # list --upgradable
    ]):
        updates = await apt_plugin.check_updates()
        assert len(updates) > 0
        assert updates[0].ecosystem == "apt"


# DNF Plugin Tests

@pytest.fixture
def dnf_plugin():
    """Create a DNF plugin instance."""
    return DnfPlugin()


@pytest.mark.asyncio
async def test_dnf_plugin_name(dnf_plugin):
    """Test DNF plugin name."""
    assert dnf_plugin.name == "dnf"


@pytest.mark.asyncio
async def test_dnf_plugin_is_available_true(dnf_plugin):
    """Test is_available when dnf is installed."""
    with patch.object(dnf_plugin, "run_command", return_value=("4.14.0", "", 0)):
        result = await dnf_plugin.is_available()
        assert result is True


@pytest.mark.asyncio
async def test_dnf_plugin_is_available_false(dnf_plugin):
    """Test is_available when dnf is not installed."""
    with patch.object(dnf_plugin, "run_command", return_value=("", "command not found", 127)):
        result = await dnf_plugin.is_available()
        assert result is False


@pytest.mark.asyncio
async def test_dnf_plugin_check_updates(dnf_plugin):
    """Test check_updates for DNF."""
    check_update_output = "curl.x86_64  7.76.1-14.el9  updates"
    rpm_output = "curl-7.76.1-13.el9"
    
    with patch.object(dnf_plugin, "run_command", side_effect=[
        ("4.14.0", "", 0),  # is_available
        (check_update_output, "", 100),  # check-update (100 = updates available)
        (rpm_output, "", 0),  # rpm query
    ]):
        updates = await dnf_plugin.check_updates()
        assert len(updates) > 0
        assert updates[0].ecosystem == "dnf"


# Flatpak Plugin Tests

@pytest.fixture
def flatpak_plugin():
    """Create a Flatpak plugin instance."""
    return FlatpakPlugin()


@pytest.mark.asyncio
async def test_flatpak_plugin_name(flatpak_plugin):
    """Test Flatpak plugin name."""
    assert flatpak_plugin.name == "flatpak"


@pytest.mark.asyncio
async def test_flatpak_plugin_is_available_true(flatpak_plugin):
    """Test is_available when flatpak is installed."""
    with patch.object(flatpak_plugin, "run_command", return_value=("Flatpak 1.12.0", "", 0)):
        result = await flatpak_plugin.is_available()
        assert result is True


@pytest.mark.asyncio
async def test_flatpak_plugin_is_available_false(flatpak_plugin):
    """Test is_available when flatpak is not installed."""
    with patch.object(flatpak_plugin, "run_command", return_value=("", "command not found", 127)):
        result = await flatpak_plugin.is_available()
        assert result is False


@pytest.mark.asyncio
async def test_flatpak_plugin_check_updates(flatpak_plugin):
    """Test check_updates for Flatpak."""
    remote_ls_output = "org.gimp.GIMP\t2.10.32\tflathub"
    installed_output = "org.gimp.GIMP/x86_64/stable\tflathub\t2.10.30"
    
    with patch.object(flatpak_plugin, "run_command", side_effect=[
        ("Flatpak 1.12.0", "", 0),  # is_available
        (remote_ls_output, "", 0),  # remote-ls
        (installed_output, "", 0),  # list
    ]):
        updates = await flatpak_plugin.check_updates()
        assert len(updates) > 0
        assert updates[0].ecosystem == "flatpak"


@pytest.mark.asyncio
async def test_flatpak_plugin_perform_update_dry_run(flatpak_plugin, sample_update_info):
    """Test perform_update in dry-run mode."""
    sample_update_info.ecosystem = "flatpak"
    sample_update_info.package = "org.gimp.GIMP"
    
    result = await flatpak_plugin.perform_update(sample_update_info, dry_run=True)
    
    assert result.status == UpdateStatus.SKIPPED
    assert "dry run" in result.message.lower()
