import uuid
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from openhealthkit.models.health_record import HealthRecord, Observation
from openhealthkit.models.sync import SyncState
from openhealthkit.schemas.sync import (
    SyncAction,
    SyncPushItem,
    SyncPushRequest,
    SyncPullRequest,
)

from openhealthkit.sync import sync_engine
from openhealthkit.sync.resolver import ConflictResolver, ConflictStrategy


@pytest.mark.asyncio
async def test_sync_engine_offline_create_update_delete(db_session: AsyncSession):
    client_id = "test-device-01"
    record_id = str(uuid.uuid4())

    # 1. Offline CREATE
    create_item = SyncPushItem(
        client_id=client_id,
        entity_type="health_record",
        entity_id=record_id,
        action=SyncAction.CREATE,
        payload={"patient_identifier": "SYNTH-PAT-001", "age_years": 35, "gender": "Female"},
        client_timestamp=datetime.now(timezone.utc),
    )
    push_req = SyncPushRequest(client_id=client_id, items=[create_item])
    push_res = await sync_engine.process_push(db_session, push_req)

    assert push_res.success_count == 1
    assert push_res.results[0].state == SyncState.SYNCED

    # 2. Offline UPDATE
    update_item = SyncPushItem(
        client_id=client_id,
        entity_type="health_record",
        entity_id=record_id,
        action=SyncAction.UPDATE,
        payload={"age_years": 36},
        client_timestamp=datetime.now(timezone.utc),
    )
    push_req2 = SyncPushRequest(client_id=client_id, items=[update_item])
    push_res2 = await sync_engine.process_push(db_session, push_req2)
    assert push_res2.success_count == 1

    # 3. Offline DELETE (soft delete)
    delete_item = SyncPushItem(
        client_id=client_id,
        entity_type="health_record",
        entity_id=record_id,
        action=SyncAction.DELETE,
        payload={},
        client_timestamp=datetime.now(timezone.utc),
    )
    push_req3 = SyncPushRequest(client_id=client_id, items=[delete_item])
    push_res3 = await sync_engine.process_push(db_session, push_req3)
    assert push_res3.success_count == 1


@pytest.mark.asyncio
async def test_sync_conflict_resolution_strategies():
    client_ts = datetime.now(timezone.utc)
    server_ts = client_ts - timedelta(minutes=5)
    client_payload = {"age_years": 40, "gender": "Male"}
    server_payload = {"age_years": 35, "gender": "Male"}

    # SERVER_WINS
    server_resolver = ConflictResolver(default_strategy=ConflictStrategy.SERVER_WINS)
    res_server, _ = server_resolver.resolve(client_payload, client_ts, server_payload, server_ts)
    assert res_server["age_years"] == 35

    # CLIENT_WINS
    client_resolver = ConflictResolver(default_strategy=ConflictStrategy.CLIENT_WINS)
    res_client, _ = client_resolver.resolve(client_payload, client_ts, server_payload, server_ts)
    assert res_client["age_years"] == 40

    # LAST_WRITE_WINS (client timestamp newer)
    lww_resolver = ConflictResolver(default_strategy=ConflictStrategy.LAST_WRITE_WINS)
    res_lww, _ = lww_resolver.resolve(client_payload, client_ts, server_payload, server_ts)
    assert res_lww["age_years"] == 40

    # CUSTOM resolver callback
    def custom_merge(client_data, server_data):
        return {"age_years": (client_data["age_years"] + server_data["age_years"]) // 2}

    custom_resolver = ConflictResolver(default_strategy=ConflictStrategy.CUSTOM, custom_callback=custom_merge)
    res_custom, _ = custom_resolver.resolve(client_payload, client_ts, server_payload, server_ts)
    assert res_custom["age_years"] == 37



@pytest.mark.asyncio
async def test_sync_duplicate_and_out_of_order_operations(db_session: AsyncSession):
    client_id = "test-device-02"
    obs_id = str(uuid.uuid4())
    rec_id = str(uuid.uuid4())

    # Create health record first
    rec = HealthRecord(id=rec_id, patient_identifier="SYNTH-PAT-002")
    db_session.add(rec)
    await db_session.commit()

    item = SyncPushItem(
        client_id=client_id,
        entity_type="observation",
        entity_id=obs_id,
        action=SyncAction.CREATE,
        payload={"health_record_id": rec_id, "observation_type": "body_temp_c", "value_number": 38.5},
        client_timestamp=datetime.now(timezone.utc),
    )

    # First push
    res1 = await sync_engine.process_push(db_session, SyncPushRequest(client_id=client_id, items=[item]))
    assert res1.success_count == 1

    # Duplicate push (idempotency check)
    res2 = await sync_engine.process_push(db_session, SyncPushRequest(client_id=client_id, items=[item]))
    assert res2.success_count == 1
    assert "already exists" in res2.results[0].message


@pytest.mark.asyncio
async def test_sync_pull_operations(db_session: AsyncSession):
    # Pull changes
    pull_req = SyncPullRequest(client_id="test-device-03", since_timestamp=None)
    pull_res = await sync_engine.process_pull(db_session, pull_req)
    assert isinstance(pull_res.items, list)


def test_offline_sync_client(tmp_path):
    from openhealthkit.sync.client import OfflineSyncClient
    from unittest.mock import patch, MagicMock

    db_file = str(tmp_path / "test_client_sync.db")
    client = OfflineSyncClient(client_id="device-99", server_url="http://localhost:8000", db_path=db_file)

    # Empty queue push
    res_empty = client.sync_push()
    assert res_empty["status"] == "no_pending_items"

    # Enqueue item
    req_id = client.enqueue(
        entity_type="health_record",
        entity_id="rec-99",
        action="CREATE",
        payload={"patient_identifier": "SYNTH-PAT-999"},
    )
    assert req_id is not None

    pending = client.get_pending_items()
    assert len(pending) == 1
    assert pending[0]["entity_id"] == "rec-99"

    # Mock successful HTTP push
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "client_id": "device-99",
        "processed_count": 1,
        "success_count": 1,
        "results": [{"entity_id": "rec-99", "state": "SYNCED"}],
    }

    with patch("httpx.post", return_value=mock_resp):
        res_push = client.sync_push(auth_token="test_token")
        assert res_push["processed_count"] == 1


@pytest.mark.asyncio
async def test_unsupported_sync_entity_type(db_session: AsyncSession):
    item = SyncPushItem(
        client_id="device-01",
        entity_type="unknown_entity_kind",
        entity_id="123",
        action=SyncAction.CREATE,
        payload={},
        client_timestamp=datetime.now(timezone.utc),
    )
    req = SyncPushRequest(client_id="device-01", items=[item])
    res = await sync_engine.process_push(db_session, req)
    assert res.failed_count == 1
    assert "Unsupported entity type" in res.results[0].message



