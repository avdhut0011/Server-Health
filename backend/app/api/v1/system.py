from typing import List
from fastapi import APIRouter, Depends
from app.services.zabbix.service import zabbix_service
from app.schemas.zabbix import ZabbixStatusResponse, ZabbixHostDTO
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/system", tags=["System & Zabbix Integration"])

@router.get("/zabbix-status", response_model=ZabbixStatusResponse)
async def get_zabbix_status(current_user: User = Depends(get_current_user)):
    return await zabbix_service.check_connection()

@router.get("/zabbix-discovered-hosts", response_model=List[ZabbixHostDTO])
async def get_zabbix_discovered_hosts(current_user: User = Depends(get_current_user)):
    return await zabbix_service.get_all_monitored_hosts()
