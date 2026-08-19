"""
OpenHealthKit Custom Plugin Example
Demonstrates implementing a custom Webhook Notification Plugin.
"""

import httpx
from openhealthkit.plugins import BasePlugin, plugin_manager


class WebhookNotifierPlugin(BasePlugin):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    @property
    def plugin_name(self) -> str:
        return "webhook_notifier_plugin"

    async def on_alert_triggered(self, alert: any, observation: any, **kwargs) -> None:
        payload = {
            "event": "alert.triggered",
            "alert_id": getattr(alert, "id", None),
            "severity": getattr(alert, "severity", None),
            "title": getattr(alert, "title", None),
        }
        print(f"🔗 [WEBHOOK PLUGIN] Sending payload to {self.webhook_url}: {payload}")


if __name__ == "__main__":
    plugin = WebhookNotifierPlugin("https://hooks.slack.com/services/demo")
    plugin_manager.register_plugin(plugin)
    print("Registered plugin list:", list(plugin_manager.plugins.keys()))
