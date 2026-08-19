"""
OpenHealthKit Offline Sync Client Example
Demonstrates queuing mutations into local SQLite database and pushing to server.
"""

from openhealthkit.sync import OfflineSyncClient


def run_client_demo():
    client = OfflineSyncClient(
        client_id="field-tablet-device-01",
        server_url="http://localhost:8000",
        db_path="client_offline.db",
    )

    print("📱 Queuing offline health record creation...")
    client.enqueue(
        entity_type="health_record",
        entity_id="f47ac10b-58cc-4372-a567-0e02b2c3d479",
        action="CREATE",
        payload={
            "patient_identifier": "SYNTH-OFFLINE-001",
            "age_years": 29,
            "gender": "Male",
        },
    )

    pending = client.get_pending_items()
    print(f"📦 Items in local SQLite pending queue: {len(pending)}")

    print("📡 Attempting remote sync push...")
    result = client.sync_push()
    print("Sync Result:", result)


if __name__ == "__main__":
    run_client_demo()
