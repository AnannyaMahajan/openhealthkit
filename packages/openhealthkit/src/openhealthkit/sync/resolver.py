import enum
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any


class ConflictStrategy(str, enum.Enum):
    SERVER_WINS = "SERVER_WINS"
    CLIENT_WINS = "CLIENT_WINS"
    LAST_WRITE_WINS = "LAST_WRITE_WINS"
    CUSTOM = "CUSTOM"


class ConflictResolver:
    """Handles conflict detection and resolution between client payloads and server entities."""

    def __init__(
        self,
        default_strategy: ConflictStrategy = ConflictStrategy.SERVER_WINS,
        custom_callback: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
    ):
        self.default_strategy = default_strategy
        self.custom_callback = custom_callback

    def _normalize_tz(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)

    def detect_conflict(
        self,
        client_payload: dict[str, Any],
        client_timestamp: datetime,
        server_entity: dict[str, Any],
        server_updated_at: datetime,
    ) -> bool:
        """
        Detects if a conflict exists. A conflict occurs if server_updated_at is strictly
        newer than client_timestamp and payload field values differ.
        """
        c_ts = self._normalize_tz(client_timestamp)
        s_ts = self._normalize_tz(server_updated_at)
        if s_ts > c_ts:
            for key, val in client_payload.items():
                if (
                    key in server_entity
                    and server_entity[key] != val
                    and key not in ("id", "updated_at", "created_at")
                ):
                    return True
        return False

    def resolve(
        self,
        client_payload: dict[str, Any],
        client_timestamp: datetime,
        server_entity: dict[str, Any],
        server_updated_at: datetime,
        strategy: ConflictStrategy | None = None,
    ) -> tuple[dict[str, Any], str]:
        """
        Resolves a conflict based on the chosen strategy.
        Returns tuple of (winning_payload, resolution_summary).
        """
        active_strategy = strategy or self.default_strategy
        c_ts = self._normalize_tz(client_timestamp)
        s_ts = self._normalize_tz(server_updated_at)

        if active_strategy == ConflictStrategy.SERVER_WINS:
            return server_entity, "Resolved using SERVER_WINS: preserved existing server entity."

        elif active_strategy == ConflictStrategy.CLIENT_WINS:
            merged = {**server_entity, **client_payload}
            return (
                merged,
                "Resolved using CLIENT_WINS: overwrote server entity with client payload.",
            )

        elif active_strategy == ConflictStrategy.LAST_WRITE_WINS:
            if c_ts >= s_ts:
                merged = {**server_entity, **client_payload}
                return (
                    merged,
                    f"Resolved using LAST_WRITE_WINS: client timestamp ({c_ts}) >= server ({s_ts}).",
                )
            else:
                return (
                    server_entity,
                    f"Resolved using LAST_WRITE_WINS: server timestamp ({s_ts}) > client ({c_ts}).",
                )

        elif active_strategy == ConflictStrategy.CUSTOM and self.custom_callback:
            resolved = self.custom_callback(client_payload, server_entity)
            return resolved, "Resolved using CUSTOM callback function."

        # Fallback to SERVER_WINS
        return server_entity, "Fallback resolution: SERVER_WINS."

