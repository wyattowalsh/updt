"""Configuration models using Pydantic v2."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EcosystemConfig(BaseModel):
    """Configuration for individual package manager ecosystems."""

    model_config = {"extra": "allow"}  # Allow extra fields for testing

    # macOS Ecosystem
    brew: bool = True
    mas: bool = True

    # Python Ecosystem
    uv: bool = True
    pip: bool = True
    pipx: bool = True
    conda: bool = True
    poetry: bool = True
    pyenv: bool = True

    # Node.js Ecosystem
    npm: bool = True
    yarn: bool = True
    pnpm: bool = True
    nvm: bool = True

    # Ruby Ecosystem
    gem: bool = True
    bundler: bool = True
    rvm: bool = True

    # Linux Ecosystem
    apt: bool = True
    dnf: bool = True
    flatpak: bool = True

    # Windows Ecosystem
    choco: bool = True
    scoop: bool = True
    winget: bool = True

    # Other
    cargo: bool = True
    softwareupdate: bool = True


class UpdtConfig(BaseSettings):
    """Main configuration for updtr using pydantic-settings."""

    model_config = SettingsConfigDict(
        env_prefix="UPDTR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: Literal["text", "jsonl"] = Field(
        default="text",
        description="Log output format",
    )
    log_file: Path | None = Field(
        default=None,
        description="Log file path (optional)",
    )

    # Operation mode
    default_mode: Literal["plan", "run"] = Field(
        default="plan",
        description="Default operation mode",
    )
    dry_run: bool = Field(
        default=False,
        description="Dry run mode (no actual updates)",
    )

    # Ecosystems
    ecosystems: EcosystemConfig = Field(
        default_factory=EcosystemConfig,
        description="Package manager ecosystem settings",
    )

    # Performance
    max_concurrent_updates: int = Field(
        default=5,
        description="Maximum concurrent update operations",
    )
    timeout: int = Field(
        default=300,
        description="Timeout for update operations in seconds",
    )
