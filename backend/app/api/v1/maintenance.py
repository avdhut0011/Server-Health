from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.maintenance import MaintenanceWindow
from app.models.server import Server
from app.models.audit import AuditLog
from app.schemas.maintenance import MaintenanceWindowCreate, MaintenanceWindowResponse
from app.api.deps import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/maintenance", tags=["Maintenance Windows"])

@router.get("", response_model=List[MaintenanceWindowResponse])
async def list_maintenance_windows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(MaintenanceWindow).options(selectinload(MaintenanceWindow.server))
    res = await db.execute(stmt)
    windows = res.scalars().all()
    
    out = []
    for w in windows:
        out.append(MaintenanceWindowResponse(
            id=w.id,
            server_id=w.server_id,
            title=w.title,
            description=w.description,
            start_time=w.start_time,
            end_time=w.end_time,
            suppress_alerts=w.suppress_alerts,
            created_by=w.created_by,
            created_at=w.created_at,
            server_hostname=w.server.hostname if w.server else None
        ))
    return out

@router.post("", response_model=MaintenanceWindowResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_window(
    maint_in: MaintenanceWindowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"]))
):
    # Verify server exists
    s_stmt = select(Server).where(Server.id == maint_in.server_id)
    s_res = await db.execute(s_stmt)
    server = s_res.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
        
    now = datetime.now(timezone.utc)
    new_window = MaintenanceWindow(
        server_id=maint_in.server_id,
        title=maint_in.title,
        description=maint_in.description,
        start_time=maint_in.start_time,
        end_time=maint_in.end_time,
        suppress_alerts=maint_in.suppress_alerts,
        created_by=current_user.username
    )
    db.add(new_window)
    
    # Check if active right now
    if new_window.start_time <= now <= new_window.end_time:
        server.is_in_maintenance = True
        
    audit_entry = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="MAINTENANCE_CREATED",
        resource_type="MAINTENANCE",
        resource_id=new_window.id,
        new_values=maint_in.model_dump(mode="json")
    )
    db.add(audit_entry)
    await db.commit()
    await db.refresh(new_window)
    
    return MaintenanceWindowResponse(
        id=new_window.id,
        server_id=new_window.server_id,
        title=new_window.title,
        description=new_window.description,
        start_time=new_window.start_time,
        end_time=new_window.end_time,
        suppress_alerts=new_window.suppress_alerts,
        created_by=new_window.created_by,
        created_at=new_window.created_at,
        server_hostname=server.hostname
    )

@router.delete("/{window_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance_window(
    window_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"]))
):
    stmt = select(MaintenanceWindow).where(MaintenanceWindow.id == window_id)
    res = await db.execute(stmt)
    window = res.scalar_one_or_none()
    if not window:
        raise HTTPException(status_code=404, detail="Maintenance window not found")
        
    # Reset server is_in_maintenance if this was the only active window
    s_stmt = select(Server).where(Server.id == window.server_id)
    server = (await db.execute(s_stmt)).scalar_one_or_none()
    if server:
        server.is_in_maintenance = False
        
    await db.delete(window)
    audit_entry = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="MAINTENANCE_DELETED",
        resource_type="MAINTENANCE",
        resource_id=window_id
    )
    db.add(audit_entry)
    await db.commit()
