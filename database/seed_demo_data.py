import asyncio
import os
import sys

# Ensure backend in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models.server import Server, ServerGroup
from app.models.component import Component
from app.models.user import Role, User
from app.core.security import get_password_hash

async def seed_demo_data():
    print("Initializing Database & Seeding Baseline Servers...")
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # 1. Ensure Roles
        roles = {}
        for r_name in ["ADMIN", "OPERATOR", "VIEWER"]:
            res = await db.execute(select(Role).where(Role.name == r_name))
            role = res.scalar_one_or_none()
            if not role:
                role = Role(name=r_name, description=f"{r_name} role")
                db.add(role)
                await db.flush()
            roles[r_name] = role

        # 2. Ensure Admin User
        admin_res = await db.execute(select(User).where(User.username == "admin"))
        if not admin_res.scalar_one_or_none():
            admin = User(
                username="admin",
                email="admin@datacenter.local",
                full_name="NOC Lead Administrator",
                hashed_password=get_password_hash("admin123"),
                role_id=roles["ADMIN"].id,
                is_active=True
            )
            db.add(admin)

        # 3. Ensure Server Groups
        grp_res = await db.execute(select(ServerGroup).where(ServerGroup.name == "Core Infrastructure"))
        grp = grp_res.scalar_one_or_none()
        if not grp:
            grp = ServerGroup(
                name="Core Infrastructure",
                description="Host and VM Lab Monitoring",
                environment="Production"
            )
            db.add(grp)
            await db.flush()

        # 4. Target Server 1: Windows 11 Host
        win_res = await db.execute(select(Server).where(Server.hostname == "WIN11-HOST-01"))
        win_srv = win_res.scalar_one_or_none()
        if not win_srv:
            win_srv = Server(
                group_id=grp.id,
                hostname="WIN11-HOST-01",
                display_name="Windows 11 Host Machine",
                ip_address="127.0.0.1",
                os_type="WINDOWS",
                os_version="Windows 11 Pro 23H2",
                environment="Production",
                location="Office Lab",
                rack="Workstation-01",
                vendor="Custom / Host",
                model="Development Laptop",
                agent_status="ONLINE",
                overall_health="HEALTHY",
                consecutive_failures=0,
                cpu_utilization=34.5,
                memory_utilization=52.8,
                disk_utilization=64.2,
                uptime_seconds=86400 * 3
            )
            db.add(win_srv)
            await db.flush()

            # Add baseline components
            db.add(Component(
                server_id=win_srv.id,
                component_type="CPU",
                component_name="Intel/AMD Multi-Core CPU",
                component_identifier="cpu_core_0",
                status="HEALTHY",
                metrics_metadata={"utilization_pct": 34.5},
                data_source="ZABBIX_AGENT"
            ))
            db.add(Component(
                server_id=win_srv.id,
                component_type="MEMORY",
                component_name="Physical RAM (32 GB)",
                component_identifier="system_ram",
                status="HEALTHY",
                metrics_metadata={"utilization_pct": 52.8},
                data_source="ZABBIX_AGENT"
            ))
            db.add(Component(
                server_id=win_srv.id,
                component_type="DISK",
                component_name="NVMe Storage (C:)",
                component_identifier="fs_c",
                status="HEALTHY",
                metrics_metadata={"used_pct": 64.2},
                data_source="ZABBIX_AGENT"
            ))
            db.add(Component(
                server_id=win_srv.id,
                component_type="PSU",
                component_name="Chassis Power Supply",
                component_identifier="psu_primary",
                status="UNSUPPORTED",
                metrics_metadata={"message": "Sensor not available on client OS"},
                data_source="OS"
            ))

        # 5. Target Server 2: Linux VM (Hosting Zabbix Engine)
        linux_res = await db.execute(select(Server).where(Server.hostname == "LINUX-VM-01"))
        linux_srv = linux_res.scalar_one_or_none()
        if not linux_srv:
            linux_srv = Server(
                group_id=grp.id,
                hostname="LINUX-VM-01",
                display_name="Linux VM (Zabbix Server)",
                ip_address="192.168.56.101",
                os_type="LINUX",
                os_version="Ubuntu 24.04 LTS",
                environment="Production",
                location="Virtual Hypervisor",
                rack="VM-Host-A",
                vendor="VMware / VirtualBox / Hyper-V",
                model="Virtual Machine",
                zabbix_hostid="10084",
                agent_status="ONLINE",
                overall_health="HEALTHY",
                consecutive_failures=0,
                cpu_utilization=22.1,
                memory_utilization=48.6,
                disk_utilization=38.4,
                uptime_seconds=86400 * 5
            )
            db.add(linux_srv)
            await db.flush()

            db.add(Component(
                server_id=linux_srv.id,
                component_type="CPU",
                component_name="Virtual CPU (4 Cores)",
                component_identifier="vcpu_0",
                status="HEALTHY",
                metrics_metadata={"utilization_pct": 22.1},
                data_source="ZABBIX_AGENT"
            ))
            db.add(Component(
                server_id=linux_srv.id,
                component_type="MEMORY",
                component_name="System RAM (8 GB)",
                component_identifier="system_ram",
                status="HEALTHY",
                metrics_metadata={"utilization_pct": 48.6},
                data_source="ZABBIX_AGENT"
            ))
            db.add(Component(
                server_id=linux_srv.id,
                component_type="DISK",
                component_name="Root Filesystem (/)",
                component_identifier="fs_root",
                status="HEALTHY",
                metrics_metadata={"used_pct": 38.4},
                data_source="ZABBIX_AGENT"
            ))

        await db.commit()
        print("Demo data seeded successfully! 2 Target nodes registered (Windows 11 Host + Linux VM).")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
