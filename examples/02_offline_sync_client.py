"""
OpenHealthKit Beginner-Friendly Offline Sync Client Example

Demonstrates:
1. Initializing local SQLite offline sync queue.
2. Queuing synthetic health records offline when disconnected.
3. Inspecting pending synchronization queue state.
4. Attempting remote push synchronization to server upon reconnection.

Usage:
    python examples/02_offline_sync_client.py
"""

import os
import uuid
from openhealthkit.sync import OfflineSyncClient


def run_client_demo():
    print("=" * 60)
    print("  OpenHealthKit - Offline Synchronization Example")
    print("=" * 60)

    db_filename = "client_offline_demo.db"

    # Clean up previous demo database if exists
    if os.path.exists(db_filename):
        try:
            os.remove(db_filename)
        except OSError:
            pass

    # 1. Initialize offline client with local SQLite store
    print("\n[1] Initializing OfflineSyncClient with local SQLite store...")
    client = OfflineSyncClient(
        client_id="field-tablet-device-01",
        server_url="http://localhost:8000",
        db_path=db_filename,
    )
    print(f"    SQLite Database Path: {db_filename}")

    # 2. Queue synthetic health record offline (simulating no connectivity)
    record_id = str(uuid.uuid4())
    print("\n[2] Queuing offline health record creation (No network connection required)...")
    client.enqueue(
        entity_type="health_record",
        entity_id=record_id,
        action="CREATE",
        payload={
            "patient_identifier": "SYNTH-OFFLINE-DEMO-001",
            "age_years": 29,
            "gender": "Female",
            "metadata_json": '{"community_id": "COMM-01", "location": "District 4"}',
        },
    )
    print(f"    Queued Record ID: {record_id}")

    # 3. Inspect pending sync queue
    pending_items = client.get_pending_items()
    print("\n[3] Inspecting local SQLite queue state...")
    print(f"    Total items in pending queue: {len(pending_items)}")
    if pending_items:
        first_item = pending_items[0]
        print(f"    Item 1 Action: {first_item['action']} {first_item['entity_type']}")
        print(f"    Item 1 Timestamp: {first_item['client_timestamp']}")

    local_queue_success = len(pending_items) > 0

    # 4. Attempt remote sync push upon reconnection
    print("\n[4] Attempting remote sync push to server (Simulating reconnection)...")
    result = client.sync_push()
    sync_status = result.get("status")

    remote_sync_success = sync_status == "success" or (
        isinstance(sync_status, str) and sync_status != "error" and sync_status != "network_error"
    )

    print("\n" + "=" * 60)
    print("  SUMMARY OF RESULTS")
    print("=" * 60)

    if local_queue_success:
        print("  LOCAL OFFLINE QUEUE: SUCCESS")
    else:
        print("  LOCAL OFFLINE QUEUE: FAILED")

    if remote_sync_success:
        print("  REMOTE SYNC: SUCCESS")
        print("  All local mutations successfully pushed to server!")
    else:
        print("  REMOTE SYNC: FAILED")
        reason = result.get("text") or result.get("error") or f"HTTP Status {result.get('code')}"
        if "Could not validate credentials" in str(reason):
            reason = "Could not validate credentials"
        print(f"  Reason: {reason}")
        print("\n  Explanation:")
        print("  - Local offline queue succeeded: Mutations were safely stored in local SQLite.")
        print("  - Remote sync failed: Pushing to remote server requires active connectivity")
        print("    and a valid JWT authentication token (pass auth_token to sync_push).")

    print("=" * 60)


if __name__ == "__main__":
    run_client_demo()
