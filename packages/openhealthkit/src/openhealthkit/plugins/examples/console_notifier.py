from typing import Any

from openhealthkit.plugins.base import BasePlugin
from openhealthkit.utils.logger import logger


class ConsoleNotificationPlugin(BasePlugin):
    """Example plugin that prints triggered alerts and sync summaries to standard log console."""

    @property
    def plugin_name(self) -> str:
        return "console_notification_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def on_alert_triggered(self, alert: Any, observation: Any, **kwargs: Any) -> None:
        logger.info(
            f"📢 [CONSOLE PLUGIN] Alert Notified! Title: '{getattr(alert, 'title', '')}', Severity: '{getattr(alert, 'severity', '')}'"
        )

    async def on_sync_completed(self, sync_summary: dict[str, Any], **kwargs: Any) -> None:
        logger.info(f"📢 [CONSOLE PLUGIN] Sync batch completed! Summary: {sync_summary}")
