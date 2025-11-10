"""Configuration models using Pydantic v2."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EcosystemConfig(BaseModel):
    """Configuration for individual package manager ecosystems."""

    model_config = {"extra": "allow"}  # Allow extra fields for testing

    brew: bool = True
    bundler: bool = True
    cargo: bool = True
    conda: bool = True
    gem: bool = True
    mas: bool = True
    npm: bool = True
    nvm: bool = True
    pip: bool = True
    pipx: bool = True
    pnpm: bool = True
    poetry: bool = True
    pyenv: bool = True
    rvm: bool = True
    softwareupdate: bool = True
    uv: bool = True
    yarn: bool = True


class UpdtConfig(BaseSettings):
    """Main configuration for updt using pydantic-settings."""

    model_config = SettingsConfigDict(
        env_prefix="UPDT_",
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
