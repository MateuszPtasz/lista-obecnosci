import subprocess
import os
import sys
import time
from datetime import datetime

# Próba importu centralnej konfiguracji
try:
    from configs.app_config import APP_PORT_MAIN, APP_PORT_ALT, APP_DEFAULT_IP, WEB_PANEL_PORT, LISTEN_ALL_IP
    MAIN_PORT = APP_PORT_MAIN
    WEB_PORT = WEB_PANEL_PORT
    SERVER_IP = APP_DEFAULT_IP
    HOST_IP = LISTEN_ALL_IP
    CENTRAL_CONFIG_LOADED = True
except ImportError:
    MAIN_PORT = 8000
    WEB_PORT = 8002
    SERVER_IP = "192.168.1.35"
    HOST_IP = "0.0.0.0"
    CENTRAL_CONFIG_LOADED = False

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def start_api_server(port, host=HOST_IP):
    log(f"Uruchamianie serwera API na {host}:{port}...")
    try:
        # Uruchom główny serwer API
        cmd = [sys.executable, "main.py", "--host", host, "--port", str(port)]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        log(f"Serwer API uruchomiony na {host}:{port}, PID: {process.pid}")
        return process
    except Exception as e:
        log(f"Błąd podczas uruchamiania serwera API na porcie {port}: {str(e)}")
        return None

def main():
    log("Uruchamianie serwerów API...")
    
    if CENTRAL_CONFIG_LOADED:
        log(f"Zaimportowano centralną konfigurację z configs/app_config.py")
        log(f"Używam adresu IP serwera: {SERVER_IP}")
    else:
        log(f"UWAGA: Nie można zaimportować centralnej konfiguracji z configs/app_config.py")
        log(f"Używam domyślnego adresu IP serwera: {SERVER_IP}")
    
    # Uruchom serwer API dla aplikacji mobilnej na porcie MAIN_PORT
    api_server = start_api_server(MAIN_PORT)
    
    # Uruchom serwer API dla panelu webowego na porcie WEB_PORT
    web_panel_server = start_api_server(WEB_PORT)
    
    log("Wszystkie serwery zostały uruchomione.")
    log(f"API mobilne dostępne pod adresem: http://{SERVER_IP}:{MAIN_PORT}")
    log(f"Panel webowy dostępny pod adresem: http://{SERVER_IP}:{WEB_PORT}")
    log("Naciśnij Ctrl+C, aby zatrzymać serwery.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Otrzymano sygnał przerwania. Zamykanie serwerów...")
        if api_server:
            api_server.terminate()
        if web_panel_server:
            web_panel_server.terminate()
        log("Serwery zostały zatrzymane.")

if __name__ == "__main__":
    main()
