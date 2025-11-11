"""Data models for updtr."""

from .config import EcosystemConfig, UpdtConfig
from .update import UpdateInfo, UpdateResult

__all__ = [
    "UpdtConfig",
    "EcosystemConfig",
    "UpdateInfo",
    "UpdateResult",
]
