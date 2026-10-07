import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import generate_uuid, utc_now

class NotificationChannel(Base):
    __tablename__ = "notification_channels"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    channel_type = Column(String(50), default="EMAIL")  # EMAIL
    
    # JSON configuration for SMTP (host, port, username, password, tls, ssl, sender, default_recipients)
    config = Column(JSON, default=dict)
    
    is_default = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    
    logs = relationship("NotificationLog", back_populates="channel")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    alert_id = Column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(String(36), ForeignKey("notification_channels.id", ondelete="SET NULL"), nullable=True)
    
    channel_type = Column(String(50), default="EMAIL")
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body_snippet = Column(Text, nullable=True)
    
    # Status: PENDING, SENT, FAILED, SUPPRESSED
    status = Column(String(50), default="PENDING", index=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    alert = relationship("Alert", back_populates="notifications")
    channel = relationship("NotificationChannel", back_populates="logs")
