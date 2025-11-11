"""Update information and result models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class UpdateStatus(str, Enum):
    """Status of an update operation."""

    PENDING = "pending"
    CHECKING = "checking"
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    UPDATING = "updating"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class UpdateInfo(BaseModel):
    """Information about available updates."""

    ecosystem: str = Field(description="Package manager ecosystem")
    package: str = Field(description="Package name")
    current_version: str | None = Field(default=None, description="Current version")
    latest_version: str | None = Field(default=None, description="Latest available version")
    is_global: bool = Field(default=True, description="Whether this is a global package")
    project_path: str | None = Field(default=None, description="Project path for local packages")
    status: UpdateStatus = Field(default=UpdateStatus.PENDING, description="Update status")
    message: str | None = Field(default=None, description="Status message")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class UpdateResult(BaseModel):
    """Result of an update operation."""

    update_info: UpdateInfo = Field(description="Update information")
    status: UpdateStatus = Field(description="Final status")
    message: str = Field(description="Result message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")
    duration: float | None = Field(default=None, description="Duration in seconds")
    stdout: str | None = Field(default=None, description="Command stdout")
    stderr: str | None = Field(default=None, description="Command stderr")
    exit_code: int | None = Field(default=None, description="Command exit code")
