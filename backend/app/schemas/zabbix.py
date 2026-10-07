from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ZabbixStatusResponse(BaseModel):
    connected: bool
    url: str
    api_version: Optional[str] = None
    authenticated: bool
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None

class ZabbixHostDTO(BaseModel):
    hostid: str
    host: str
    name: str
    status: str  # 0 = monitored, 1 = unmonitored
    available: str  # 1 = available, 2 = unavailable, 0 = unknown
    error: Optional[str] = None
    ip: Optional[str] = None

class ZabbixProblemDTO(BaseModel):
    eventid: str
    objectid: str  # trigger id
    name: str
    severity: str  # 0: Not classified, 1: Info, 2: Warning, 3: Average, 4: High, 5: Disaster
    clock: int
    acknowledged: str
    r_eventid: Optional[str] = None
    r_clock: Optional[int] = None
