# logging_config.py - Centralized logging configuration

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "access": {
            "format": "%(asctime)s - %(remote_addr)s - %(method)s %(url)s - %(status_code)s - %(response_time)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "access",
            "filename": "logs/access.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "": {  # Root logger
            "level": "INFO",
            "handlers": ["console", "file", "error_file"]
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access_file"],
            "propagate": False
        },
        "lista_obecnosci": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "auth": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)

# Get loggers
app_logger = logging.getLogger("lista_obecnosci")
auth_logger = logging.getLogger("auth")
access_logger = logging.getLogger("uvicorn.access")

def log_request(request, response, response_time: float = None):
    """Log HTTP request/response"""
    access_logger.info(
        "",
        extra={
            "remote_addr": getattr(request.client, "host", "unknown") if hasattr(request, "client") else "unknown",
            "method": request.method,
            "url": str(request.url),
            "status_code": getattr(response, "status_code", "unknown"),
            "response_time": f"{response_time:.3f}s" if response_time else "unknown"
        }
    )

def log_auth_event(event_type: str, username: str = None, details: Dict[str, Any] = None):
    """Log authentication events"""
    message = f"Auth event: {event_type}"
    if username:
        message += f" - User: {username}"
    if details:
        message += f" - Details: {details}"
    
    auth_logger.info(message)

def log_error(error: Exception, context: str = None, user: str = None):
    """Log application errors"""
    message = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    if user:
        message += f" - User: {user}"
    
    app_logger.error(message, exc_info=True)

def log_security_event(event_type: str, details: Dict[str, Any] = None, severity: str = "WARNING"):
    """Log security events"""
    message = f"Security event: {event_type}"
    if details:
        message += f" - Details: {details}"
    
    if severity == "ERROR":
        app_logger.error(message)
    elif severity == "WARNING":
        app_logger.warning(message)
    else:
        app_logger.info(message)

# Request logging middleware
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        app_logger.debug(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            log_request(request, response, process_time)
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            log_error(e, f"Request processing: {request.method} {request.url}")
            
            # Re-raise the exception
            raise