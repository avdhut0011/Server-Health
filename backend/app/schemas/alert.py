from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class AlertHistoryResponse(BaseModel):
    id: str
    from_state: Optional[str] = None
    to_state: str
    current_value: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AlertAcknowledgeRequest(BaseModel):
    note: Optional[str] = Field(None, description="Operational notes for acknowledging this alert")

class AlertResponse(BaseModel):
    id: str
    server_id: str
    component_id: Optional[str] = None
    dedup_key: str
    problem_title: str
    metric_name: Optional[str] = None
    trigger_value: Optional[str] = None
    threshold_value: Optional[str] = None
    severity: str
    status: str
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    acknowledge_note: Optional[str] = None
    started_at: datetime
    recovered_at: Optional[datetime] = None
    duration_seconds: int
    notification_count: int
    last_notified_at: Optional[datetime] = None
    updated_at: datetime
    server_hostname: Optional[str] = None
    server_display_name: Optional[str] = None
    history: List[AlertHistoryResponse] = []

    class Config:
        from_attributes = True
