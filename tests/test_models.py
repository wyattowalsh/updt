"""Tests for data models."""

from updtr.models.update import UpdateInfo, UpdateResult, UpdateStatus


def test_update_info_creation() -> None:
    """Test creating UpdateInfo."""
    info = UpdateInfo(
        ecosystem="npm",
        package="express",
        current_version="4.18.0",
        latest_version="4.19.0",
        is_global=True,
    )
    assert info.ecosystem == "npm"
    assert info.package == "express"
    assert info.current_version == "4.18.0"
    assert info.latest_version == "4.19.0"
    assert info.is_global is True
    assert info.status == UpdateStatus.PENDING


def test_update_status_enum() -> None:
    """Test UpdateStatus enum values."""
    assert UpdateStatus.PENDING.value == "pending"
    assert UpdateStatus.SUCCESS.value == "success"
    assert UpdateStatus.FAILED.value == "failed"
    assert UpdateStatus.AVAILABLE.value == "available"


def test_update_result_creation() -> None:
    """Test creating UpdateResult."""
    info = UpdateInfo(
        ecosystem="brew",
        package="python",
        current_version="3.11.0",
        latest_version="3.12.0",
    )
    result = UpdateResult(
        update_info=info,
        status=UpdateStatus.SUCCESS,
        message="Update successful",
    )
    assert result.status == UpdateStatus.SUCCESS
    assert result.message == "Update successful"
    assert result.update_info.package == "python"
