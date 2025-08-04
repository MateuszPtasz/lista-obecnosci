"""
Skrypt do uruchamiania serwerów API Lista Obecności
"""
import subprocess
import sys
import os

# Próba importu centralnej konfiguracji
try:
    from configs.app_config import APP_PORT_MAIN, APP_PORT_ALT, APP_DEFAULT_IP, WEB_PANEL_PORT
    MAIN_PORT = APP_PORT_MAIN
    ALT_PORT = APP_PORT_ALT
    WEB_PORT = WEB_PANEL_PORT
    SERVER_IP = APP_DEFAULT_IP
    CENTRAL_CONFIG_LOADED = True
    print("Zaimportowano centralną konfigurację z configs/app_config.py")
except ImportError:
    MAIN_PORT = 8000
    ALT_PORT = 8080
    WEB_PORT = 8002
    SERVER_IP = "192.168.1.35"
    CENTRAL_CONFIG_LOADED = False
    print("UWAGA: Nie można zaimportować centralnej konfiguracji z configs/app_config.py")
    print("Używam domyślnych wartości")

def start_servers():
    """
    Uruchamia główny i alternatywny serwer API w oddzielnych procesach
    """
    print("===================================================")
    print("      Uruchamianie serwerów API Lista Obecności     ")
    print("===================================================")
    
    # Sprawdzanie czy katalog static istnieje, jeśli nie - utwórz go
    if not os.path.exists("static"):
        os.makedirs("static")
        print("✅ Utworzono brakujący katalog 'static'")
    
    # Uruchomienie głównego serwera
    main_server = subprocess.Popen([sys.executable, "main.py"])
    print(f"✅ Uruchomiono główny serwer na porcie {MAIN_PORT}")
    print(f"📡 Adres: http://{SERVER_IP}:{MAIN_PORT}")
    
    # Uruchomienie alternatywnego serwera
    alt_server = subprocess.Popen([sys.executable, "server_alt_port.py"])
    print(f"✅ Uruchomiono alternatywny serwer na porcie {ALT_PORT}")
    print(f"📡 Adres: http://{SERVER_IP}:{ALT_PORT}")
    
    # Uruchomienie serwera panelu webowego
    web_server = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", str(WEB_PORT)  # Rzutowanie na string, aby uniknąć TypeError
    ])
    print(f"✅ Uruchomiono serwer panelu webowego na porcie {WEB_PORT}")
    print(f"📡 Adres: http://{SERVER_IP}:{WEB_PORT}")
    
    print("\n💡 Serwery uruchomione! Pamiętaj o konfiguracji firewalla.")
    print("📄 Zobacz plik FIREWALL_INSTRUKCJA.md aby dowiedzieć się więcej.")
    
    if not CENTRAL_CONFIG_LOADED:
        print("\n⚠️ UWAGA: Centralna konfiguracja nie została załadowana!")
        print("Możesz napotkać problemy z konfiguracją aplikacji mobilnej.")
        print("Zalecane kroki:")
        print("1. Upewnij się, że katalog 'configs' istnieje")
        print("2. Sprawdź czy plik 'configs/app_config.py' jest dostępny i poprawny")
        print("3. Uruchom ponownie serwery")
    
    print("\nNaciśnij Ctrl+C aby zatrzymać wszystkie serwery...")
    
    try:
        # Czekaj na przerwanie przez użytkownika
        main_server.wait()
        alt_server.wait()
        web_server.wait()
    except KeyboardInterrupt:
        print("\n⚠️ Zatrzymywanie serwerów...")
        main_server.terminate()
        alt_server.terminate()
        web_server.terminate()
        print("✅ Serwery zatrzymane.")

if __name__ == "__main__":
    start_servers()
