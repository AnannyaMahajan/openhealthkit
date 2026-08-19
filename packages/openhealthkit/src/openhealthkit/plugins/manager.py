import inspect
from typing import Any

from openhealthkit.plugins.base import BasePlugin
from openhealthkit.utils.logger import logger


class PluginManager:
    """Manager for registering, discovering, and dispatching event hooks to active plugins."""

    def __init__(self) -> None:
        self.plugins: dict[str, BasePlugin] = {}

    def register_plugin(self, plugin: BasePlugin) -> None:
        if plugin.plugin_name in self.plugins:
            logger.warning(f"Plugin '{plugin.plugin_name}' is being re-registered.")
        self.plugins[plugin.plugin_name] = plugin
        logger.info(f"Registered OpenHealthKit Plugin: '{plugin.plugin_name}' (v{plugin.version})")

    def unregister_plugin(self, plugin_name: str) -> None:
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logger.info(f"Unregistered OpenHealthKit Plugin: '{plugin_name}'")

    async def dispatch_event(self, event_name: str, **kwargs: Any) -> None:

        for name, plugin in self.plugins.items():
            handler = getattr(plugin, event_name, None)
            if handler and callable(handler):
                try:
                    if inspect.iscoroutinefunction(handler):
                        await handler(**kwargs)
                    else:
                        handler(**kwargs)
                except Exception as exc:
                    logger.error(f"Error executing event '{event_name}' in plugin '{name}': {exc}")


plugin_manager = PluginManager()
