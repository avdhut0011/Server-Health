import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import generate_uuid, utc_now

class ServerGroup(Base):
    __tablename__ = "server_groups"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    environment = Column(String(50), default="Production")
    created_at = Column(DateTime, default=utc_now)
    
    servers = relationship("Server", back_populates="group")

class Server(Base):
    __tablename__ = "servers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("server_groups.id"), nullable=True)
    hostname = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False, index=True)
    os_type = Column(String(50), nullable=False)  # WINDOWS, LINUX
    os_version = Column(String(100), nullable=True)
    environment = Column(String(50), default="Production", index=True)  # Production, Development, Testing, DR
    location = Column(String(100), default="Data Center 1")  # Data Center 1, Data Center 2, Office, Lab
    rack = Column(String(50), nullable=True)
    vendor = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    zabbix_hostid = Column(String(50), unique=True, nullable=True, index=True)
    
    # Status fields
    agent_status = Column(String(50), default="UNKNOWN")  # ONLINE, OFFLINE, UNKNOWN
    overall_health = Column(String(50), default="HEALTHY")  # HEALTHY, WARNING, CRITICAL, DOWN
    consecutive_failures = Column(Integer, default=0)
    is_in_maintenance = Column(Boolean, default=False)
    last_seen_at = Column(DateTime, nullable=True)
    uptime_seconds = Column(Integer, default=0)
    
    # Metrics snapshot
    cpu_utilization = Column(Float, default=0.0)
    memory_utilization = Column(Float, default=0.0)
    disk_utilization = Column(Float, default=0.0)
    network_status = Column(String(50), default="OK")
    
    # Custom Threshold Overrides (Optional JSON)
    custom_thresholds = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    group = relationship("ServerGroup", back_populates="servers")
    components = relationship("Component", back_populates="server", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="server", cascade="all, delete-orphan")
    maintenance_windows = relationship("MaintenanceWindow", back_populates="server", cascade="all, delete-orphan")
