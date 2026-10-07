import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    log_dir = settings.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    
    log_format = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
    )
    console_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # Application file handler
    app_handler = RotatingFileHandler(
        os.path.join(log_dir, "application.log"),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    app_handler.setFormatter(log_format)
    root_logger.addHandler(app_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)
    
    # Specific specialized loggers
    def configure_named_logger(name: str, filename: str) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = RotatingFileHandler(
            os.path.join(log_dir, filename),
            maxBytes=10*1024*1024,
            backupCount=5
        )
        handler.setFormatter(log_format)
        logger.addHandler(handler)
        return logger

    configure_named_logger("audit", "audit.log")
    configure_named_logger("notification", "notification.log")
    configure_named_logger("zabbix", "zabbix.log")

setup_logging()

# Convenient loggers
logger = logging.getLogger("server_health")
audit_logger = logging.getLogger("audit")
notification_logger = logging.getLogger("notification")
zabbix_logger = logging.getLogger("zabbix")
