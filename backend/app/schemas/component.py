from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ComponentBase(BaseModel):
    component_type: str = Field(..., description="CPU, MEMORY, DISK, RAID_CONTROLLER, PHYSICAL_DISK, PSU, FAN, TEMP_SENSOR, NIC")
    component_name: str
    component_identifier: str
    status: str = Field("HEALTHY", description="HEALTHY, WARNING, CRITICAL, FAILED, NOT_PRESENT, UNSUPPORTED")
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    metrics_metadata: Dict[str, Any] = Field(default_factory=dict)
    data_source: str = Field("ZABBIX_AGENT", description="ZABBIX_AGENT, IPMI, SNMP, REDFISH, OS")

class ComponentCreate(ComponentBase):
    pass

class ComponentUpdate(BaseModel):
    status: Optional[str] = None
    metrics_metadata: Optional[Dict[str, Any]] = None
    vendor: Optional[str] = None
    model: Optional[str] = None

class ComponentResponse(ComponentBase):
    id: str
    server_id: str
    updated_at: datetime

    class Config:
        from_attributes = True
