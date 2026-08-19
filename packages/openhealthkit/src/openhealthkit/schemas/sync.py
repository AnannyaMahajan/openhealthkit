from datetime import datetime
from typing import Any

from pydantic import BaseModel

from openhealthkit.models.sync import SyncAction, SyncState


class SyncPushItem(BaseModel):
    id: str | None = None
    client_id: str
    entity_type: str  # health_record, observation, community
    entity_id: str
    action: SyncAction
    payload: dict[str, Any]
    client_timestamp: datetime


class SyncPushRequest(BaseModel):
    client_id: str
    items: list[SyncPushItem]


class SyncItemStatus(BaseModel):
    entity_type: str
    entity_id: str
    state: SyncState
    message: str | None = None
    server_entity: dict[str, Any] | None = None


class SyncPushResponse(BaseModel):
    client_id: str
    processed_count: int
    success_count: int
    conflict_count: int
    failed_count: int
    results: list[SyncItemStatus]


class SyncPullRequest(BaseModel):
    client_id: str
    since_timestamp: datetime | None = None
    entity_types: list[str] | None = None


class SyncPullItem(BaseModel):
    entity_type: str
    entity_id: str
    action: SyncAction
    payload: dict[str, Any]
    updated_at: datetime


class SyncPullResponse(BaseModel):
    server_timestamp: datetime
    items: list[SyncPullItem]


class SyncConflictResolveRequest(BaseModel):
    sync_record_id: str
    resolution_strategy: str = "SERVER_WINS"  # SERVER_WINS, CLIENT_WINS, CUSTOM
    resolved_payload: dict[str, Any] | None = None
