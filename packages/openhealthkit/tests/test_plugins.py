import pytest
from openhealthkit.plugins import ConsoleNotificationPlugin, plugin_manager


@pytest.mark.asyncio
async def test_plugin_registration_and_dispatch():
    plugin = ConsoleNotificationPlugin()
    plugin_manager.register_plugin(plugin)

    assert "console_notification_plugin" in plugin_manager.plugins

    class MockAlert:
        title = "Mock High Water Turbidity"
        severity = "HIGH"

    await plugin_manager.dispatch_event("on_alert_triggered", alert=MockAlert(), observation=None)
    plugin_manager.unregister_plugin("console_notification_plugin")
    assert "console_notification_plugin" not in plugin_manager.plugins
