# Offline-First Synchronization Engine

Synchronization is a core architectural pillar of OpenHealthKit. Applications operating in remote or low-connectivity environments must allow community health workers to record patient observations offline without interruption, enqueuing changes locally and synchronizing seamlessly when connectivity is restored.

---

## Architectural Topology

```
┌──────────────────────────────────────┐          HTTP POST /api/v1/sync/push         ┌─────────────────────────────────────┐
│       Client Offline Device          │ ───────────────────────────────────────────► │        OpenHealthKit Server         │
│                                      │                                              │                                     │
│  - Local App Mutation                │                                              │  - SyncEngine Validator             │
│  - SQLite Client Queue (SyncRecord)  │ ◄─────────────────────────────────────────── │  - PostgreSQL Production Store      │
│  - OfflineSyncClient Helper          │          HTTP POST /api/v1/sync/pull         │  - ConflictResolver Engine          │
└──────────────────────────────────────┘                                              └─────────────────────────────────────┘
```

---

## Synchronization States

| State | Description |
| :--- | :--- |
| `PENDING` | Mutation recorded locally in SQLite queue; awaiting sync push. |
| `SYNCING` | Batch actively transmitted to remote API server. |
| `SYNCED` | Server successfully processed item and updated master database. |
| `CONFLICT` | Server detected conflicting concurrent updates; resolution required. |
| `FAILED` | Transaction failed due to validation or database constraints. |

---

## Conflict Resolution Strategies

1. **SERVER_WINS** (*Default*): Server entity takes precedence.
2. **CLIENT_WINS**: Client mutation overwrites server entity.
3. **LAST_WRITE_WINS**: Compares client and server timestamps.
4. **CUSTOM**: Invokes a custom Python callback function.

---

## Consistency & Guarantees

- **Eventual Consistency**: OpenHealthKit provides eventual consistency across edge devices.
- **Idempotency**: All push items use client-generated UUID primary keys.
