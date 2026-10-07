from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    client_ip: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
