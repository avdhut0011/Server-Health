from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.api.deps import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    action: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"]))
):
    stmt = select(AuditLog).order_by(desc(AuditLog.created_at))
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if username:
        stmt = stmt.where(AuditLog.username == username)
    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()
