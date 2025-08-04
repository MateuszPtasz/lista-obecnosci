#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Prosty test API dla aplikacji mobilnej
Testuje konfigurację sieci i format odpowiedzi API
"""

import argparse
import requests
import json
import socket
import platform
import sys
import os
from datetime import datetime
import time

# Kolory do konsoli
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

def print_colored(text, color=RESET):
    """Drukuje tekst w kolorze"""
    print(f"{color}{text}{RESET}")

def print_header(text):
    """Drukuje nagłówek sekcji"""
    border = "=" * len(text)
    print_colored(f"\n{border}", BLUE)
    print_colored(text, BLUE)
    print_colored(f"{border}\n", BLUE)

def print_result(success, message):
    """Drukuje wynik testu"""
    prefix = f"{GREEN}✓ " if success else f"{RED}✗ "
    print(f"{prefix}{message}{RESET}")

def get_local_ip():
    """Zwraca lokalny adres IP"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception:
        return "nieznane"

def test_api_connection(url, endpoint="/api/connection-test", timeout=5):
    """Testuje połączenie z API"""
    full_url = f"{url}{endpoint}"
    
    try:
        response = requests.get(full_url, timeout=timeout)
        print_result(True, f"Połączenie z {full_url} działa (status: {response.status_code})")
        
        try:
            data = response.json()
            print(f"Odpowiedź: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True, data
        except json.JSONDecodeError:
            print_result(False, "Odpowiedź nie jest prawidłowym JSON")
            print(f"Otrzymano: {response.text[:100]}...")
            return True, response.text
    except requests.RequestException as e:
        print_result(False, f"Błąd połączenia z {full_url}: {str(e)}")
        return False, None

def check_mobile_config_format(data):
    """Sprawdza czy format odpowiedzi jest zgodny z oczekiwaniami aplikacji mobilnej"""
    if not isinstance(data, dict):
        print_result(False, "Odpowiedź nie jest obiektem JSON")
        return False
    
    if "config" in data and isinstance(data["config"], dict):
        print_result(True, "Format odpowiedzi jest POPRAWNY (zawiera zagnieżdżony obiekt 'config')")
        print(f"Struktura konfiguracji: {json.dumps({k: type(v).__name__ for k, v in data['config'].items()}, indent=2, ensure_ascii=False)}")
        return True
    else:
        print_result(False, "Format odpowiedzi jest NIEPOPRAWNY (brak zagnieżdżonego obiektu 'config')")
        print(f"Otrzymano strukturę: {json.dumps({k: type(v).__name__ for k, v in data.items()}, indent=2, ensure_ascii=False)}")
        return False

def test_mobile_app_api(base_url):
    """Testuje wszystkie endpointy potrzebne do działania aplikacji mobilnej"""
    print_header(f"TEST API DLA APLIKACJI MOBILNEJ ({base_url})")
    
    # Test podstawowego połączenia
    connection_ok, _ = test_api_connection(base_url, "/api/connection-test")
    if not connection_ok:
        return False
    
    # Test endpointu konfiguracji mobilnej
    print("\nTest endpointu konfiguracji mobilnej:")
    config_ok, config_data = test_api_connection(base_url, "/api/mobile-config")
    
    if config_ok and config_data:
        format_ok = check_mobile_config_format(config_data)
        if not format_ok:
            print_colored("\nSUGESTIA: Endpoint powinien zwracać dane w formacie:", YELLOW)
            print(json.dumps({
                "config": {
                    "enable_location": True,
                    "location_interval_seconds": 60,
                    # inne ustawienia konfiguracji
                },
                "version": "1.0.0",
                "timestamp": "2025-08-05T12:00:00"
            }, indent=2, ensure_ascii=False))
            
            print_colored("\nPrzekształć odpowiedź API w main.py, aby zwracała obiekt z kluczem 'config':", YELLOW)
            print("""
@app.get("/api/mobile-config")
def get_mobile_config():
    config_data = {
        "enable_location": True,
        # inne ustawienia
    }
    
    # Zwracamy zagnieżdżony format oczekiwany przez aplikację mobilną
    return {
        "config": config_data,  # <- kluczowe zagnieżdżenie!
        "version": "1.0.0",
        "timestamp": dt.datetime.now().isoformat()
    }
            """)
    
    return config_ok and (config_data and check_mobile_config_format(config_data))

def suggest_fixes():
    """Sugeruje poprawki do najczęstszych problemów"""
    print_header("SUGESTIE ROZWIĄZANIA PROBLEMÓW")
    
    print_colored("1. Problem z formatem danych API:", YELLOW)
    print("   - Upewnij się, że endpoint /api/mobile-config zwraca zagnieżdżony obiekt 'config'")
    print("   - Popraw implementację w pliku main.py")
    
    print_colored("\n2. Problem z połączeniem sieciowym:", YELLOW)
    print("   - Sprawdź czy serwer API jest uruchomiony")
    print("   - Upewnij się, że aplikacja ma dostęp do sieci")
    print("   - Sprawdź ustawienia zapory sieciowej")
    
    print_colored("\n3. Problem z adresami IP w konfiguracji aplikacji:", YELLOW)
    print("   - W aplikacji mobilnej użyj prawidłowego adresu IP serwera")
    print("   - Upewnij się, że urządzenie mobilne i serwer są w tej samej sieci")
    
    print_colored("\n4. Jak przetestować na urządzeniu mobilnym:", YELLOW)
    print("   - Upewnij się, że telefon i komputer są w tej samej sieci Wi-Fi")
    print("   - W aplikacji mobilnej użyj adresu IP komputera z serwerem")
    print(f"   - Sprawdź lokalny adres IP tego komputera: {get_local_ip()}")
    print("   - Upewnij się, że zapora na komputerze zezwala na połączenia do Pythona")

def main():
    parser = argparse.ArgumentParser(description='Test API dla aplikacji mobilnej')
    parser.add_argument('--host', default=None, help='Adres hosta API (np. localhost, 192.168.1.100)')
    parser.add_argument('--port', type=int, default=8000, help='Port API (domyślnie: 8000)')
    parser.add_argument('--endpoint', default="/api/mobile-config", help='Endpoint do testowania')
    parser.add_argument('--all-tests', action='store_true', help='Wykonaj wszystkie testy')
    
    args = parser.parse_args()
    
    # Informacje o systemie
    print_colored("TEST API DLA APLIKACJI MOBILNEJ LISTA OBECNOŚCI", MAGENTA)
    print_colored("=" * 45, MAGENTA)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Lokalny adres IP: {get_local_ip()}")
    
    # Ustal adresy do testów
    hosts = []
    if args.host:
        hosts = [args.host]
    else:
        hosts = ["localhost", "127.0.0.1", get_local_ip()]
        # Usuwamy duplikaty i None
        hosts = list(set([h for h in hosts if h]))
    
    port = args.port
    
    # Testowanie wszystkich hostów
    all_succeeded = True
    
    for host in hosts:
        base_url = f"http://{host}:{port}"
        
        if args.all_tests:
            if not test_mobile_app_api(base_url):
                all_succeeded = False
        else:
            print_header(f"TEST POJEDYNCZEGO ENDPOINTU: {base_url}{args.endpoint}")
            success, data = test_api_connection(base_url, args.endpoint)
            
            if not success:
                all_succeeded = False
            elif args.endpoint == "/api/mobile-config" and data:
                if not check_mobile_config_format(data):
                    all_succeeded = False
    
    # Wyświetlamy sugestie
    if not all_succeeded:
        suggest_fixes()
    else:
        print_colored("\nWszystkie testy zakończone sukcesem!", GREEN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nPrzerwano przez użytkownika", YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\nWystąpił nieoczekiwany błąd: {e}", RED)
        sys.exit(1)
