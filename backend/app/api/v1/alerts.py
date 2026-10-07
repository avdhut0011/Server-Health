from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.alert import Alert, AlertHistory
from app.models.server import Server
from app.models.audit import AuditLog
from app.schemas.alert import AlertResponse, AlertAcknowledgeRequest
from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/alerts", tags=["Alerts Management"])

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    status_filter: Optional[str] = Query(None, description="ACTIVE, ACKNOWLEDGED, RECOVERED, SUPPRESSED"),
    severity: Optional[str] = Query(None, description="INFO, WARNING, CRITICAL, DOWN"),
    server_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Alert).options(selectinload(Alert.server), selectinload(Alert.history)).order_by(desc(Alert.started_at))
    
    if status_filter:
        stmt = stmt.where(Alert.status == status_filter.upper())
    if severity:
        stmt = stmt.where(Alert.severity == severity.upper())
    if server_id:
        stmt = stmt.where(Alert.server_id == server_id)
        
    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    alerts = res.scalars().all()
    
    out = []
    for a in alerts:
        out.append(AlertResponse(
            id=a.id,
            server_id=a.server_id,
            component_id=a.component_id,
            dedup_key=a.dedup_key,
            problem_title=a.problem_title,
            metric_name=a.metric_name,
            trigger_value=a.trigger_value,
            threshold_value=a.threshold_value,
            severity=a.severity,
            status=a.status,
            acknowledged_by=a.acknowledged_by,
            acknowledged_at=a.acknowledged_at,
            acknowledge_note=a.acknowledge_note,
            started_at=a.started_at,
            recovered_at=a.recovered_at,
            duration_seconds=a.duration_seconds,
            notification_count=a.notification_count,
            last_notified_at=a.last_notified_at,
            updated_at=a.updated_at,
            server_hostname=a.server.hostname if a.server else None,
            server_display_name=a.server.display_name if a.server else None,
            history=a.history
        ))
    return out

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str,
    ack_in: AlertAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"]))
):
    stmt = select(Alert).options(selectinload(Alert.server), selectinload(Alert.history)).where(Alert.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    now = datetime.now(timezone.utc)
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_by = current_user.username
    alert.acknowledged_at = now
    alert.acknowledge_note = ack_in.note
    alert.updated_at = now
    
    history = AlertHistory(
        alert_id=alert.id,
        from_state="ACTIVE",
        to_state="ACKNOWLEDGED",
        current_value=alert.trigger_value,
        note=f"Acknowledged by {current_user.username}: {ack_in.note or 'No notes'}"
    )
    db.add(history)
    
    audit_entry = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="ALERT_ACKNOWLEDGED",
        resource_type="ALERT",
        resource_id=alert.id,
        new_values={"note": ack_in.note}
    )
    db.add(audit_entry)
    await db.commit()
    
    await ws_manager.broadcast_event("ALERT_ACKNOWLEDGED", {
        "alert_id": alert.id,
        "acknowledged_by": current_user.username
    })
    
    return AlertResponse(
        id=alert.id,
        server_id=alert.server_id,
        component_id=alert.component_id,
        dedup_key=alert.dedup_key,
        problem_title=alert.problem_title,
        metric_name=alert.metric_name,
        trigger_value=alert.trigger_value,
        threshold_value=alert.threshold_value,
        severity=alert.severity,
        status=alert.status,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        acknowledge_note=alert.acknowledge_note,
        started_at=alert.started_at,
        recovered_at=alert.recovered_at,
        duration_seconds=alert.duration_seconds,
        notification_count=alert.notification_count,
        last_notified_at=alert.last_notified_at,
        updated_at=alert.updated_at,
        server_hostname=alert.server.hostname if alert.server else None,
        server_display_name=alert.server.display_name if alert.server else None,
        history=alert.history
    )
