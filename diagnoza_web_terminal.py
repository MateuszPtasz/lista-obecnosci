# Skrypt do sprawdzania konfiguracji bez zależności zewnętrznych
import os
import sys
import importlib.util
import traceback
import datetime
import json
import urllib.request
import socket

def print_colored(text, color):
    """Wyświetla kolorowy tekst w terminalu"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def check_config_file():
    """Sprawdza plik config.py"""
    print_colored("\n=== Sprawdzanie pliku konfiguracyjnego ===", "cyan")
    config_path = "config.py"
    
    if not os.path.exists(config_path):
        print_colored(f"BŁĄD: Plik {config_path} nie istnieje!", "red")
        return False
    
    print_colored(f"✓ Plik {config_path} istnieje", "green")
    
    # Sprawdź uprawnienia
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        print_colored(f"✓ Plik {config_path} można odczytać", "green")
    except Exception as e:
        print_colored(f"BŁĄD: Nie można odczytać pliku: {str(e)}", "red")
        return False
    
    return True

def check_config_import():
    """Próbuje zaimportować config.py"""
    print_colored("\n=== Sprawdzanie importu konfiguracji ===", "cyan")
    try:
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # Sprawdź kluczowe zmienne
        if hasattr(config, "MOBILE_APP_CONFIG"):
            print_colored(f"✓ Konfiguracja aplikacji mobilnej: {config.MOBILE_APP_CONFIG}", "green")
        else:
            print_colored("BŁĄD: Brak konfiguracji MOBILE_APP_CONFIG!", "red")
            return False
            
        if hasattr(config, "APP_VERSION_INFO"):
            print_colored(f"✓ Informacje o wersji: {config.APP_VERSION_INFO}", "green")
        else:
            print_colored("⚠ Ostrzeżenie: Brak informacji APP_VERSION_INFO", "yellow")
            
        return True
    except Exception as e:
        print_colored(f"BŁĄD: Nie można zaimportować konfiguracji: {str(e)}", "red")
        print_colored(traceback.format_exc(), "red")
        return False

def check_api_endpoint():
    """Sprawdza endpoint API dla konfiguracji mobilnej używając urllib"""
    print_colored("\n=== Sprawdzanie API konfiguracji mobilnej ===", "cyan")
    
    endpoints = [
        "http://localhost:8000/mobile-config",
        "http://localhost:8080/mobile-config",
        "http://127.0.0.1:8000/mobile-config",
        "http://127.0.0.1:8080/mobile-config"
    ]
    
    success = False
    
    for endpoint in endpoints:
        try:
            print_colored(f"Sprawdzam endpoint: {endpoint}", "yellow")
            req = urllib.request.Request(endpoint)
            response = urllib.request.urlopen(req, timeout=2)
            
            if response.status == 200:
                print_colored(f"✓ Endpoint {endpoint} działa (status 200)", "green")
                try:
                    data = response.read().decode('utf-8')
                    config_data = json.loads(data)
                    print_colored("✓ Zwrócono poprawne dane JSON", "green")
                    print_colored(f"Struktura danych: {json.dumps(config_data, indent=2)}", "cyan")
                    success = True
                except:
                    print_colored("⚠ Ostrzeżenie: Otrzymano odpowiedź, ale nie jest to prawidłowy JSON", "yellow")
            else:
                print_colored(f"⚠ Endpoint {endpoint} zwrócił status {response.status}", "yellow")
                
        except urllib.error.URLError:
            print_colored(f"⚠ Nie można połączyć się z {endpoint}", "yellow")
        except socket.timeout:
            print_colored(f"⚠ Timeout przy połączeniu z {endpoint}", "yellow")
        except Exception as e:
            print_colored(f"⚠ Błąd przy sprawdzaniu {endpoint}: {str(e)}", "yellow")
    
    if not success:
        print_colored("BŁĄD: Nie można połączyć się z żadnym endpointem API!", "red")
        print_colored("Sprawdź czy serwery są uruchomione (porty 8000 i 8080)", "red")
    
    return success

def check_terminal_session():
    """Sprawdza środowisko terminala i sesji"""
    print_colored("\n=== Sprawdzanie środowiska terminala i sesji ===", "cyan")
    
    # Sprawdź system operacyjny
    print_colored(f"System: {os.name}", "yellow")
    
    # Sprawdź zmienne środowiskowe
    print_colored("Zmienne środowiskowe:", "yellow")
    for var in ['PATH', 'PYTHONPATH', 'TEMP', 'USERNAME']:
        if var in os.environ:
            print_colored(f"  - {var}: {os.environ.get(var)}", "green")
        else:
            print_colored(f"  - {var}: Brak", "red")
    
    # Sprawdź aktualny katalog
    print_colored(f"Aktualny katalog: {os.getcwd()}", "yellow")
    
    # Sprawdź czy możemy wykonywać komendy
    try:
        import subprocess
        result = subprocess.run("echo Test", shell=True, capture_output=True, text=True)
        print_colored(f"Test wykonania komendy: {result.stdout.strip()}", "green")
    except Exception as e:
        print_colored(f"Błąd wykonania komendy: {str(e)}", "red")
    
    return True

def main():
    """Główna funkcja diagnostyczna"""
    print_colored("=============================================", "cyan")
    print_colored("  DIAGNOSTYKA KONFIGURACJI APLIKACJI MOBILNEJ ", "cyan")
    print_colored("=============================================", "cyan")
    print_colored(f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "yellow")
    
    results = []
    results.append(("Środowisko terminala", check_terminal_session()))
    results.append(("Plik konfiguracyjny", check_config_file()))
    results.append(("Import konfiguracji", check_config_import()))
    results.append(("Endpoint API", check_api_endpoint()))
    
    print_colored("\n=============================================", "cyan")
    print_colored("             WYNIKI DIAGNOSTYKI              ", "cyan")
    print_colored("=============================================", "cyan")
    
    for name, result in results:
        status = "✓ OK" if result else "✗ BŁĄD"
        color = "green" if result else "red"
        print_colored(f"{name}: {status}", color)
    
    if all(result for _, result in results):
        print_colored("\nWszystkie testy zakończone pomyślnie! ✓", "green")
    else:
        print_colored("\nWystąpiły problemy z konfiguracją! ✗", "red")
        print_colored("Sprawdź powyższe komunikaty błędów.", "red")
    
    print_colored("\n=============================================", "cyan")
    print_colored("             INSTRUKCJE URUCHOMIENIA         ", "cyan")
    print_colored("=============================================", "cyan")
    print_colored("W terminalu VS Code:", "yellow")
    print_colored("  .\\diagnoza_konfiguracji.bat", "white")
    print_colored("W terminalu webowym:", "yellow")
    print_colored("  python diagnoza_web_terminal.py", "white")
    print_colored("Diagnostyka środowiska:", "yellow")
    print_colored("  powershell -ExecutionPolicy Bypass -File diagnostyka_terminal.ps1", "white")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_colored(f"BŁĄD KRYTYCZNY: {str(e)}", "red")
        print_colored(traceback.format_exc(), "red")
        sys.exit(1)
