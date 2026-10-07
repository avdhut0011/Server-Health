import time
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import zabbix_logger

class ZabbixClient:
    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_token: Optional[str] = None,
        timeout: Optional[int] = None,
        verify_ssl: Optional[bool] = None
    ):
        self.url = url or settings.ZABBIX_URL
        self.username = username or settings.ZABBIX_USERNAME
        self.password = password or settings.ZABBIX_PASSWORD
        self.api_token = api_token or settings.ZABBIX_API_TOKEN
        self.timeout = timeout or settings.ZABBIX_TIMEOUT
        self.verify_ssl = verify_ssl if verify_ssl is not None else settings.ZABBIX_VERIFY_SSL
        
        self.auth_token: Optional[str] = None
        self.req_id = 1
        
        # Circuit Breaker metrics
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.circuit_open = False
        self.circuit_reset_timeout = 30.0  # seconds

    def _is_circuit_open(self) -> bool:
        if self.circuit_open:
            if self.last_failure_time and (time.time() - self.last_failure_time > self.circuit_reset_timeout):
                zabbix_logger.info("Zabbix API Circuit Breaker: Half-Open test attempt")
                return False
            return True
        return False

    def _record_success(self):
        self.failure_count = 0
        self.circuit_open = False

    def _record_failure(self, error_msg: str):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= 5:
            self.circuit_open = True
            zabbix_logger.warning(f"Zabbix API Circuit Breaker: OPENED after {self.failure_count} consecutive failures. Error: {error_msg}")

    async def execute_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if self._is_circuit_open():
            raise RuntimeError("Zabbix API Circuit Breaker is OPEN. Service temporarily unavailable.")
            
        params = params or {}
        self.req_id += 1
        
        payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.req_id
        }
        
        headers = {
            "Content-Type": "application/json-rpc",
            "User-Agent": "ServerHealthMonitor/1.0"
        }
        
        # Zabbix 7.0 / 6.4 API Token or session token
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        elif self.auth_token and method not in ["user.login", "apiinfo.version"]:
            payload["auth"] = self.auth_token
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=self.verify_ssl) as client:
                start_t = time.perf_counter()
                response = await client.post(self.url, json=payload, headers=headers)
                latency = (time.perf_counter() - start_t) * 1000
                
                if response.status_code != 200:
                    err_msg = f"HTTP {response.status_code}: {response.text}"
                    self._record_failure(err_msg)
                    zabbix_logger.error(f"Zabbix RPC HTTP Error [{method}]: {err_msg}")
                    raise RuntimeError(f"Zabbix HTTP error: {err_msg}")
                    
                data = response.json()
                if "error" in data:
                    err_info = data["error"]
                    err_msg = f"{err_info.get('message', 'RPC Error')} - {err_info.get('data', '')}"
                    self._record_failure(err_msg)
                    zabbix_logger.error(f"Zabbix RPC Error [{method}]: {err_msg}")
                    raise RuntimeError(f"Zabbix RPC error: {err_msg}")
                
                self._record_success()
                zabbix_logger.debug(f"Zabbix RPC [{method}] ok in {latency:.1f}ms")
                return data.get("result")
                
        except httpx.RequestError as exc:
            err_msg = f"Connection error: {str(exc)}"
            self._record_failure(err_msg)
            zabbix_logger.error(f"Zabbix Connection Error [{method}]: {err_msg}")
            raise RuntimeError(err_msg)

    async def get_api_version(self) -> str:
        return await self.execute_request("apiinfo.version", {})

    async def authenticate(self) -> bool:
        if self.api_token:
            return True
        try:
            res = await self.execute_request("user.login", {
                "username": self.username,
                "password": self.password
            })
            if res:
                self.auth_token = res
                zabbix_logger.info("Successfully authenticated with Zabbix API via user.login")
                return True
            return False
        except Exception as e:
            zabbix_logger.error(f"Failed to authenticate with Zabbix: {e}")
            return False

    async def get_hosts(self, filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        params = {
            "output": ["hostid", "host", "name", "status", "available", "error", "description", "lastaccess"],
            "selectInterfaces": ["interfaceid", "ip", "dns", "useip", "port", "main", "available", "error"],
            "selectGroups": ["groupid", "name"]
        }
        if filter_params:
            params.update(filter_params)
        return await self.execute_request("host.get", params)

    async def get_problems(self, hostids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        params = {
            "output": "extend",
            "selectAcknowledges": "extend",
            "recent": "true",
            "sortfield": ["eventid"],
            "sortorder": "DESC"
        }
        if hostids:
            params["hostids"] = hostids
        return await self.execute_request("problem.get", params)

    async def get_items(self, hostid: str, search_keys: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        params = {
            "output": ["itemid", "name", "key_", "lastvalue", "lastclock", "units", "value_type", "status", "error"],
            "hostids": [hostid],
            "monitored": True
        }
        if search_keys:
            params["search"] = {"key_": search_keys}
            params["searchByAny"] = True
        return await self.execute_request("item.get", params)

    async def get_history(self, itemids: List[str], history_type: int = 0, time_from: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        # history_type: 0 - numeric float, 1 - character, 2 - log, 3 - numeric unsigned, 4 - text
        params = {
            "output": "extend",
            "history": history_type,
            "itemids": itemids,
            "time_from": time_from,
            "sortfield": "clock",
            "sortorder": "ASC",
            "limit": limit
        }
        return await self.execute_request("history.get", params)

    async def acknowledge_event(self, event_id: str, message: str) -> bool:
        # action: 2 = close problem, 4 = add message, 6 = acknowledge + message
        params = {
            "eventids": [event_id],
            "action": 6,
            "message": message
        }
        res = await self.execute_request("event.acknowledge", params)
        return bool(res and "eventids" in res)
