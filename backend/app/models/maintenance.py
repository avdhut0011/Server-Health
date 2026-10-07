import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import generate_uuid, utc_now

class MaintenanceWindow(Base):
    __tablename__ = "maintenance_windows"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    server_id = Column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    
    suppress_alerts = Column(Boolean, default=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    server = relationship("Server", back_populates="maintenance_windows")
