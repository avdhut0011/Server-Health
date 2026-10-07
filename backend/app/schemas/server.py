from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.component import ComponentResponse

class ServerGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    environment: str = "Production"

class ServerGroupCreate(ServerGroupBase):
    pass

class ServerGroupResponse(ServerGroupBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ServerBase(BaseModel):
    hostname: str
    display_name: str
    ip_address: str
    os_type: str = Field(..., description="WINDOWS, LINUX")
    os_version: Optional[str] = None
    environment: str = Field("Production", description="Production, Development, Testing, DR")
    location: str = Field("Data Center 1", description="Data Center 1, Data Center 2, Office, Lab")
    rack: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    zabbix_hostid: Optional[str] = None
    custom_thresholds: Dict[str, Any] = Field(default_factory=dict)

class ServerCreate(ServerBase):
    group_id: Optional[str] = None

class ServerUpdate(BaseModel):
    display_name: Optional[str] = None
    ip_address: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    environment: Optional[str] = None
    location: Optional[str] = None
    rack: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    zabbix_hostid: Optional[str] = None
    group_id: Optional[str] = None
    custom_thresholds: Optional[Dict[str, Any]] = None

class ServerResponse(ServerBase):
    id: str
    group_id: Optional[str] = None
    agent_status: str
    overall_health: str
    consecutive_failures: int
    is_in_maintenance: bool
    last_seen_at: Optional[datetime] = None
    uptime_seconds: int
    cpu_utilization: float
    memory_utilization: float
    disk_utilization: float
    network_status: str
    created_at: datetime
    updated_at: datetime
    group: Optional[ServerGroupResponse] = None

    class Config:
        from_attributes = True

class ServerDetailResponse(ServerResponse):
    components: List[ComponentResponse] = []

    class Config:
        from_attributes = True
