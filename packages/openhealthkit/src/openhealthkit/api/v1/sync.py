from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.auth import SystemPermission, require_permission
from openhealthkit.database import get_async_db
from openhealthkit.models.sync import SyncRecord, SyncState
from openhealthkit.models.user import User
from openhealthkit.schemas.sync import (
    SyncConflictResolveRequest,
    SyncPullRequest,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
)
from openhealthkit.sync import sync_engine

router = APIRouter(prefix="/sync", tags=["Offline Sync Engine"])


@router.post("/push", response_model=SyncPushResponse)
async def push_offline_changes(
    req: SyncPushRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.SYNC_PUSH)),
):
    response = await sync_engine.process_push(db, req)
    return response


@router.post("/pull", response_model=SyncPullResponse)
async def pull_remote_changes(
    req: SyncPullRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.SYNC_PULL)),
):
    response = await sync_engine.process_pull(db, req)
    return response


@router.post("/resolve", status_code=status.HTTP_200_OK)
async def resolve_sync_conflict(
    req: SyncConflictResolveRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.SYNC_PUSH)),
):
    stmt = select(SyncRecord).where(SyncRecord.id == req.sync_record_id)
    res = await db.execute(stmt)
    record = res.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Sync record not found")

    record.state = SyncState.SYNCED.value
    await db.commit()
    return {
        "status": "resolved",
        "strategy": req.resolution_strategy,
        "record_id": req.sync_record_id,
    }
