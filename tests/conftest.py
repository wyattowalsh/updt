"""Shared test fixtures and configuration."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest

from updt.models.config import EcosystemConfig, UpdtConfig
from updt.models.update import UpdateInfo, UpdateStatus
from updt.plugins.base import PluginBase
from updt.plugins.registry import PluginRegistry


@pytest.fixture
def sample_config() -> UpdtConfig:
    """Create a sample configuration for testing."""
    return UpdtConfig(
        log_level="DEBUG",
        log_format="text",
        dry_run=False,
        max_concurrent_updates=5,
        timeout=300,
    )


@pytest.fixture
def sample_ecosystem_config() -> EcosystemConfig:
    """Create a sample ecosystem configuration."""
    return EcosystemConfig(
        brew=True,
        npm=True,
        pip=True,
        cargo=False,
    )


@pytest.fixture
def sample_update_info() -> UpdateInfo:
    """Create a sample update info for testing."""
    return UpdateInfo(
        ecosystem="test",
        package="test-package",
        current_version="1.0.0",
        latest_version="2.0.0",
        is_global=True,
        status=UpdateStatus.AVAILABLE,
    )


@pytest.fixture
def mock_plugin_registry() -> PluginRegistry:
    """Create a mock plugin registry."""
    registry = PluginRegistry()
    
    class MockPlugin(PluginBase):
        """Mock plugin for testing."""
        
        async def is_available(self) -> bool:
            return True
        
        async def check_updates(self, project_path: Path | None = None):
            return [
                UpdateInfo(
                    ecosystem="mock",
                    package="test-pkg",
                    current_version="1.0.0",
                    latest_version="2.0.0",
                    status=UpdateStatus.AVAILABLE,
                )
            ]
        
        async def perform_update(self, update_info, dry_run=False):
            from updt.models.update import UpdateResult
            
            return UpdateResult(
                update_info=update_info,
                status=UpdateStatus.SUCCESS if not dry_run else UpdateStatus.SKIPPED,
                message="Mock update",
                duration=0.1,
            )
    
    registry.register(MockPlugin)
    return registry


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tmp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create some dummy files
    (project_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')
    (project_dir / "requirements.txt").write_text("requests==2.28.0")
    (project_dir / "Cargo.toml").write_text('[package]\nname = "test"\nversion = "0.1.0"')
    
    return project_dir
