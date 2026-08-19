# OpenHealthKit Examples & Tutorials

This directory contains beginner-friendly code examples demonstrating core OpenHealthKit functionality using synthetic health data.

---

## Example 1: Quickstart (`01_quickstart.py`)

Demonstrates setting up an in-memory database, registering synthetic health records, logging observations, evaluating alert rules, and computing aggregate analytics.

```bash
python examples/01_quickstart.py
```

---

## Example 2: Offline Sync Client (`02_offline_sync_client.py`)

Demonstrates the offline-first synchronization workflow:
1. Initializing a local SQLite queue (`OfflineSyncClient`).
2. Queuing synthetic health record mutations while offline.
3. Inspecting local pending queue state.
4. Pushing offline mutations to a remote OpenHealthKit server upon reconnection.

```bash
python examples/02_offline_sync_client.py
```

### Key Workflow Highlights
- **No Internet Required for Mutations**: Field devices record patient data locally in SQLite.
- **Idempotent Queue**: Records are stamped with client timestamps and UUIDs.
- **Conflict Resolution**: The remote OpenHealthKit backend automatically resolves conflicts using configurable strategies (`SERVER_WINS`, `CLIENT_WINS`, `LAST_WRITE_WINS`, or `CUSTOM`).

---

## Example 3: Custom Alert Plugin (`03_custom_plugin.py`)

Demonstrates creating custom event listeners to notify external systems when health alert rules are triggered.

```bash
python examples/03_custom_plugin.py
```

---

## Additional Documentation

- [Synchronization Architecture Documentation](../docs/synchronization.md)
- [Security & Compliance Guide](../docs/security.md)
