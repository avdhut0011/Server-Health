import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.models.server import Server
from app.models.component import Component
from app.services.zabbix.service import zabbix_service
from app.services.health.evaluator import HealthEvaluator
from app.services.alerts.state_machine import AlertStateMachine
from app.services.notifications.smtp_service import SMTPService
from app.services.hardware.zabbix_provider import ZabbixHardwareProvider
from app.websocket.manager import ws_manager

hw_provider = ZabbixHardwareProvider()

async def sync_servers_and_evaluate_health():
    """
    Periodic background cycle to pull Zabbix metrics, evaluate health,
    manage alert state machines, dispatch recovery/problem notifications,
    and broadcast real-time telemetry updates.
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch registered servers
            stmt = select(Server)
            res = await db.execute(stmt)
            servers: List[Server] = list(res.scalars().all())
            
            if not servers:
                return

            for server in servers:
                # If server has a linked Zabbix host ID
                if server.zabbix_hostid:
                    try:
                        metrics = await zabbix_service.get_host_latest_metrics(server.zabbix_hostid)
                        
                        # Update server metrics
                        if metrics.get("cpu_utilization") is not None:
                            server.cpu_utilization = metrics["cpu_utilization"]
                        if metrics.get("memory_utilization") is not None:
                            server.memory_utilization = metrics["memory_utilization"]
                        if metrics.get("disk_utilization") is not None:
                            server.disk_utilization = metrics["disk_utilization"]
                        if metrics.get("uptime_seconds") is not None:
                            server.uptime_seconds = metrics["uptime_seconds"]
                            
                        # Check host connectivity
                        if metrics.get("raw_items"):
                            server.agent_status = "ONLINE"
                            server.consecutive_failures = 0
                            server.last_seen_at = datetime.now(timezone.utc)
                        else:
                            server.consecutive_failures += 1
                            if server.consecutive_failures >= settings.CONSECUTIVE_FAILURES_FOR_DOWN:
                                server.agent_status = "OFFLINE"
                                
                    except Exception as e:
                        logger.warning(f"Error reading metrics for server {server.hostname}: {e}")
                        server.consecutive_failures += 1
                        if server.consecutive_failures >= settings.CONSECUTIVE_FAILURES_FOR_DOWN:
                            server.agent_status = "OFFLINE"
                            
                else:
                    # Non-Zabbix mock/unlinked node - keep default status
                    pass

                # 2. Evaluate component discovery & status
                if server.zabbix_hostid and metrics.get("raw_items"):
                    discovered_comps = await hw_provider.discover_components(server.id, metrics)
                    # Upsert components in DB
                    for d_comp in discovered_comps:
                        c_stmt = select(Component).where(
                            Component.server_id == server.id,
                            Component.component_identifier == d_comp.component_identifier
                        )
                        c_res = await db.execute(c_stmt)
                        db_comp = c_res.scalar_one_or_none()
                        
                        if db_comp:
                            db_comp.status = d_comp.status
                            db_comp.metrics_metadata = d_comp.metrics_metadata
                            db_comp.updated_at = datetime.now(timezone.utc)
                        else:
                            new_comp = Component(
                                server_id=server.id,
                                component_type=d_comp.component_type,
                                component_name=d_comp.component_name,
                                component_identifier=d_comp.component_identifier,
                                status=d_comp.status,
                                vendor=d_comp.vendor,
                                metrics_metadata=d_comp.metrics_metadata,
                                data_source=d_comp.data_source
                            )
                            db.add(new_comp)

                # 3. Evaluate Metric Thresholds (CPU, RAM, Disk)
                metric_severities = []
                
                # CPU check
                cpu_sev, cpu_reason = HealthEvaluator.evaluate_metric_threshold(
                    "cpu", server.cpu_utilization, server.custom_thresholds
                )
                metric_severities.append(cpu_sev)
                if cpu_sev in ["WARNING", "CRITICAL"]:
                    alert, is_new, should_notify = await AlertStateMachine.process_problem(
                        db=db,
                        server=server,
                        component_id=None,
                        component_identifier="cpu",
                        metric_name="CPU Utilization",
                        trigger_value=f"{server.cpu_utilization}%",
                        threshold_value=f"{settings.CPU_CRITICAL_THRESHOLD if cpu_sev == 'CRITICAL' else settings.CPU_WARNING_THRESHOLD}%",
                        severity=cpu_sev,
                        problem_title=cpu_reason or "CPU Threshold Exceeded"
                    )
                    if should_notify and alert:
                        await SMTPService.dispatch_alert_notification(db, alert, server, "Central Processor")
                        await ws_manager.broadcast_event("ALERT_CREATED" if is_new else "ALERT_UPDATED", {
                            "alert_id": alert.id,
                            "server_id": server.id,
                            "server_hostname": server.hostname,
                            "severity": alert.severity,
                            "problem_title": alert.problem_title
                        })
                else:
                    # Check recovery for CPU
                    recovered_alert = await AlertStateMachine.process_recovery(
                        db=db,
                        server=server,
                        component_identifier="cpu",
                        metric_name="CPU Utilization",
                        current_value=f"{server.cpu_utilization}%"
                    )
                    if recovered_alert:
                        await SMTPService.dispatch_recovery_notification(
                            db, recovered_alert, server, f"{server.cpu_utilization}%"
                        )
                        await ws_manager.broadcast_event("ALERT_RECOVERED", {
                            "alert_id": recovered_alert.id,
                            "server_id": server.id,
                            "server_hostname": server.hostname,
                            "duration_seconds": recovered_alert.duration_seconds
                        })

                # Memory check
                mem_sev, mem_reason = HealthEvaluator.evaluate_metric_threshold(
                    "memory", server.memory_utilization, server.custom_thresholds
                )
                metric_severities.append(mem_sev)
                if mem_sev in ["WARNING", "CRITICAL"]:
                    alert, is_new, should_notify = await AlertStateMachine.process_problem(
                        db=db,
                        server=server,
                        component_id=None,
                        component_identifier="memory",
                        metric_name="Memory Utilization",
                        trigger_value=f"{server.memory_utilization}%",
                        threshold_value=f"{settings.MEMORY_CRITICAL_THRESHOLD if mem_sev == 'CRITICAL' else settings.MEMORY_WARNING_THRESHOLD}%",
                        severity=mem_sev,
                        problem_title=mem_reason or "Memory Threshold Exceeded"
                    )
                    if should_notify and alert:
                        await SMTPService.dispatch_alert_notification(db, alert, server, "System RAM")
                        await ws_manager.broadcast_event("ALERT_CREATED" if is_new else "ALERT_UPDATED", {
                            "alert_id": alert.id,
                            "server_id": server.id,
                            "server_hostname": server.hostname,
                            "severity": alert.severity,
                            "problem_title": alert.problem_title
                        })
                else:
                    recovered_alert = await AlertStateMachine.process_recovery(
                        db=db,
                        server=server,
                        component_identifier="memory",
                        metric_name="Memory Utilization",
                        current_value=f"{server.memory_utilization}%"
                    )
                    if recovered_alert:
                        await SMTPService.dispatch_recovery_notification(
                            db, recovered_alert, server, f"{server.memory_utilization}%"
                        )
                        await ws_manager.broadcast_event("ALERT_RECOVERED", {
                            "alert_id": recovered_alert.id,
                            "server_id": server.id,
                            "server_hostname": server.hostname,
                            "duration_seconds": recovered_alert.duration_seconds
                        })

                # Disk check
                disk_sev, disk_reason = HealthEvaluator.evaluate_metric_threshold(
                    "disk", server.disk_utilization, server.custom_thresholds
                )
                metric_severities.append(disk_sev)
                if disk_sev in ["WARNING", "CRITICAL"]:
                    alert, is_new, should_notify = await AlertStateMachine.process_problem(
                        db=db,
                        server=server,
                        component_id=None,
                        component_identifier="disk",
                        metric_name="Disk Utilization",
                        trigger_value=f"{server.disk_utilization}%",
                        threshold_value=f"{settings.DISK_CRITICAL_THRESHOLD if disk_sev == 'CRITICAL' else settings.DISK_WARNING_THRESHOLD}%",
                        severity=disk_sev,
                        problem_title=disk_reason or "Disk Space Exhaustion"
                    )
                    if should_notify and alert:
                        await SMTPService.dispatch_alert_notification(db, alert, server, "Primary Storage")
                        await ws_manager.broadcast_event("ALERT_CREATED" if is_new else "ALERT_UPDATED", {
                            "alert_id": alert.id,
                            "server_id": server.id,
                            "server_hostname": server.hostname,
                            "severity": alert.severity,
                            "problem_title": alert.problem_title
                        })
                else:
                    recovered_alert = await AlertStateMachine.process_recovery(
                        db=db,
                        server=server,
                        component_identifier="disk",
                        metric_name="Disk Utilization",
                        current_value=f"{server.disk_utilization}%"
                    )
                    if recovered_alert:
                        await SMTPService.dispatch_recovery_notification(
                            db, recovered_alert, server, f"{server.disk_utilization}%"
                        )
                        await ws_manager.broadcast_event("ALERT_RECOVERED", {
                            "alert_id": recovered_alert.id,
                            "server_id": server.id,
                            "server_hostname": server.hostname,
                            "duration_seconds": recovered_alert.duration_seconds
                        })

                # 4. Check Server DOWN or RECOVERED state
                if server.agent_status == "OFFLINE":
                    alert, is_new, should_notify = await AlertStateMachine.process_problem(
                        db=db,
                        server=server,
                        component_id=None,
                        component_identifier="availability",
                        metric_name="Host Availability",
                        trigger_value="OFFLINE",
                        threshold_value="ONLINE",
                        severity="DOWN",
                        problem_title=f"Server {server.hostname} is Unreachable (Consecutive Failures: {server.consecutive_failures})"
                    )
                    if should_notify and alert:
                        await SMTPService.dispatch_alert_notification(db, alert, server, "Host Node")
                        await ws_manager.broadcast_event("SERVER_DOWN", {
                            "server_id": server.id,
                            "server_hostname": server.hostname,
                            "consecutive_failures": server.consecutive_failures
                        })
                else:
                    # Check recovery from DOWN
                    recovered_alert = await AlertStateMachine.process_recovery(
                        db=db,
                        server=server,
                        component_identifier="availability",
                        metric_name="Host Availability",
                        current_value="ONLINE"
                    )
                    if recovered_alert:
                        await SMTPService.dispatch_recovery_notification(
                            db, recovered_alert, server, "ONLINE"
                        )
                        await ws_manager.broadcast_event("SERVER_RECOVERED", {
                            "server_id": server.id,
                            "server_hostname": server.hostname
                        })

                # 5. Determine Overall Server Health
                comp_dicts = []
                c_q = select(Component).where(Component.server_id == server.id)
                c_all = (await db.execute(c_q)).scalars().all()
                for c in c_all:
                    comp_dicts.append({"status": c.status})

                prev_health = server.overall_health
                server.overall_health = HealthEvaluator.evaluate_overall_server_health(
                    agent_status=server.agent_status,
                    consecutive_failures=server.consecutive_failures,
                    components=comp_dicts,
                    metric_severities=metric_severities
                )
                
                if prev_health != server.overall_health:
                    logger.info(f"Server {server.hostname} health transitioned from {prev_health} to {server.overall_health}")
                    await ws_manager.broadcast_event("SERVER_HEALTH_CHANGED", {
                        "server_id": server.id,
                        "server_hostname": server.hostname,
                        "previous_health": prev_health,
                        "current_health": server.overall_health
                    })

            await db.commit()
            
            # Broadcast global telemetry update
            await ws_manager.broadcast_event("TELEMETRY_SYNCED", {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "server_count": len(servers)
            })

        except Exception as exc:
            logger.error(f"Error in sync_servers_and_evaluate_health cycle: {exc}", exc_info=True)
            await db.rollback()

async def start_background_sync_loop():
    """Starts the continuous background sync worker loop."""
    logger.info("Starting background Zabbix synchronization & Health evaluation loop...")
    while True:
        try:
            await sync_servers_and_evaluate_health()
        except Exception as e:
            logger.error(f"Unexpected error in background sync loop: {e}")
        await asyncio.sleep(settings.ZABBIX_SYNC_INTERVAL_SECONDS)
