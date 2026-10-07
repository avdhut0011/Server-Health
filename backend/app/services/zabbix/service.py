import time
from typing import Optional, List, Dict, Any
from app.services.zabbix.client import ZabbixClient
from app.schemas.zabbix import ZabbixStatusResponse, ZabbixHostDTO, ZabbixProblemDTO
from app.core.logging import zabbix_logger

class ZabbixService:
    def __init__(self, client: Optional[ZabbixClient] = None):
        self.client = client or ZabbixClient()

    async def check_connection(self) -> ZabbixStatusResponse:
        start_t = time.perf_counter()
        try:
            version = await self.client.get_api_version()
            authed = await self.client.authenticate()
            latency = (time.perf_counter() - start_t) * 1000
            return ZabbixStatusResponse(
                connected=True,
                url=self.client.url,
                api_version=version,
                authenticated=authed,
                latency_ms=round(latency, 2),
                error_message=None
            )
        except Exception as e:
            latency = (time.perf_counter() - start_t) * 1000
            return ZabbixStatusResponse(
                connected=False,
                url=self.client.url,
                api_version=None,
                authenticated=False,
                latency_ms=round(latency, 2),
                error_message=str(e)
            )

    async def get_all_monitored_hosts(self) -> List[ZabbixHostDTO]:
        try:
            raw_hosts = await self.client.get_hosts()
            hosts = []
            for h in raw_hosts:
                ip = None
                interfaces = h.get("interfaces", [])
                if interfaces:
                    ip = interfaces[0].get("ip")
                hosts.append(ZabbixHostDTO(
                    hostid=h.get("hostid"),
                    host=h.get("host"),
                    name=h.get("name"),
                    status=str(h.get("status")),
                    available=str(h.get("available")),
                    error=h.get("error"),
                    ip=ip
                ))
            return hosts
        except Exception as e:
            zabbix_logger.error(f"Error fetching Zabbix hosts: {e}")
            return []

    async def get_active_problems(self, hostids: Optional[List[str]] = None) -> List[ZabbixProblemDTO]:
        try:
            raw_probs = await self.client.get_problems(hostids=hostids)
            probs = []
            for p in raw_probs:
                probs.append(ZabbixProblemDTO(
                    eventid=p.get("eventid"),
                    objectid=p.get("objectid"),
                    name=p.get("name"),
                    severity=str(p.get("severity")),
                    clock=int(p.get("clock", 0)),
                    acknowledged=str(p.get("acknowledged", "0")),
                    r_eventid=p.get("r_eventid"),
                    r_clock=int(p.get("r_clock", 0)) if p.get("r_clock") else None
                ))
            return probs
        except Exception as e:
            zabbix_logger.error(f"Error fetching Zabbix problems: {e}")
            return []

    async def get_host_latest_metrics(self, hostid: str) -> Dict[str, Any]:
        """
        Retrieves CPU, Memory, Disk, Uptime, Network metrics from Zabbix items
        """
        try:
            items = await self.client.get_items(hostid)
            metrics = {
                "cpu_utilization": None,
                "memory_utilization": None,
                "disk_utilization": None,
                "uptime_seconds": None,
                "ping_latency_ms": None,
                "packet_loss_pct": None,
                "raw_items": items
            }
            
            for itm in items:
                key = itm.get("key_", "")
                val_str = itm.get("lastvalue")
                try:
                    val_float = float(val_str) if val_str is not None else None
                except ValueError:
                    val_float = None

                # CPU utilization detection
                if "system.cpu.util" in key or "perf_counter" in key and "Processor" in key:
                    if val_float is not None:
                        metrics["cpu_utilization"] = round(val_float, 2)
                        
                # Memory utilization detection
                elif "vm.memory.util" in key or "vm.memory.size[pused]" in key or "vm.memory.size[pavailable]" in key:
                    if val_float is not None:
                        if "pavailable" in key:
                            metrics["memory_utilization"] = round(100.0 - val_float, 2)
                        else:
                            metrics["memory_utilization"] = round(val_float, 2)
                            
                # Disk utilization
                elif "vfs.fs.dependent.size" in key and "pused" in key or "vfs.fs.size" in key and "pused" in key:
                    if val_float is not None:
                        if metrics["disk_utilization"] is None or val_float > metrics["disk_utilization"]:
                            metrics["disk_utilization"] = round(val_float, 2)
                            
                # System uptime
                elif "system.uptime" in key:
                    if val_float is not None:
                        metrics["uptime_seconds"] = int(val_float)
                        
                # Ping & ICMP
                elif "icmppingsec" in key or "net.tcp.service.perf" in key:
                    if val_float is not None:
                        metrics["ping_latency_ms"] = round(val_float * 1000, 2)
                elif "icmppingloss" in key:
                    if val_float is not None:
                        metrics["packet_loss_pct"] = round(val_float, 2)
                        
            return metrics
        except Exception as e:
            zabbix_logger.error(f"Error fetching host metrics for {hostid}: {e}")
            return {}

zabbix_service = ZabbixService()
