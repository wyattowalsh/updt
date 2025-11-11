"""Plugin system for package managers."""

from .base import PluginBase
from .registry import PluginRegistry

__all__ = ["PluginBase", "PluginRegistry"]
