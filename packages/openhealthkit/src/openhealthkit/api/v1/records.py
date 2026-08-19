from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.audit import audit_logger
from openhealthkit.auth import SystemPermission, require_permission
from openhealthkit.database import get_async_db
from openhealthkit.models.health_record import HealthRecord, Observation
from openhealthkit.models.user import User
from openhealthkit.schemas.health_record import (
    HealthRecordCreate,
    HealthRecordRead,
    HealthRecordUpdate,
)

router = APIRouter(prefix="/records", tags=["Health Records"])


@router.get("", response_model=list[HealthRecordRead])
async def list_health_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    community_id: str | None = None,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.RECORDS_READ)),
):
    stmt = select(HealthRecord)
    if not include_deleted:
        stmt = stmt.where(HealthRecord.is_deleted == False)
    if community_id:
        stmt = stmt.where(HealthRecord.community_id == community_id)

    stmt = stmt.order_by(HealthRecord.created_at.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=HealthRecordRead, status_code=status.HTTP_201_CREATED)
async def create_health_record(
    req: HealthRecordCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.RECORDS_WRITE)),
):
    record = HealthRecord(
        id=req.id,  # allow optional client-provided UUID for sync
        patient_identifier=req.patient_identifier,
        age_years=req.age_years,
        gender=req.gender,
        community_id=req.community_id,
        metadata_json=req.metadata_json,
    )

    if req.observations:
        for obs_req in req.observations:
            obs = Observation(
                observation_type=obs_req.observation_type,
                value_number=obs_req.value_number,
                value_text=obs_req.value_text,
                unit=obs_req.unit,
                metadata_json=obs_req.metadata_json,
            )
            record.observations.append(obs)

    db.add(record)
    await db.commit()

    from sqlalchemy.orm import selectinload

    reload_stmt = (
        select(HealthRecord)
        .where(HealthRecord.id == record.id)
        .options(selectinload(HealthRecord.observations))
    )
    reloaded_record = (await db.execute(reload_stmt)).scalars().first()

    # Evaluate alerts if observations included
    if reloaded_record and reloaded_record.observations:
        from openhealthkit.alerts import alert_engine

        for obs in reloaded_record.observations:
            await alert_engine.evaluate_observation(db, obs)
        await db.commit()


    await audit_logger.log_action(
        db,
        action="CREATE_HEALTH_RECORD",
        resource_type="health_record",
        resource_id=record.id,
        user_id=current_user.id,
    )
    return record


@router.get("/{record_id}", response_model=HealthRecordRead)
async def get_health_record(
    record_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.RECORDS_READ)),
):
    stmt = select(HealthRecord).where(
        HealthRecord.id == record_id, HealthRecord.is_deleted == False
    )
    res = await db.execute(stmt)
    record = res.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")
    return record


@router.put("/{record_id}", response_model=HealthRecordRead)
async def update_health_record(
    record_id: str,
    req: HealthRecordUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.RECORDS_WRITE)),
):
    stmt = select(HealthRecord).where(
        HealthRecord.id == record_id, HealthRecord.is_deleted == False
    )
    res = await db.execute(stmt)
    record = res.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")

    if req.patient_identifier is not None:
        record.patient_identifier = req.patient_identifier
    if req.age_years is not None:
        record.age_years = req.age_years
    if req.gender is not None:
        record.gender = req.gender
    if req.community_id is not None:
        record.community_id = req.community_id

    await db.commit()
    await db.refresh(record)

    await audit_logger.log_action(
        db,
        action="UPDATE_HEALTH_RECORD",
        resource_type="health_record",
        resource_id=record.id,
        user_id=current_user.id,
    )
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_record(
    record_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.RECORDS_DELETE)),
):
    stmt = select(HealthRecord).where(
        HealthRecord.id == record_id, HealthRecord.is_deleted == False
    )
    res = await db.execute(stmt)
    record = res.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")

    record.is_deleted = True
    await db.commit()

    await audit_logger.log_action(
        db,
        action="SOFT_DELETE_HEALTH_RECORD",
        resource_type="health_record",
        resource_id=record.id,
        user_id=current_user.id,
    )
