from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """Abstract Base Class for OpenHealthKit plugins."""

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Unique identifier for the plugin."""
        pass

    @property
    def version(self) -> str:
        return "1.0.0"

    async def on_observation_created(self, observation: Any, **kwargs: Any) -> None:
        """Hook triggered when a new health observation is registered."""
        pass

    async def on_alert_triggered(self, alert: Any, observation: Any, **kwargs: Any) -> None:
        """Hook triggered when an alert rule is fired."""
        pass

    async def on_sync_completed(self, sync_summary: dict[str, Any], **kwargs: Any) -> None:
        """Hook triggered when a sync batch completes."""
        pass
