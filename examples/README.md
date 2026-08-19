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
2. Queuing synthetic health record mutations while offline (**LOCAL OFFLINE QUEUE: SUCCESS**).
3. Inspecting local pending queue state.
4. Attempting remote synchronization to an OpenHealthKit server (**REMOTE SYNC**).

```bash
python examples/02_offline_sync_client.py
```

### Expected Execution Behavior
- **Local Offline Queue (Success)**: Field devices record patient mutations locally in SQLite without requiring network connectivity or server access.
- **Remote Push (Requires Auth)**: When executing the example out-of-the-box without an active server or JWT bearer token, the remote sync step returns `REMOTE SYNC: FAILED (Reason: Could not validate credentials)`. Pass a valid `auth_token` parameter to `client.sync_push(auth_token=...)` once the server is running.
- **Conflict Resolution**: The remote backend resolves conflicts using configurable strategies (`SERVER_WINS`, `CLIENT_WINS`, `LAST_WRITE_WINS`, or `CUSTOM`).

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
