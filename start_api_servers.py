"""
Skrypt do uruchamiania serwerów API Lista Obecności
"""
import subprocess
import sys
import os
import socket
import time

# Funkcja do sprawdzania, czy port jest już używany
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Funkcja do zatrzymywania procesu na określonym porcie
def kill_process_on_port(port):
    try:
        # Dla Windows
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        if output:
            # Wyciągnij PID z outputu (ostatnia kolumna)
            lines = output.strip().split('\n')
            for line in lines:
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.split()[-1]
                    print(f"⚠️ Port {port} jest już używany przez proces o PID {pid}. Próbuję zatrzymać...")
                    try:
                        subprocess.call(f"taskkill /F /PID {pid}", shell=True)
                        print(f"✅ Proces na porcie {port} został zatrzymany.")
                        # Daj czas na zwolnienie portu
                        time.sleep(1)
                        return True
                    except Exception as e:
                        print(f"❌ Nie można zatrzymać procesu na porcie {port}: {e}")
                        return False
    except Exception:
        # Jeśli nie znaleziono procesu lub wystąpił inny błąd
        return False
    return False

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
    
    # Sprawdź czy porty są już używane i zatrzymaj procesy, jeśli tak
    ports_to_check = [MAIN_PORT, ALT_PORT, WEB_PORT]
    for port in ports_to_check:
        if is_port_in_use(port):
            print(f"⚠️ Port {port} jest już używany!")
            kill_process_on_port(port)
            # Sprawdź ponownie, czy port został zwolniony
            if is_port_in_use(port):
                print(f"❌ Nie udało się zwolnić portu {port}. Spróbuj zatrzymać procesy ręcznie.")
                print(f"   Możesz użyć komendy: taskkill /F /FI \"WINDOWTITLE eq *python*\" /T")
                print(f"   lub: netstat -ano | findstr :{port}")
                input("Naciśnij Enter, aby kontynuować mimo to, lub Ctrl+C aby przerwać...")
    
    # Uruchomienie głównego serwera z dodatkowym parametrem dla debugowania
    try:
        main_server = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", str(MAIN_PORT),  # Główny port 8000
            "--log-level", "debug"  # Dodane pełne logowanie dla diagnostyki
        ])
        print(f"✅ Uruchomiono główny serwer na porcie {MAIN_PORT}")
        print(f"📡 Adres: http://{SERVER_IP}:{MAIN_PORT}")
    except Exception as e:
        print(f"❌ Błąd podczas uruchamiania głównego serwera: {str(e)}")
        main_server = None
    # Uruchomienie alternatywnego serwera
    try:
        alt_server = subprocess.Popen([sys.executable, "server_alt_port.py"])
        print(f"✅ Uruchomiono alternatywny serwer na porcie {ALT_PORT}")
        print(f"📡 Adres: http://{SERVER_IP}:{ALT_PORT}")
    except Exception as e:
        print(f"❌ Błąd podczas uruchamiania alternatywnego serwera: {str(e)}")
        alt_server = None
    
    # Uruchomienie serwera panelu webowego
    try:
        web_server = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", str(WEB_PORT)  # Rzutowanie na string, aby uniknąć TypeError
            # Usunięto opcję --reload, aby zapobiec automatycznemu restartowi
        ])
        print(f"✅ Uruchomiono serwer panelu webowego na porcie {WEB_PORT}")
        print(f"📡 Adres: http://{SERVER_IP}:{WEB_PORT}")
    except Exception as e:
        print(f"❌ Błąd podczas uruchamiania serwera panelu webowego: {str(e)}")
        web_server = None
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
        if main_server:
            main_server.wait()
        if alt_server:
            alt_server.wait()
        if web_server:
            web_server.wait()
    except KeyboardInterrupt:
        print("\n⚠️ Zatrzymywanie serwerów...")
        if main_server:
            main_server.terminate()
        if alt_server:
            alt_server.terminate()
        if web_server:
            web_server.terminate()
        print("✅ Serwery zatrzymane.")

if __name__ == "__main__":
    start_servers()
