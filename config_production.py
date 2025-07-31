# config_production.py - Production configuration template
# Copy this file to config.py and modify for your production environment

import os
from typing import Dict, Any

# Get environment variables with defaults
def get_env_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in ('true', '1', 'yes', 'on')

def get_env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-production-secret-key-change-this-immediately")
DEBUG = get_env_bool("DEBUG", False)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Database Configuration  
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/shifts.db")

# Mobile App Configuration
MOBILE_APP_CONFIG: Dict[str, Any] = {
    "timer_enabled": get_env_bool("TIMER_ENABLED", True),
    "daily_stats": get_env_bool("DAILY_STATS", False),
    "monthly_stats": get_env_bool("MONTHLY_STATS", False),
    "field_blocking": get_env_bool("FIELD_BLOCKING", True),
    "gps_verification": get_env_bool("GPS_VERIFICATION", True),
    "widget_support": get_env_bool("WIDGET_SUPPORT", False),
    "notifications": get_env_bool("NOTIFICATIONS", True),
    "offline_mode": get_env_bool("OFFLINE_MODE", True),
    "debug_mode": get_env_bool("APP_DEBUG_MODE", False),
    "auto_updates": get_env_bool("AUTO_UPDATES", True),
    "forceUpdate": get_env_bool("FORCE_UPDATE", False),
}

# Configuration version - increment when changing mobile config
CONFIG_VERSION = os.getenv("CONFIG_VERSION", "2.0")

# Email Configuration
EMAIL_CONFIG: Dict[str, Any] = {
    "enabled": get_env_bool("EMAIL_ENABLED", False),
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": get_env_int("SMTP_PORT", 587),
    "smtp_username": os.getenv("SMTP_USERNAME", ""),
    "smtp_password": os.getenv("SMTP_PASSWORD", ""),
    "sender_email": os.getenv("SENDER_EMAIL", ""),
    "sender_name": os.getenv("SENDER_NAME", "System Lista Obecności"),
    "use_tls": get_env_bool("SMTP_USE_TLS", True),
    "use_ssl": get_env_bool("SMTP_USE_SSL", False),
    "timeout": get_env_int("SMTP_TIMEOUT", 30),
}

# App Version Information
APP_VERSION_INFO: Dict[str, Any] = {
    "current_version": os.getenv("APP_CURRENT_VERSION", "1.0.0"),
    "minimum_version": os.getenv("APP_MINIMUM_VERSION", "1.0.0"),
    "update_required": get_env_bool("UPDATE_REQUIRED", False),
    "update_message": os.getenv("UPDATE_MESSAGE", "Dostępna nowa wersja aplikacji z ulepszeniami!"),
    "play_store_url": os.getenv("PLAY_STORE_URL", "https://play.google.com/store/apps/details?id=com.example.lista_obecnosci"),
    "update_features": [
        "Enhanced security with JWT authentication",
        "Improved CSV export functionality", 
        "Better error handling and logging",
        "Production-ready Docker deployment"
    ]
}

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = get_env_bool("LOG_TO_FILE", True)
LOG_FILE_MAX_SIZE = get_env_int("LOG_FILE_MAX_SIZE", 10485760)  # 10MB
LOG_FILE_BACKUP_COUNT = get_env_int("LOG_FILE_BACKUP_COUNT", 5)

# Security Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
CORS_ALLOW_CREDENTIALS = get_env_bool("CORS_ALLOW_CREDENTIALS", True)

# Rate Limiting
RATE_LIMIT_ENABLED = get_env_bool("RATE_LIMIT_ENABLED", True)
RATE_LIMIT_REQUESTS_PER_MINUTE = get_env_int("RATE_LIMIT_RPM", 60)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = get_env_int("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60)

# Admin User Configuration (for initial setup)
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "change-this-password")

# Backup Configuration
BACKUP_ENABLED = get_env_bool("BACKUP_ENABLED", True)
BACKUP_SCHEDULE = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
BACKUP_RETENTION_DAYS = get_env_int("BACKUP_RETENTION_DAYS", 30)
BACKUP_RETENTION_COUNT = get_env_int("BACKUP_RETENTION_COUNT", 10)

# Feature Flags
FEATURES = {
    "csv_export": get_env_bool("FEATURE_CSV_EXPORT", True),
    "email_reports": get_env_bool("FEATURE_EMAIL_REPORTS", True),
    "mobile_api": get_env_bool("FEATURE_MOBILE_API", True),
    "web_panel": get_env_bool("FEATURE_WEB_PANEL", True),
    "backup_api": get_env_bool("FEATURE_BACKUP_API", True),
}

# Production Settings Validation
def validate_production_config():
    """Validate production configuration"""
    issues = []
    
    if SECRET_KEY == "your-production-secret-key-change-this-immediately":
        issues.append("SECRET_KEY must be changed from default value")
    
    if len(SECRET_KEY) < 32:
        issues.append("SECRET_KEY should be at least 32 characters long")
    
    if DEBUG:
        issues.append("DEBUG should be False in production")
    
    if EMAIL_CONFIG["enabled"] and not EMAIL_CONFIG["smtp_username"]:
        issues.append("SMTP_USERNAME required when email is enabled")
    
    if EMAIL_CONFIG["enabled"] and not EMAIL_CONFIG["smtp_password"]:
        issues.append("SMTP_PASSWORD required when email is enabled")
    
    return issues

# Print configuration warnings on import
if __name__ != "__main__":
    config_issues = validate_production_config()
    if config_issues:
        import warnings
        for issue in config_issues:
            warnings.warn(f"Configuration issue: {issue}", UserWarning)