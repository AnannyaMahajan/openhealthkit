# OpenHealthKit

**Tagline:** *An offline-first open-source toolkit for building resilient community and public-health applications.*

Welcome to the documentation for **OpenHealthKit**, a modular, developer-friendly open-source software toolkit designed for public-health teams, NGOs, research organizations, and software engineers.

---

## Core Technical Building Blocks

1. **Dual DB Architecture**: Seamless support for local **SQLite** (client/edge) and production **PostgreSQL**.
2. **Offline-First Sync Engine**: Batch push/pull synchronization with conflict resolution strategies (`SERVER_WINS`, `CLIENT_WINS`, `LAST_WRITE_WINS`, `CUSTOM`).
3. **Configurable Alert Engine**: Rule-based numeric & categorical condition evaluation with cooldown protection.
4. **Role-Based Access Control (RBAC)**: JWT authentication with default `ADMIN`, `HEALTH_WORKER`, `ANALYST`, and `VIEWER` roles.
5. **i18n Localization**: Built-in support for English (`en`) and Hindi (`hi`) locale packs.
6. **Audit & Compliance**: Structured security audit logging.
7. **Extensible Plugin System**: Asynchronous event hooks (`on_observation_created`, `on_alert_triggered`, `on_sync_completed`).

---

## Quick Installation

```bash
pip install -e "./packages/openhealthkit[dev]"
```

Start API backend:

```bash
openhealthkit
```
