import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.models.health_record import HealthRecord, Observation
from openhealthkit.models.organization import Community
from openhealthkit.models.sync import SyncAction, SyncRecord, SyncState
from openhealthkit.schemas.sync import (
    SyncItemStatus,
    SyncPullItem,
    SyncPullRequest,
    SyncPullResponse,
    SyncPushItem,
    SyncPushRequest,
    SyncPushResponse,
)
from openhealthkit.sync.resolver import ConflictResolver, ConflictStrategy
from openhealthkit.utils.logger import logger
from openhealthkit.utils.time import utc_now


class SyncEngine:
    """Core synchronization engine for receiving client pushes and serving pulls."""

    def __init__(self, resolver: ConflictResolver | None = None):
        self.resolver = resolver or ConflictResolver(default_strategy=ConflictStrategy.SERVER_WINS)

    async def process_push(self, db: AsyncSession, push_req: SyncPushRequest) -> SyncPushResponse:
        results: list[SyncItemStatus] = []
        processed_count = 0
        success_count = 0
        conflict_count = 0
        failed_count = 0

        for item in push_req.items:
            processed_count += 1
            try:
                status = await self._process_single_item(db, push_req.client_id, item)
                results.append(status)
                if status.state == SyncState.SYNCED:
                    success_count += 1
                elif status.state == SyncState.CONFLICT:
                    conflict_count += 1
                else:
                    failed_count += 1
            except Exception as exc:
                logger.error(f"Error processing sync item {item.entity_id}: {exc}")
                failed_count += 1
                results.append(
                    SyncItemStatus(
                        entity_type=item.entity_type,
                        entity_id=item.entity_id,
                        state=SyncState.FAILED,
                        message=str(exc),
                    )
                )

        await db.commit()

        return SyncPushResponse(
            client_id=push_req.client_id,
            processed_count=processed_count,
            success_count=success_count,
            conflict_count=conflict_count,
            failed_count=failed_count,
            results=results,
        )

    async def _process_single_item(
        self, db: AsyncSession, client_id: str, item: SyncPushItem
    ) -> SyncItemStatus:
        entity_type = item.entity_type.lower()

        # Audit sync record in DB
        sync_log = SyncRecord(
            client_id=client_id,
            entity_type=item.entity_type,
            entity_id=item.entity_id,
            action=item.action.value,
            payload_json=json.dumps(item.payload),
            state=SyncState.SYNCING.value,
            client_timestamp=item.client_timestamp,
        )
        db.add(sync_log)

        if entity_type == "health_record":
            return await self._sync_health_record(db, sync_log, item)
        elif entity_type == "observation":
            return await self._sync_observation(db, sync_log, item)
        elif entity_type == "community":
            return await self._sync_community(db, sync_log, item)
        else:
            sync_log.state = SyncState.FAILED.value
            sync_log.error_message = f"Unsupported entity type '{item.entity_type}'"
            return SyncItemStatus(
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                state=SyncState.FAILED,
                message=sync_log.error_message,
            )

    async def _sync_health_record(
        self, db: AsyncSession, sync_log: SyncRecord, item: SyncPushItem
    ) -> SyncItemStatus:
        stmt = select(HealthRecord).where(HealthRecord.id == item.entity_id)
        res = await db.execute(stmt)
        existing = res.scalars().first()

        if item.action == SyncAction.CREATE:
            if existing:
                # Conflict or already exists
                sync_log.state = SyncState.CONFLICT.value
                server_dict = {
                    "id": existing.id,
                    "patient_identifier": existing.patient_identifier,
                    "age_years": existing.age_years,
                    "gender": existing.gender,
                    "community_id": existing.community_id,
                    "updated_at": existing.updated_at.isoformat(),
                }
                sync_log.conflict_data_json = json.dumps(server_dict)
                return SyncItemStatus(
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    state=SyncState.CONFLICT,
                    message="Entity already exists on server during CREATE",
                    server_entity=server_dict,
                )

            record = HealthRecord(
                id=item.entity_id,
                patient_identifier=item.payload.get("patient_identifier", "UNKNOWN"),
                age_years=item.payload.get("age_years"),
                gender=item.payload.get("gender"),
                community_id=item.payload.get("community_id"),
                metadata_json=json.dumps(item.payload.get("metadata", {}))
                if item.payload.get("metadata")
                else None,
            )
            db.add(record)
            sync_log.state = SyncState.SYNCED.value
            sync_log.synced_at = utc_now()
            return SyncItemStatus(
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                state=SyncState.SYNCED,
                message="Successfully created health record",
            )

        elif item.action == SyncAction.UPDATE:
            if not existing:
                sync_log.state = SyncState.FAILED.value
                sync_log.error_message = "Record not found for UPDATE"
                return SyncItemStatus(
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    state=SyncState.FAILED,
                    message="Record not found on server",
                )

            server_dict = {
                "patient_identifier": existing.patient_identifier,
                "age_years": existing.age_years,
                "gender": existing.gender,
                "community_id": existing.community_id,
            }

            has_conflict = self.resolver.detect_conflict(
                item.payload, item.client_timestamp, server_dict, existing.updated_at
            )

            if has_conflict:
                resolved, msg = self.resolver.resolve(
                    item.payload, item.client_timestamp, server_dict, existing.updated_at
                )
                existing.patient_identifier = resolved.get(
                    "patient_identifier", existing.patient_identifier
                )
                existing.age_years = resolved.get("age_years", existing.age_years)
                existing.gender = resolved.get("gender", existing.gender)
                existing.community_id = resolved.get("community_id", existing.community_id)

                sync_log.state = SyncState.SYNCED.value
                sync_log.synced_at = utc_now()
                return SyncItemStatus(
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    state=SyncState.SYNCED,
                    message=f"Conflict resolved during UPDATE: {msg}",
                )

            # Apply update cleanly
            if "patient_identifier" in item.payload:
                existing.patient_identifier = item.payload["patient_identifier"]
            if "age_years" in item.payload:
                existing.age_years = item.payload["age_years"]
            if "gender" in item.payload:
                existing.gender = item.payload["gender"]
            if "community_id" in item.payload:
                existing.community_id = item.payload["community_id"]

            sync_log.state = SyncState.SYNCED.value
            sync_log.synced_at = utc_now()
            return SyncItemStatus(
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                state=SyncState.SYNCED,
                message="Successfully updated health record",
            )

        elif item.action == SyncAction.DELETE:
            if existing:
                existing.is_deleted = True
            sync_log.state = SyncState.SYNCED.value
            sync_log.synced_at = utc_now()
            return SyncItemStatus(
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                state=SyncState.SYNCED,
                message="Successfully marked health record as soft-deleted",
            )

        return SyncItemStatus(
            entity_type=item.entity_type,
            entity_id=item.entity_id,
            state=SyncState.FAILED,
            message="Unknown action",
        )

    async def _sync_observation(
        self, db: AsyncSession, sync_log: SyncRecord, item: SyncPushItem
    ) -> SyncItemStatus:
        stmt = select(Observation).where(Observation.id == item.entity_id)
        res = await db.execute(stmt)
        existing = res.scalars().first()

        if item.action == SyncAction.CREATE:
            if existing:
                sync_log.state = SyncState.SYNCED.value
                return SyncItemStatus(
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    state=SyncState.SYNCED,
                    message="Observation already exists on server",
                )

            obs = Observation(
                id=item.entity_id,
                health_record_id=item.payload.get("health_record_id"),
                observation_type=item.payload.get("observation_type", "generic"),
                value_number=item.payload.get("value_number"),
                value_text=item.payload.get("value_text"),
                unit=item.payload.get("unit"),
            )
            db.add(obs)
            sync_log.state = SyncState.SYNCED.value
            sync_log.synced_at = utc_now()

            # Trigger alert engine evaluation asynchronously
            from openhealthkit.alerts.engine import alert_engine

            await alert_engine.evaluate_observation(db, obs)

            return SyncItemStatus(
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                state=SyncState.SYNCED,
                message="Observation synced and evaluated by alert engine",
            )

        sync_log.state = SyncState.SYNCED.value
        return SyncItemStatus(
            entity_type=item.entity_type,
            entity_id=item.entity_id,
            state=SyncState.SYNCED,
            message="Processed observation action",
        )

    async def _sync_community(
        self, db: AsyncSession, sync_log: SyncRecord, item: SyncPushItem
    ) -> SyncItemStatus:
        stmt = select(Community).where(Community.id == item.entity_id)
        res = await db.execute(stmt)
        existing = res.scalars().first()

        if item.action == SyncAction.CREATE and not existing:
            comm = Community(
                id=item.entity_id,
                name=item.payload.get("name", "Unnamed Community"),
                location_name=item.payload.get("location_name"),
                organization_id=item.payload.get("organization_id"),
            )
            db.add(comm)

        sync_log.state = SyncState.SYNCED.value
        sync_log.synced_at = utc_now()
        return SyncItemStatus(
            entity_type=item.entity_type,
            entity_id=item.entity_id,
            state=SyncState.SYNCED,
            message="Processed community sync item",
        )

    async def process_pull(self, db: AsyncSession, pull_req: SyncPullRequest) -> SyncPullResponse:
        items: list[SyncPullItem] = []
        since = pull_req.since_timestamp

        # Pull updated HealthRecords
        hr_stmt = select(HealthRecord)
        if since:
            hr_stmt = hr_stmt.where(HealthRecord.updated_at > since)
        hr_res = await db.execute(hr_stmt)
        for hr in hr_res.scalars().all():
            items.append(
                SyncPullItem(
                    entity_type="health_record",
                    entity_id=hr.id,
                    action=SyncAction.DELETE if hr.is_deleted else SyncAction.UPDATE,
                    payload={
                        "patient_identifier": hr.patient_identifier,
                        "age_years": hr.age_years,
                        "gender": hr.gender,
                        "community_id": hr.community_id,
                        "is_deleted": hr.is_deleted,
                    },
                    updated_at=hr.updated_at,
                )
            )

        # Pull updated Observations
        obs_stmt = select(Observation)
        if since:
            obs_stmt = obs_stmt.where(Observation.updated_at > since)
        obs_res = await db.execute(obs_stmt)
        for obs in obs_res.scalars().all():
            items.append(
                SyncPullItem(
                    entity_type="observation",
                    entity_id=obs.id,
                    action=SyncAction.CREATE,
                    payload={
                        "health_record_id": obs.health_record_id,
                        "observation_type": obs.observation_type,
                        "value_number": obs.value_number,
                        "value_text": obs.value_text,
                        "unit": obs.unit,
                        "observed_at": obs.observed_at.isoformat(),
                    },
                    updated_at=obs.updated_at,
                )
            )

        return SyncPullResponse(server_timestamp=utc_now(), items=items)


sync_engine = SyncEngine()
