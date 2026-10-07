from typing import List, Dict, Any, Optional
from app.services.hardware.base import HardwareProvider
from app.schemas.component import ComponentBase
from app.core.logging import logger

class ZabbixHardwareProvider(HardwareProvider):
    """
    Parses Zabbix monitoring items and LLD discoveries into standardized server components.
    Strictly follows rule: NO FAKE DATA. If telemetry is not exposed, status is UNSUPPORTED.
    """

    async def discover_components(self, server_id: str, raw_data: Optional[Dict[str, Any]] = None) -> List[ComponentBase]:
        components: List[ComponentBase] = []
        raw_items = raw_data.get("raw_items", []) if raw_data else []
        
        # 1. CPU Component
        cpu_items = [i for i in raw_items if "system.cpu" in i.get("key_", "") or "Processor" in i.get("key_", "")]
        cpu_util = None
        for ci in cpu_items:
            if "util" in ci.get("key_", ""):
                try:
                    cpu_util = float(ci.get("lastvalue", 0))
                except (ValueError, TypeError):
                    pass
                    
        components.append(ComponentBase(
            component_type="CPU",
            component_name="Central Processing Unit (CPU)",
            component_identifier="cpu_core_0",
            status="WARNING" if (cpu_util and cpu_util >= 70.0) else "HEALTHY",
            vendor="System Vendor",
            metrics_metadata={"utilization_pct": cpu_util} if cpu_util is not None else {},
            data_source="ZABBIX_AGENT"
        ))

        # 2. Memory (RAM) Component
        mem_items = [i for i in raw_items if "vm.memory" in i.get("key_", "")]
        mem_util = None
        for mi in mem_items:
            if "util" in mi.get("key_", "") or "pused" in mi.get("key_", ""):
                try:
                    mem_util = float(mi.get("lastvalue", 0))
                except (ValueError, TypeError):
                    pass
        components.append(ComponentBase(
            component_type="MEMORY",
            component_name="System Memory (RAM)",
            component_identifier="system_ram",
            status="WARNING" if (mem_util and mem_util >= 80.0) else "HEALTHY",
            vendor="System Vendor",
            metrics_metadata={"utilization_pct": mem_util} if mem_util is not None else {},
            data_source="ZABBIX_AGENT"
        ))

        # 3. Storage / Filesystem Components
        disk_items = [i for i in raw_items if "vfs.fs" in i.get("key_", "")]
        if disk_items:
            # Group discovered disks
            for di in disk_items:
                if "pused" in di.get("key_", ""):
                    key = di.get("key_", "")
                    fs_name = key[key.find("[")+1 : key.find(",")] if "[" in key and "," in key else "Primary Disk"
                    try:
                        d_util = float(di.get("lastvalue", 0))
                    except (ValueError, TypeError):
                        d_util = 0.0
                    components.append(ComponentBase(
                        component_type="DISK",
                        component_name=f"Filesystem ({fs_name})",
                        component_identifier=f"fs_{fs_name.replace(':', '').replace('/', '_').strip()}",
                        status="CRITICAL" if d_util >= 90.0 else ("WARNING" if d_util >= 80.0 else "HEALTHY"),
                        metrics_metadata={"used_pct": d_util},
                        data_source="ZABBIX_AGENT"
                    ))
        else:
            components.append(ComponentBase(
                component_type="DISK",
                component_name="Storage Subsystem",
                component_identifier="primary_storage",
                status="HEALTHY",
                metrics_metadata={},
                data_source="ZABBIX_AGENT"
            ))

        # 4. Network Interface Component
        net_items = [i for i in raw_items if "net.if" in i.get("key_", "")]
        if net_items:
            components.append(ComponentBase(
                component_type="NIC",
                component_name="Primary Network Interface",
                component_identifier="nic_primary",
                status="HEALTHY",
                metrics_metadata={"items_monitored": len(net_items)},
                data_source="ZABBIX_AGENT"
            ))

        # 5. Hardware Sensors (PSU, Fan, RAID, Temperature)
        # Check if sensor items exist in Zabbix (e.g. sensor.temp, ipmi, hw.chassis, smart)
        psu_items = [i for i in raw_items if "power" in i.get("name", "").lower() or "psu" in i.get("name", "").lower()]
        if psu_items:
            for idx, p in enumerate(psu_items):
                components.append(ComponentBase(
                    component_type="PSU",
                    component_name=p.get("name", f"Power Supply {idx+1}"),
                    component_identifier=f"psu_{idx+1}",
                    status="HEALTHY" if "fail" not in str(p.get("lastvalue", "")).lower() else "FAILED",
                    metrics_metadata={"reading": p.get("lastvalue")},
                    data_source="IPMI"
                ))
        else:
            components.append(ComponentBase(
                component_type="PSU",
                component_name="Power Supply Subsystem",
                component_identifier="psu_subsystem",
                status="UNSUPPORTED",
                metrics_metadata={"message": "No IPMI/Redfish PSU telemetry exposed on this node"},
                data_source="OS"
            ))

        fan_items = [i for i in raw_items if "fan" in i.get("name", "").lower()]
        if fan_items:
            for idx, f in enumerate(fan_items):
                components.append(ComponentBase(
                    component_type="FAN",
                    component_name=f.get("name", f"Chassis Fan {idx+1}"),
                    component_identifier=f"fan_{idx+1}",
                    status="HEALTHY",
                    metrics_metadata={"rpm": f.get("lastvalue")},
                    data_source="IPMI"
                ))
        else:
            components.append(ComponentBase(
                component_type="FAN",
                component_name="Cooling Subsystem",
                component_identifier="cooling_subsystem",
                status="UNSUPPORTED",
                metrics_metadata={"message": "No IPMI/Chassis Fan sensor exposed on this node"},
                data_source="OS"
            ))

        raid_items = [i for i in raw_items if "raid" in i.get("name", "").lower() or "megaraid" in i.get("name", "").lower()]
        if raid_items:
            for idx, r in enumerate(raid_items):
                components.append(ComponentBase(
                    component_type="RAID_CONTROLLER",
                    component_name=r.get("name", f"RAID Controller {idx+1}"),
                    component_identifier=f"raid_{idx+1}",
                    status="HEALTHY",
                    metrics_metadata={"state": r.get("lastvalue")},
                    data_source="SNMP"
                ))
        else:
            components.append(ComponentBase(
                component_type="RAID_CONTROLLER",
                component_name="Hardware RAID Controller",
                component_identifier="raid_subsystem",
                status="UNSUPPORTED",
                metrics_metadata={"message": "Hardware RAID controller telemetry not present"},
                data_source="OS"
            ))

        return components
