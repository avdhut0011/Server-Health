from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.notification import NotificationChannel, NotificationLog
from app.models.audit import AuditLog
from app.schemas.notification import (
    NotificationChannelCreate,
    NotificationChannelResponse,
    NotificationLogResponse,
    SendTestEmailRequest
)
from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.services.notifications.smtp_service import SMTPService

router = APIRouter(prefix="/notifications", tags=["Notifications & SMTP Configuration"])

@router.get("/logs", response_model=List[NotificationLogResponse])
async def list_notification_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(NotificationLog).order_by(desc(NotificationLog.created_at)).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/channels", response_model=List[NotificationChannelResponse])
async def list_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(NotificationChannel)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/channels", response_model=NotificationChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_in: NotificationChannelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    new_channel = NotificationChannel(
        name=channel_in.name,
        channel_type=channel_in.channel_type,
        config=channel_in.config,
        is_default=channel_in.is_default,
        is_enabled=channel_in.is_enabled
    )
    db.add(new_channel)
    await db.commit()
    await db.refresh(new_channel)
    return new_channel

@router.post("/send-test-email")
async def send_test_email(
    req: SendTestEmailRequest,
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"]))
):
    success, error = await SMTPService.send_email(
        recipient=req.recipient,
        subject=req.subject,
        plain_content=req.message,
        html_content=f"<p>{req.message}</p>"
    )
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {error}")
    return {"status": "success", "message": f"Test email sent successfully to {req.recipient}"}
