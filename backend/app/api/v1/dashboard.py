from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.server import Server
from app.models.alert import Alert
from app.schemas.dashboard import DashboardSummaryResponse, HealthSummary
from app.schemas.server import ServerResponse
from app.schemas.alert import AlertResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard Summary"])

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch all servers
    s_stmt = select(Server).options(selectinload(Server.group))
    s_res = await db.execute(s_stmt)
    servers = list(s_res.scalars().all())
    
    # Calculate health summary
    total = len(servers)
    healthy_cnt = sum(1 for s in servers if s.overall_health == "HEALTHY")
    warning_cnt = sum(1 for s in servers if s.overall_health == "WARNING")
    critical_cnt = sum(1 for s in servers if s.overall_health == "CRITICAL")
    down_cnt = sum(1 for s in servers if s.overall_health == "DOWN")
    maint_cnt = sum(1 for s in servers if s.is_in_maintenance)
    
    # Fetch active alerts
    a_stmt = (
        select(Alert)
        .options(selectinload(Alert.server), selectinload(Alert.history))
        .where(Alert.status.in_(["ACTIVE", "ACKNOWLEDGED"]))
        .order_by(desc(Alert.started_at))
        .limit(20)
    )
    a_res = await db.execute(a_stmt)
    active_alerts = list(a_res.scalars().all())
    
    unack_cnt = sum(1 for a in active_alerts if a.status == "ACTIVE")
    
    formatted_alerts = []
    for a in active_alerts:
        formatted_alerts.append(AlertResponse(
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
        
    return DashboardSummaryResponse(
        health_summary=HealthSummary(
            total_servers=total,
            healthy=healthy_cnt,
            warning=warning_cnt,
            critical=critical_cnt,
            down=down_cnt,
            in_maintenance=maint_cnt
        ),
        active_alerts_count=len(active_alerts),
        unacknowledged_alerts_count=unack_cnt,
        servers=servers,
        active_alerts=formatted_alerts
    )
