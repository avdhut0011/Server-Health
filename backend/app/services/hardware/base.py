from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.component import ComponentBase

class HardwareProvider(ABC):
    """
    Abstract HardwareProvider interface for extracting component-level hardware telemetry.
    Subclasses implement vendor or protocol-specific extraction (Zabbix, IPMI, SNMP, Redfish).
    """

    @abstractmethod
    async def discover_components(self, server_id: str, raw_data: Optional[Dict[str, Any]] = None) -> List[ComponentBase]:
        """
        Discovers and normalizes hardware and OS subsystems.
        """
        pass
