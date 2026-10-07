import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.logging import logger, setup_logging
from app.core.security import get_password_hash
from app.models.user import Role, User
from app.models.notification import NotificationChannel
from app.api.v1 import auth, servers, alerts, dashboard, maintenance, notifications, audit, system, websocket
from app.services.sync.worker import start_background_sync_loop

async def seed_initial_data():
    """Initializes default roles, admin user, and default notification channel if not already seeded."""
    async with AsyncSessionLocal() as db:
        try:
            # Roles
            for r_name, r_desc in [("ADMIN", "System Administrator"), ("OPERATOR", "NOC Operator"), ("VIEWER", "Read-Only Viewer")]:
                r_q = select(Role).where(Role.name == r_name)
                res = await db.execute(r_q)
                if not res.scalar_one_or_none():
                    db.add(Role(name=r_name, description=r_desc))
            await db.flush()
            
            # Admin User
            admin_q = select(User).where(User.username == "admin")
            admin_res = await db.execute(admin_q)
            if not admin_res.scalar_one_or_none():
                admin_role_q = select(Role).where(Role.name == "ADMIN")
                admin_role = (await db.execute(admin_role_q)).scalar_one()
                admin_user = User(
                    username="admin",
                    email="admin@serverhealth.local",
                    full_name="System Administrator",
                    hashed_password=get_password_hash("admin123"),
                    role_id=admin_role.id,
                    is_active=True
                )
                db.add(admin_user)
                logger.info("Default administrator account created (username: admin / pass: admin123)")
                
            # Default Email Channel
            chan_q = select(NotificationChannel).where(NotificationChannel.name == "Default SMTP")
            if not (await db.execute(chan_q)).scalar_one_or_none():
                db.add(NotificationChannel(
                    name="Default SMTP",
                    channel_type="EMAIL",
                    config={
                        "host": settings.SMTP_HOST,
                        "port": settings.SMTP_PORT,
                        "username": settings.SMTP_USERNAME,
                        "sender": settings.SMTP_SENDER,
                        "tls": settings.SMTP_TLS,
                        "ssl": settings.SMTP_SSL
                    },
                    is_default=True,
                    is_enabled=True
                ))
                
            await db.commit()
        except Exception as e:
            logger.error(f"Error seeding initial data: {e}")
            await db.rollback()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Server Health Monitoring Backend...")
    setup_logging()
    await init_db()
    await seed_initial_data()
    
    # Start background synchronization worker
    sync_task = asyncio.create_task(start_background_sync_loop())
    yield
    # Shutdown
    sync_task.cancel()
    logger.info("Shutting down Server Health Monitoring Backend.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Server Health Monitoring Platform with Zabbix Integration and Real-time Alerting",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred. Please consult system logs."}
    )

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(servers.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(maintenance.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)
app.include_router(websocket.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}
