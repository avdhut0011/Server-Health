from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.alert import Alert, AlertHistory
from app.models.server import Server
from app.models.notification import NotificationLog
from app.core.logging import logger, notification_logger

class AlertStateMachine:
    @staticmethod
    def generate_dedup_key(server_id: str, component_identifier: str, metric_or_problem: str) -> str:
        """
        Creates a deterministic unique key: e.g. 'srv-123:cpu:utilization'
        """
        return f"{server_id}:{component_identifier}:{metric_or_problem}".lower()

    @classmethod
    async def process_problem(
        cls,
        db: AsyncSession,
        server: Server,
        component_id: Optional[str],
        component_identifier: str,
        metric_name: str,
        trigger_value: str,
        threshold_value: str,
        severity: str,
        problem_title: str
    ) -> Tuple[Optional[Alert], bool, bool]:
        """
        Processes a detected problem.
        Returns: (Alert object, is_new_alert, should_notify)
        """
        now = datetime.now(timezone.utc)
        dedup_key = cls.generate_dedup_key(server.id, component_identifier or "system", metric_name)
        
        # Check active alerts
        stmt = select(Alert).where(
            and_(
                Alert.dedup_key == dedup_key,
                Alert.status.in_(["ACTIVE", "ACKNOWLEDGED"])
            )
        )
        res = await db.execute(stmt)
        existing_alert = res.scalar_one_or_none()
        
        is_suppressed = server.is_in_maintenance
        
        if existing_alert:
            # Same problem already active
            if existing_alert.severity != severity:
                # Severity changed (Escalation or De-escalation)
                old_sev = existing_alert.severity
                existing_alert.severity = severity
                existing_alert.trigger_value = str(trigger_value)
                existing_alert.threshold_value = str(threshold_value)
                existing_alert.updated_at = now
                
                history = AlertHistory(
                    alert_id=existing_alert.id,
                    from_state=old_sev,
                    to_state=severity,
                    current_value=str(trigger_value),
                    note=f"Severity transitioned from {old_sev} to {severity}"
                )
                db.add(history)
                
                # Should notify on escalation if not suppressed
                should_notify = not is_suppressed
                return (existing_alert, False, should_notify)
            else:
                # Same severity -> update value & timestamp, DO NOT resend notification (deduplicated)
                existing_alert.trigger_value = str(trigger_value)
                existing_alert.updated_at = now
                return (existing_alert, False, False)
        else:
            # New problem detected
            new_alert = Alert(
                server_id=server.id,
                component_id=component_id,
                dedup_key=dedup_key,
                problem_title=problem_title,
                metric_name=metric_name,
                trigger_value=str(trigger_value),
                threshold_value=str(threshold_value),
                severity=severity,
                status="SUPPRESSED" if is_suppressed else "ACTIVE",
                started_at=now,
                updated_at=now,
                notification_count=0
            )
            db.add(new_alert)
            await db.flush()
            
            history = AlertHistory(
                alert_id=new_alert.id,
                from_state="NORMAL",
                to_state=severity,
                current_value=str(trigger_value),
                note=f"Alert triggered with initial severity {severity}" + (" (Suppressed by Maintenance)" if is_suppressed else "")
            )
            db.add(history)
            
            should_notify = not is_suppressed
            return (new_alert, True, should_notify)

    @classmethod
    async def process_recovery(
        cls,
        db: AsyncSession,
        server: Server,
        component_identifier: str,
        metric_name: str,
        current_value: str
    ) -> Optional[Alert]:
        """
        Transitions an active problem to RECOVERED.
        Returns: The recovered Alert object if one was resolved, otherwise None.
        """
        now = datetime.now(timezone.utc)
        dedup_key = cls.generate_dedup_key(server.id, component_identifier or "system", metric_name)
        
        stmt = select(Alert).where(
            and_(
                Alert.dedup_key == dedup_key,
                Alert.status.in_(["ACTIVE", "ACKNOWLEDGED", "SUPPRESSED"])
            )
        )
        res = await db.execute(stmt)
        active_alert = res.scalar_one_or_none()
        
        if active_alert:
            old_status = active_alert.status
            old_severity = active_alert.severity
            
            # Duration calculation in seconds
            # Ensure timezone-aware subtraction
            started = active_alert.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            duration = int((now - started).total_seconds())
            
            active_alert.status = "RECOVERED"
            active_alert.recovered_at = now
            active_alert.duration_seconds = max(0, duration)
            active_alert.updated_at = now
            
            history = AlertHistory(
                alert_id=active_alert.id,
                from_state=old_severity,
                to_state="RECOVERED",
                current_value=str(current_value),
                note=f"Recovered after {duration // 60}m {duration % 60}s. Current value: {current_value}"
            )
            db.add(history)
            
            logger.info(f"Alert {active_alert.id} ({active_alert.problem_title}) transitioned to RECOVERED for {server.hostname}")
            return active_alert
            
        return None
