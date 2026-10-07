from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class NotificationChannelBase(BaseModel):
    name: str
    channel_type: str = "EMAIL"
    config: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = True
    is_enabled: bool = True

class NotificationChannelCreate(NotificationChannelBase):
    pass

class NotificationChannelResponse(NotificationChannelBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationLogResponse(BaseModel):
    id: str
    alert_id: str
    channel_id: Optional[str] = None
    channel_type: str
    recipient: str
    subject: str
    body_snippet: Optional[str] = None
    status: str
    retry_count: int
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SendTestEmailRequest(BaseModel):
    recipient: EmailStr
    subject: Optional[str] = "Test Email from Server Health Monitoring"
    message: Optional[str] = "This is a test notification confirming generic SMTP configuration is operating properly."
