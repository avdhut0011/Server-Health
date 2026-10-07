import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import generate_uuid, utc_now

class Component(Base):
    __tablename__ = "components"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    server_id = Column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Component Categories: CPU, MEMORY, DISK, RAID_CONTROLLER, PHYSICAL_DISK, PSU, FAN, TEMP_SENSOR, NIC
    component_type = Column(String(50), nullable=False, index=True)
    component_name = Column(String(150), nullable=False)
    component_identifier = Column(String(100), nullable=False)
    
    # Status: HEALTHY, WARNING, CRITICAL, FAILED, NOT_PRESENT, UNSUPPORTED
    status = Column(String(50), default="HEALTHY")
    
    vendor = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    
    # Dynamic telemetry metrics payload (e.g. {"temp_c": 45.2, "rpm": 2400, "voltage": 12.1})
    metrics_metadata = Column(JSON, default=dict)
    
    # Source: ZABBIX_AGENT, IPMI, SNMP, REDFISH, OS
    data_source = Column(String(50), default="ZABBIX_AGENT")
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    server = relationship("Server", back_populates="components")
    alerts = relationship("Alert", back_populates="component")
