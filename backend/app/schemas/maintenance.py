from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MaintenanceWindowBase(BaseModel):
    server_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    suppress_alerts: bool = True

class MaintenanceWindowCreate(MaintenanceWindowBase):
    pass

class MaintenanceWindowResponse(MaintenanceWindowBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    server_hostname: Optional[str] = None

    class Config:
        from_attributes = True
