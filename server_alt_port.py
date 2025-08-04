"""
Alternatywny serwer Lista Obecnosci na porcie alternatywnym
Używaj tego gdy główny port jest blokowany przez firewall
"""
import uvicorn
from main import app
import os

# Próba importu centralnej konfiguracji
try:
    from configs.app_config import APP_PORT_ALT, APP_DEFAULT_IP
    print("Zaimportowano centralną konfigurację z configs/app_config.py")
    PORT = APP_PORT_ALT
    IP = APP_DEFAULT_IP
except ImportError:
    print("UWAGA: Nie można zaimportować centralnej konfiguracji z configs/app_config.py")
    print("Używam domyślnych wartości 0.0.0.0:8080")
    PORT = 8080
    IP = "0.0.0.0"

if __name__ == "__main__":
    print(f"🚀 Uruchamianie serwera Lista Obecności na alternatywnym porcie {PORT}...")
    print("💡 Ten port może nie być blokowany przez Windows Firewall")
    print(f"📱 Zmień w aplikacji mobilnej adres na: http://{IP}:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
