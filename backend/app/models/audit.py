import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import generate_uuid, utc_now

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(100), nullable=True)
    
    # Action Examples: LOGIN, LOGOUT, SERVER_ADDED, SERVER_MODIFIED, THRESHOLD_MODIFIED, ALERT_ACKNOWLEDGED, MAINTENANCE_CREATED
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    client_ip = Column(String(50), nullable=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=utc_now, index=True)
    
    user = relationship("User", back_populates="audit_logs")
