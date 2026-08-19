import pytest
from openhealthkit.i18n.engine import i18n_engine
from openhealthkit.plugins.base import BasePlugin
from openhealthkit.plugins.manager import plugin_manager


class BrokenTestPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "broken_plugin"

    async def on_observation_created(self, **kwargs) -> None:
        raise RuntimeError("Simulated plugin execution failure")


def test_i18n_missing_keys_and_fallback():
    # Valid key lookup
    assert i18n_engine.t("app_name", locale="en") == "OpenHealthKit"
    assert i18n_engine.t("app_name", locale="hi") == "ओपनहेल्थकिट"

    # Missing key fallback returns key string
    missing_val = i18n_engine.t("non_existent_translation_key", locale="en")
    assert missing_val == "non_existent_translation_key"

    # Unsupported locale fallback to default ('en')
    fallback_val = i18n_engine.t("app_name", locale="fr")
    assert fallback_val == "OpenHealthKit"


@pytest.mark.asyncio
async def test_plugin_manager_resilience():
    broken_plugin = BrokenTestPlugin()
    plugin_manager.register_plugin(broken_plugin)
    assert "broken_plugin" in plugin_manager.plugins

    # Dispatching event should handle exception gracefully without crashing caller
    try:
        await plugin_manager.dispatch_event("on_observation_created", data="test")
    except Exception as exc:
        pytest.fail(f"Plugin manager should catch plugin exceptions safely, got: {exc}")

