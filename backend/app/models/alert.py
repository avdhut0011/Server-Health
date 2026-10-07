import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import generate_uuid, utc_now

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    server_id = Column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(String(36), ForeignKey("components.id", ondelete="SET NULL"), nullable=True)
    
    # Deduplication key: e.g. "server_id:component_type:component_id:problem_type"
    dedup_key = Column(String(255), unique=True, nullable=False, index=True)
    
    problem_title = Column(String(255), nullable=False)
    metric_name = Column(String(100), nullable=True)
    trigger_value = Column(String(100), nullable=True)
    threshold_value = Column(String(100), nullable=True)
    
    # Severity: INFO, WARNING, CRITICAL, DOWN
    severity = Column(String(50), nullable=False, index=True)
    
    # Status: ACTIVE, ACKNOWLEDGED, RECOVERED, SUPPRESSED
    status = Column(String(50), default="ACTIVE", index=True)
    
    acknowledged_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledge_note = Column(Text, nullable=True)
    
    started_at = Column(DateTime, default=utc_now, index=True)
    recovered_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    notification_count = Column(Integer, default=0)
    last_notified_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    server = relationship("Server", back_populates="alerts")
    component = relationship("Component", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="alert", cascade="all, delete-orphan")

class AlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    alert_id = Column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state = Column(String(50), nullable=True)
    to_state = Column(String(50), nullable=False)
    current_value = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    alert = relationship("Alert", back_populates="history")
