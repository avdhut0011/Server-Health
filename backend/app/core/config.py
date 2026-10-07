from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "Server Health Monitoring Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, testing, production
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Security & Auth
    SECRET_KEY: str = "supersecretkey_for_server_health_monitoring_2026_change_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
    
    # Database
    # Default to sqlite for instant local test capability if postgres isn't running yet, with postgres support
    DATABASE_URL: str = "sqlite+aiosqlite:///./server_health.db"
    SYNC_DATABASE_URL: str = "sqlite:///./server_health.db"
    
    # Zabbix Server API Configuration
    ZABBIX_URL: str = "http://localhost:8080/api_jsonrpc.php"
    ZABBIX_USERNAME: str = "Admin"
    ZABBIX_PASSWORD: str = "zabbix"
    ZABBIX_API_TOKEN: Optional[str] = None
    ZABBIX_TIMEOUT: int = 10
    ZABBIX_VERIFY_SSL: bool = False
    ZABBIX_SYNC_INTERVAL_SECONDS: int = 10
    
    # Health & Availability Logic
    CONSECUTIVE_FAILURES_FOR_DOWN: int = 3
    
    # Default Metric Thresholds
    CPU_WARNING_THRESHOLD: float = 70.0
    CPU_CRITICAL_THRESHOLD: float = 90.0
    MEMORY_WARNING_THRESHOLD: float = 80.0
    MEMORY_CRITICAL_THRESHOLD: float = 95.0
    DISK_WARNING_THRESHOLD: float = 80.0
    DISK_CRITICAL_THRESHOLD: float = 90.0
    LATENCY_WARNING_MS: float = 100.0
    LATENCY_CRITICAL_MS: float = 300.0
    PACKET_LOSS_WARNING_PCT: float = 2.0
    PACKET_LOSS_CRITICAL_PCT: float = 10.0
    
    # Generic SMTP Email Configuration
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_SENDER: str = "alerts@serverhealth.local"
    NOTIFICATION_MAX_RETRIES: int = 3
    
    # Logging
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
