import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from openhealthkit.models.audit import AuditLog
from openhealthkit.utils.logger import logger


class AuditLogger:
    """Service for creating security and operational audit logs."""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        details_json = json.dumps(details) if details else None
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=details_json,
            ip_address=ip_address,
        )
        db.add(audit_entry)
        logger.info(f"AUDIT LOG [{action}] resource={resource_type}:{resource_id} user={user_id}")
        return audit_entry


audit_logger = AuditLogger()
