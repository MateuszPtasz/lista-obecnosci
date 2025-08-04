# -*- coding: utf-8 -*-
"""
Konfiguracja API dla systemu Lista Obecności
"""

import os
import socket
from datetime import datetime

# Podstawowa konfiguracja API
API_CONFIG = {
    "title": "System Lista Obecności API",
    "description": "API dla systemu do zarządzania listą obecności pracowników",
    "version": "1.2.5",
    "debug": True
}

# Porty dla serwerów API
API_PORTS = {
    "main": 8000,
    "backup": 8002
}

# Konfiguracja zabezpieczeń
SECURITY_CONFIG = {
    "jwt_secret": os.environ.get("JWT_SECRET", "tajny_klucz_jwt_12345"),
    "token_expiry_minutes": 60 * 12,  # 12 godzin
    "require_auth": True,
    "cors_origins": ["*"]  # W produkcji należy ograniczyć do konkretnych domen
}

# Diagnostyka API
ENABLE_DIAGNOSTICS = True

# Funkcja do logowania diagnostycznego
def log_diagnostic(message, level="INFO"):
    """Loguje wiadomości diagnostyczne"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()
    print(f"[{timestamp}] [{level}] [{hostname}] {message}")

# Lista aktywnych endpointów (dla dokumentacji)
ACTIVE_ENDPOINTS = [
    {"path": "/api/workers", "methods": ["GET", "POST"], "description": "Zarządzanie pracownikami"},
    {"path": "/api/workers/{worker_id}", "methods": ["GET", "PUT", "DELETE"], "description": "Szczegóły pracownika"},
    {"path": "/api/mobile-config", "methods": ["GET", "POST"], "description": "Konfiguracja aplikacji mobilnej"},
    {"path": "/api/app-version", "methods": ["GET"], "description": "Informacje o wersji aplikacji"},
    {"path": "/api/connection-test", "methods": ["GET"], "description": "Test połączenia z API"}
]

# Funkcja do sprawdzania czy endpoint jest aktywny
def is_endpoint_active(path, method="GET"):
    """Sprawdza czy endpoint jest aktywny"""
    for endpoint in ACTIVE_ENDPOINTS:
        if endpoint["path"] == path and method in endpoint["methods"]:
            return True
    return False
