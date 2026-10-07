import asyncio
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Optional, Dict, Any, List, Tuple
import aiosmtplib
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import notification_logger
from app.models.alert import Alert
from app.models.server import Server
from app.models.notification import NotificationLog, NotificationChannel

class SMTPService:
    @staticmethod
    def render_problem_email(
        server_name: str,
        component_name: str,
        metric_name: str,
        current_value: str,
        threshold: str,
        severity: str,
        detected_at: str
    ) -> Dict[str, str]:
        subject = f"[{severity.upper()}] {server_name} - {metric_name.upper()} Threshold Exceeded"
        
        plain_text = f"""====================================================
SERVER HEALTH ALERT: [{severity.upper()}]
====================================================

Server:        {server_name}
Component:     {component_name}
Metric:        {metric_name}
Current Value: {current_value}
Threshold:     {threshold}
Severity:      {severity.upper()}
Detected At:   {detected_at}

====================================================
This is an automated alert from Server Health Monitoring.
"""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 8px; border-left: 6px solid {'#ef4444' if severity.upper() in ['CRITICAL', 'DOWN'] else '#f59e0b'}; padding: 24px;">
                <h2 style="margin-top: 0; color: {'#ef4444' if severity.upper() in ['CRITICAL', 'DOWN'] else '#f59e0b'};">
                    [{severity.upper()}] {server_name} Alert
                </h2>
                <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Server:</td><td style="font-weight: bold; color: #f8fafc;">{server_name}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Component:</td><td style="color: #f8fafc;">{component_name}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Metric:</td><td style="color: #f8fafc;">{metric_name}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Current Value:</td><td style="font-weight: bold; color: {'#ef4444' if severity.upper() in ['CRITICAL', 'DOWN'] else '#f59e0b'};">{current_value}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Threshold:</td><td style="color: #f8fafc;">{threshold}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Severity:</td><td style="font-weight: bold; color: {'#ef4444' if severity.upper() in ['CRITICAL', 'DOWN'] else '#f59e0b'};">{severity.upper()}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Detected At:</td><td style="color: #f8fafc;">{detected_at}</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        return {"subject": subject, "plain": plain_text, "html": html_content}

    @staticmethod
    def render_recovery_email(
        server_name: str,
        problem_title: str,
        previous_severity: str,
        start_time: str,
        recovery_time: str,
        duration: str,
        current_value: str
    ) -> Dict[str, str]:
        subject = f"[RECOVERED] {server_name} - {problem_title}"
        
        plain_text = f"""====================================================
SERVER HEALTH RECOVERY: [RECOVERED]
====================================================

Server:            {server_name}
Problem:           {problem_title}
Previous Severity: {previous_severity.upper()}
Problem Started:   {start_time}
Recovered At:      {recovery_time}
Duration:          {duration}
Current Value:     {current_value}

====================================================
Server has returned to healthy state.
"""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 8px; border-left: 6px solid #22c55e; padding: 24px;">
                <h2 style="margin-top: 0; color: #22c55e;">
                    [RECOVERED] {server_name}
                </h2>
                <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Server:</td><td style="font-weight: bold; color: #f8fafc;">{server_name}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Problem:</td><td style="color: #f8fafc;">{problem_title}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Previous Severity:</td><td style="color: #f8fafc;">{previous_severity.upper()}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Problem Started:</td><td style="color: #f8fafc;">{start_time}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Recovered At:</td><td style="color: #f8fafc;">{recovery_time}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Duration:</td><td style="font-weight: bold; color: #22c55e;">{duration}</td></tr>
                    <tr><td style="padding: 8px 0; color: #94a3b8;">Current Value:</td><td style="color: #f8fafc;">{current_value}</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        return {"subject": subject, "plain": plain_text, "html": html_content}

    @classmethod
    async def send_email(
        cls,
        recipient: str,
        subject: str,
        plain_content: str,
        html_content: Optional[str] = None,
        smtp_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Sends an email using generic SMTP settings. Returns (success: bool, error_message: str)
        """
        cfg = smtp_config or {}
        host = cfg.get("host", settings.SMTP_HOST)
        port = int(cfg.get("port", settings.SMTP_PORT))
        username = cfg.get("username", settings.SMTP_USERNAME)
        password = cfg.get("password", settings.SMTP_PASSWORD)
        use_tls = cfg.get("tls", settings.SMTP_TLS)
        use_ssl = cfg.get("ssl", settings.SMTP_SSL)
        sender = cfg.get("sender", settings.SMTP_SENDER)

        message = EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(plain_content)
        if html_content:
            message.add_alternative(html_content, subtype="html")

        try:
            notification_logger.info(f"Connecting to SMTP {host}:{port} to send email to {recipient}...")
            await aiosmtplib.send(
                message,
                hostname=host,
                port=port,
                username=username,
                password=password,
                use_tls=use_ssl,  # Implicit SSL on e.g. 465
                start_tls=use_tls and not use_ssl,  # Explicit STARTTLS on e.g. 587
                timeout=10
            )
            notification_logger.info(f"Email successfully delivered to {recipient} - Subject: '{subject}'")
            return (True, None)
        except Exception as exc:
            err = f"SMTP Error sending to {recipient}: {str(exc)}"
            notification_logger.error(err)
            return (False, err)

    @classmethod
    async def dispatch_alert_notification(
        cls,
        db: AsyncSession,
        alert: Alert,
        server: Server,
        component_name: Optional[str] = None,
        recipient: Optional[str] = None
    ) -> NotificationLog:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        to_email = recipient or settings.SMTP_SENDER
        
        rendered = cls.render_problem_email(
            server_name=server.display_name or server.hostname,
            component_name=component_name or "System Subsystem",
            metric_name=alert.metric_name or "Metric Breach",
            current_value=str(alert.trigger_value),
            threshold=str(alert.threshold_value),
            severity=alert.severity,
            detected_at=now_str
        )
        
        # Create pending log entry
        log_entry = NotificationLog(
            alert_id=alert.id,
            channel_type="EMAIL",
            recipient=to_email,
            subject=rendered["subject"],
            body_snippet=rendered["plain"][:500],
            status="PENDING",
            retry_count=0
        )
        db.add(log_entry)
        await db.flush()
        
        # Attempt delivery
        success, error_msg = await cls.send_email(
            recipient=to_email,
            subject=rendered["subject"],
            plain_content=rendered["plain"],
            html_content=rendered["html"]
        )
        
        if success:
            log_entry.status = "SENT"
            log_entry.sent_at = datetime.now(timezone.utc)
            alert.notification_count += 1
            alert.last_notified_at = datetime.now(timezone.utc)
        else:
            log_entry.status = "FAILED"
            log_entry.error_message = error_msg
            log_entry.retry_count = 1
            
        return log_entry

    @classmethod
    async def dispatch_recovery_notification(
        cls,
        db: AsyncSession,
        alert: Alert,
        server: Server,
        current_value: str,
        recipient: Optional[str] = None
    ) -> NotificationLog:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        started_str = alert.started_at.strftime("%Y-%m-%d %H:%M:%S UTC") if alert.started_at else "Unknown"
        duration_min = alert.duration_seconds // 60
        duration_sec = alert.duration_seconds % 60
        duration_str = f"{duration_min} minutes {duration_sec} seconds" if duration_min > 0 else f"{duration_sec} seconds"
        to_email = recipient or settings.SMTP_SENDER

        rendered = cls.render_recovery_email(
            server_name=server.display_name or server.hostname,
            problem_title=alert.problem_title,
            previous_severity=alert.severity,
            start_time=started_str,
            recovery_time=now_str,
            duration=duration_str,
            current_value=str(current_value)
        )

        log_entry = NotificationLog(
            alert_id=alert.id,
            channel_type="EMAIL",
            recipient=to_email,
            subject=rendered["subject"],
            body_snippet=rendered["plain"][:500],
            status="PENDING",
            retry_count=0
        )
        db.add(log_entry)
        await db.flush()

        success, error_msg = await cls.send_email(
            recipient=to_email,
            subject=rendered["subject"],
            plain_content=rendered["plain"],
            html_content=rendered["html"]
        )

        if success:
            log_entry.status = "SENT"
            log_entry.sent_at = datetime.now(timezone.utc)
        else:
            log_entry.status = "FAILED"
            log_entry.error_message = error_msg
            log_entry.retry_count = 1

        return log_entry
