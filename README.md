# OpenHealthKit

> **An offline-first open-source toolkit for building resilient community and public-health applications.**

[![CI Test Suite](https://github.com/anannyamahajan/openhealthkit/actions/workflows/test.yml/badge.svg)](https://github.com/anannyamahajan/openhealthkit/actions/workflows/test.yml)
[![Lint & Type Check](https://github.com/anannyamahajan/openhealthkit/actions/workflows/lint.yml/badge.svg)](https://github.com/anannyamahajan/openhealthkit/actions/workflows/lint.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](pyproject.toml)

---

## What is OpenHealthKit?

**OpenHealthKit** is a production-quality, open-source developer toolkit built with Python, FastAPI, React, and TypeScript. It provides modular building blocks for engineers, public health developers, research teams, and NGOs building applications that must function reliably in low-connectivity, offline, or remote community environments.

---

## Why OpenHealthKit Exists

Public health workers and community health projects frequently operate in remote areas where cellular networks and internet connectivity are intermittent or non-existent. Traditional cloud-first web architectures fail when connectivity drops. OpenHealthKit provides an offline-first foundation with dual SQLite/PostgreSQL support, batch synchronization, rule-based alerts, role-based access control (RBAC), internationalization (i18n), and an interactive dashboard.

---

## Key Features

- 📱 **Offline-First Synchronization**: Local SQLite queue with batch REST push/pull API and configurable conflict resolution (`SERVER_WINS`, `CLIENT_WINS`, `LAST_WRITE_WINS`).
- ⚡ **Modern FastAPI Backend**: Asynchronous SQLAlchemy 2.0 ORM, Pydantic v2 validation, OpenAPI docs.
- 🔐 **Authentication & RBAC**: Argon2id password hashing, JWT access/refresh tokens, role enforcement (`ADMIN`, `HEALTH_WORKER`, `ANALYST`, `VIEWER`).
- 🚨 **Rule-Based Alert Engine**: Configurable observation condition triggers with cooldown protection to avoid alert fatigue.
- 🌐 **Multilingual (i18n)**: Translation manager supporting English (`en`) and Hindi (`hi`) locale packs out-of-the-box.
- 📊 **Privacy-Preserving Analytics**: Non-PII aggregate metrics, trend analytics, and health indicators.
- 🔌 **Extensible Plugin System**: Asynchronous event hooks (`on_observation_created`, `on_alert_triggered`, `on_sync_completed`).
- 🐳 **Docker & CI/CD Ready**: Multi-stage Dockerfiles, Docker Compose orchestrating API, Dashboard, PostgreSQL, and Redis, with GitHub Actions CI workflows.

---

## Architecture Diagram

```
                               ┌─────────────────────────────────────────┐
                               │       React / TypeScript Dashboard      │
                               │        (Vite + Tailwind CSS UI)         │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼ REST API /api/v1
┌──────────────────────────────┐        ┌─────────────────────────────────────────┐
│     Client Offline Device    │ ──────►│            OpenHealthKit API            │
│                              │ Push   │       (FastAPI + Pydantic v2)           │
│  - Local SQLite Store        │ ◄───── │                                         │
│  - SyncRecord Pending Queue  │ Pull   │  - Auth & RBAC Dependencies             │
│  - OfflineSyncClient SDK     │        │  - Alert & Notification Engine          │
└──────────────────────────────┘        │  - SyncEngine Conflict Resolver         │
                                        │  - I18n Engine (en / hi)                │
                                        │  - Plugin Manager                       │
                                        └────────────────────┬────────────────────┘
                                                             │
                                                             ▼ SQLAlchemy 2.0 Async
                                        ┌─────────────────────────────────────────┐
                                        │       Database Engine Abstraction       │
                                        │    (SQLite Local / PostgreSQL Prod)     │
                                        └─────────────────────────────────────────┘
```

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/anannyamahajan/openhealthkit.git
cd openhealthkit

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -e "./packages/openhealthkit[dev]"
```

### 2. Seed Synthetic Demo Data

```bash
python scripts/seed_data.py
```

### 3. Start API Server

```bash
openhealthkit
```
API Documentation will be available at `http://localhost:8000/docs`.

---

## Python SDK & Usage Examples

### 1. Creating Health Record & Logging Observation

```python
import asyncio
from openhealthkit.database import init_db, AsyncSessionLocal
from openhealthkit.models import HealthRecord, Observation
from openhealthkit.alerts import alert_engine

async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        record = HealthRecord(patient_identifier="SYNTH-PATIENT-101", age_years=32, gender="Female")
        db.add(record)
        await db.commit()

        obs = Observation(health_record_id=record.id, observation_type="fever_body_temp_c", value_number=39.1, unit="°C")
        db.add(obs)
        await db.commit()

        # Alert Engine automatically checks thresholds
        alerts = await alert_engine.evaluate_observation(db, obs)
        print(f"Triggered Alerts: {len(alerts)}")

asyncio.run(main())
```

### 2. Client Offline Sync SDK Example

```python
from openhealthkit.sync import OfflineSyncClient

client = OfflineSyncClient(
    client_id="tablet-device-01",
    server_url="http://localhost:8000",
    db_path="client_queue.db"
)

# Enqueue mutation when offline
client.enqueue(
    entity_type="health_record",
    entity_id="f47ac10b-58cc-4372-a567-0e02b2c3d479",
    action="CREATE",
    payload={"patient_identifier": "SYNTH-PATIENT-202", "age_years": 45}
)

# Push queued items when back online
result = client.sync_push()
print("Sync Push Result:", result)
```

---

## Running with Docker Compose

Run full production stack (API, PostgreSQL, Redis, and React Dashboard):

```bash
docker compose up --build
```

Access services:
- **Dashboard UI**: `http://localhost:3000`
- **FastAPI API**: `http://localhost:8000/docs`

---

## Testing & Linting

```bash
# Run pytest test suite
pytest

# Run Ruff linter
ruff check packages/openhealthkit/src

# Run Mypy type analysis
mypy packages/openhealthkit/src/openhealthkit
```

---

## Roadmap

- **v0.1.0 (Current)**: Core API, JWT auth, SQLite/PostgreSQL support, Sync Engine, Alert Engine, React Dashboard.
- **v0.2.0**: Enhanced conflict resolution UI, expanded webhook notification providers.
- **v0.3.0**: Flutter/React Native mobile client SDK bindings.
- **v1.0.0**: Production security hardening, LTS release.

---

## Security

Please read [SECURITY.md](SECURITY.md) for details on responsible vulnerability disclosure and security practices.

---

## Contributing

We welcome open-source contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## License

Licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for full details.

Copyright (c) 2026 Anannya Mahajan.
