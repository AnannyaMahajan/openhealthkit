# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-08-19

### Added
- **Core Architecture**: Initial release of `openhealthkit` Python package (Python 3.11+).
- **FastAPI REST Endpoints**: Versioned `/api/v1` routes for Authentication, Users, Organizations, Communities, Health Records, Observations, Alerts, Sync, and Analytics.
- **Dual Database Support**: SQLAlchemy 2.0 ORM supporting **SQLite** (client/offline) and **PostgreSQL** (production server).
- **Offline Sync Engine**: Batch push/pull synchronization engine with conflict resolution strategies (`SERVER_WINS`, `CLIENT_WINS`, `LAST_WRITE_WINS`, `CUSTOM`) and `OfflineSyncClient` local SQLite queue manager.
- **Rule-Based Alert Engine**: Numeric and categorical threshold condition evaluation with cooldown protection and notification logs.
- **Authentication & RBAC**: Password hashing via Argon2id, JWT token management, and role-based permissions (`ADMIN`, `HEALTH_WORKER`, `ANALYST`, `VIEWER`).
- **i18n Engine**: Localization manager with English (`en`) and Hindi (`hi`) locale packs.
- **Plugin System**: Asynchronous event hooks (`on_observation_created`, `on_alert_triggered`, `on_sync_completed`) and example `ConsoleNotificationPlugin`.
- **Demo Dashboard**: React 18 + TypeScript + Vite + Tailwind CSS dashboard app (`apps/dashboard`).
- **Database Migrations**: Baseline Alembic migration configuration (`001_initial_schema`).
- **Docker Infrastructure**: Multi-stage `Dockerfile`, `Dockerfile.dashboard`, and `docker-compose.yml` orchestrating API, Dashboard, PostgreSQL, and Redis.
- **CI/CD**: GitHub Actions workflows for testing (`test.yml`), linting (`lint.yml`), and security auditing (`security.yml`).
- **Documentation**: Comprehensive MkDocs Material documentation site and OSS governance files (`README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`).
