"""Plugin registry for managing package manager plugins."""


from loguru import logger

from .base import PluginBase


class PluginRegistry:
    """Registry for managing available plugins."""

    def __init__(self) -> None:
        """Initialize the plugin registry."""
        self._plugins: dict[str, type[PluginBase]] = {}

    def register(self, plugin_class: type[PluginBase]) -> None:
        """Register a plugin class.

        Args:
            plugin_class: Plugin class to register
        """
        plugin_name = plugin_class.__name__.replace("Plugin", "").lower()
        self._plugins[plugin_name] = plugin_class
        logger.debug(f"Registered plugin: {plugin_name}")

    def get(self, name: str) -> type[PluginBase] | None:
        """Get a plugin class by name.

        Args:
            name: Plugin name

        Returns:
            Plugin class or None if not found
        """
        return self._plugins.get(name.lower())

    def get_all(self) -> dict[str, type[PluginBase]]:
        """Get all registered plugins.

        Returns:
            Dictionary of plugin name to plugin class
        """
        return self._plugins.copy()

    def list_names(self) -> list[str]:
        """Get list of all registered plugin names.

        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())


# Global plugin registry instance
registry = PluginRegistry()
