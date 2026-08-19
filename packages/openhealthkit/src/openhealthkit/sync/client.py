import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class OfflineSyncClient:
    """
    Developer SDK client for offline-first local data queuing and remote synchronization.
    Maintains a local SQLite queue database for pending offline mutations.
    """

    def __init__(self, client_id: str, server_url: str, db_path: str = "client_sync.db"):
        self.client_id = client_id
        self.server_url = server_url.rstrip("/")
        self.db_path = db_path
        self._init_local_db()

    def _init_local_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_queue (
                    id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'PENDING',
                    client_timestamp TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def enqueue(
        self, entity_type: str, entity_id: str, action: str, payload: dict[str, Any]
    ) -> str:
        record_id = str(uuid.uuid4())
        now = utc_now_iso()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO pending_queue (id, client_id, entity_type, entity_id, action, payload, state, client_timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
                """,
                (
                    record_id,
                    self.client_id,
                    entity_type,
                    entity_id,
                    action.upper(),
                    json.dumps(payload),
                    now,
                    now,
                ),
            )
        return record_id

    def get_pending_items(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM pending_queue WHERE state IN ('PENDING', 'FAILED') ORDER BY created_at ASC"
            )
            rows = cursor.fetchall()
            items = []
            for row in rows:
                items.append(
                    {
                        "id": row["id"],
                        "client_id": row["client_id"],
                        "entity_type": row["entity_type"],
                        "entity_id": row["entity_id"],
                        "action": row["action"],
                        "payload": json.loads(row["payload"]),
                        "client_timestamp": row["client_timestamp"],
                    }
                )
            return items

    def sync_push(self, auth_token: str | None = None) -> dict[str, Any]:
        pending = self.get_pending_items()
        if not pending:
            return {"status": "no_pending_items", "count": 0}

        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        push_payload = {
            "client_id": self.client_id,
            "items": [
                {
                    "client_id": item["client_id"],
                    "entity_type": item["entity_type"],
                    "entity_id": item["entity_id"],
                    "action": item["action"],
                    "payload": item["payload"],
                    "client_timestamp": item["client_timestamp"],
                }
                for item in pending
            ],
        }

        try:
            response = httpx.post(
                f"{self.server_url}/api/v1/sync/push",
                json=push_payload,
                headers=headers,
                timeout=10.0,
            )
            if response.status_code == 200:
                data = response.json()
                # Update local queue states based on results
                with sqlite3.connect(self.db_path) as conn:
                    for result in data.get("results", []):
                        ent_id = result.get("entity_id")
                        st = result.get("state")
                        conn.execute(
                            "UPDATE pending_queue SET state = ? WHERE entity_id = ?",
                            (st, ent_id),
                        )
                return data
            else:
                return {"status": "error", "code": response.status_code, "text": response.text}
        except Exception as exc:
            return {"status": "network_error", "error": str(exc)}
