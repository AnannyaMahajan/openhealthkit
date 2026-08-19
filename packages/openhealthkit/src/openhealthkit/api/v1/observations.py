from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.alerts import alert_engine
from openhealthkit.auth import SystemPermission, require_permission
from openhealthkit.database import get_async_db
from openhealthkit.models.health_record import HealthRecord, Observation
from openhealthkit.models.user import User
from openhealthkit.schemas.health_record import ObservationCreate, ObservationRead

router = APIRouter(prefix="/observations", tags=["Observations"])


@router.get("", response_model=list[ObservationRead])
async def list_observations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    observation_type: str | None = None,
    health_record_id: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.OBSERVATIONS_READ)),
):
    stmt = select(Observation)
    if observation_type:
        stmt = stmt.where(Observation.observation_type == observation_type)
    if health_record_id:
        stmt = stmt.where(Observation.health_record_id == health_record_id)

    stmt = stmt.order_by(Observation.observed_at.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=ObservationRead, status_code=status.HTTP_201_CREATED)
async def create_observation(
    req: ObservationCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.OBSERVATIONS_WRITE)),
):
    if not req.health_record_id:
        raise HTTPException(status_code=400, detail="health_record_id is required")

    # Verify health record exists
    hr_stmt = select(HealthRecord).where(
        HealthRecord.id == req.health_record_id, HealthRecord.is_deleted == False
    )
    hr_res = await db.execute(hr_stmt)
    if not hr_res.scalars().first():
        raise HTTPException(status_code=404, detail="Parent health record not found")

    obs = Observation(
        health_record_id=req.health_record_id,
        observation_type=req.observation_type,
        value_number=req.value_number,
        value_text=req.value_text,
        unit=req.unit,
        metadata_json=req.metadata_json,
    )
    db.add(obs)
    await db.commit()
    await db.refresh(obs)

    # Evaluate rules against alert engine
    await alert_engine.evaluate_observation(db, obs)
    await db.commit()

    return obs
