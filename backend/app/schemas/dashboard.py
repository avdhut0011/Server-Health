from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.server import ServerResponse
from app.schemas.alert import AlertResponse

class HealthSummary(BaseModel):
    total_servers: int = 0
    healthy: int = 0
    warning: int = 0
    critical: int = 0
    down: int = 0
    in_maintenance: int = 0

class DashboardSummaryResponse(BaseModel):
    health_summary: HealthSummary
    active_alerts_count: int
    unacknowledged_alerts_count: int
    servers: List[ServerResponse] = []
    active_alerts: List[AlertResponse] = []

class MetricHistoryPoint(BaseModel):
    timestamp: int
    value: float

class MetricSeries(BaseModel):
    metric_name: str
    unit: str
    data: List[MetricHistoryPoint] = []

class ServerHistoricalMetricsResponse(BaseModel):
    server_id: str
    time_range: str
    series: List[MetricSeries] = []
