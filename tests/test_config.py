"""Tests for configuration models."""

from updtr.models.config import EcosystemConfig, UpdtConfig


def test_ecosystem_config_defaults() -> None:
    """Test default ecosystem configuration."""
    config = EcosystemConfig()
    assert config.brew is True
    assert config.npm is True
    assert config.uv is True


def test_updtr_config_defaults() -> None:
    """Test default updtr configuration."""
    config = UpdtConfig()
    assert config.log_level == "INFO"
    assert config.log_format == "text"
    assert config.default_mode == "plan"
    assert config.dry_run is False
    assert config.max_concurrent_updates == 5
    assert config.timeout == 300


def test_updtr_config_custom() -> None:
    """Test custom configuration."""
    config = UpdtConfig(
        log_level="DEBUG",
        log_format="text",
        default_mode="run",
        dry_run=True,
    )
    assert config.log_level == "DEBUG"
    assert config.log_format == "text"
    assert config.default_mode == "run"
    assert config.dry_run is True


def test_ecosystem_config_partial() -> None:
    """Test partial ecosystem configuration."""
    config = EcosystemConfig(brew=False, npm=False)
    assert config.brew is False
    assert config.npm is False
    assert config.uv is True  # Still default
