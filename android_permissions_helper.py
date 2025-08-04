#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pomocnik do weryfikacji uprawnień aplikacji mobilnej na Androidzie
Generuje instrukcje sprawdzenia uprawnień na urządzeniu mobilnym
"""

import platform
import socket
import sys
import os
import json
import datetime as dt
import argparse

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

def get_local_ip():
    """Zwraca lokalny adres IP"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception:
        return "nieznane"

def generate_qr_code(data):
    """Generuje tekstowy kod QR dla podanych danych"""
    try:
        import qrcode
        from io import StringIO

        # Tworzymy kod QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Tworzymy obrazek w trybie tekstowym
        f = StringIO()
        qr.print_ascii(out=f)
        f.seek(0)
        return f.read()
    except ImportError:
        return "[Nie można wygenerować kodu QR - zainstaluj pakiet 'qrcode' za pomocą pip]"

def print_android_instructions():
    """Wyświetla instrukcje sprawdzenia uprawnień na Androidzie"""
    print_header("INSTRUKCJA SPRAWDZANIA UPRAWNIEŃ W APLIKACJI ANDROID")
    
    print("Aby sprawdzić i włączyć uprawnienia w aplikacji, wykonaj następujące kroki:")
    
    print(f"{GREEN}1. Otwórz Ustawienia na swoim urządzeniu Android{RESET}")
    print("   Znajdź ikonę zębatki lub przesuń palcem w dół i kliknij ikonę koła zębatego.\n")
    
    print(f"{GREEN}2. Przejdź do sekcji Aplikacje{RESET}")
    print("   Zależnie od urządzenia może nazywać się 'Aplikacje', 'Aplikacje i powiadomienia' lub podobnie.\n")
    
    print(f"{GREEN}3. Znajdź aplikację Lista Obecności{RESET}")
    print("   Może być konieczne kliknięcie 'Zobacz wszystkie aplikacje' aby zobaczyć pełną listę.\n")
    
    print(f"{GREEN}4. Wybierz sekcję Uprawnienia{RESET}")
    print("   Po wybraniu aplikacji, znajdź sekcję 'Uprawnienia' lub 'Zezwolenia'.\n")
    
    print(f"{GREEN}5. Upewnij się, że następujące uprawnienia są włączone:{RESET}")
    print("   - INTERNET (często ukryte, włączone domyślnie)")
    print("   - Lokalizacja (potrzebna do geolokalizacji)")
    print("   - Przechowywanie (może być potrzebne do zapisywania danych offline)\n")
    
    print(f"{GREEN}6. Sprawdź ustawienia oszczędzania baterii{RESET}")
    print("   Wróć do szczegółów aplikacji i znajdź sekcję 'Bateria' lub 'Optymalizacja baterii'")
    print("   Ustaw na 'Nieoptymalizowane' lub 'Bez ograniczeń', aby aplikacja mogła")
    print("   działać w tle i łączyć się z internetem.\n")
    
    print(f"{GREEN}7. Sprawdź ustawienia danych komórkowych{RESET}")
    print("   W szczegółach aplikacji, znajdź sekcję 'Użycie danych' lub 'Dane komórkowe'")
    print("   Upewnij się, że aplikacja ma pozwolenie na korzystanie z danych komórkowych i Wi-Fi.\n")
    
    print(f"{GREEN}8. Uruchom ponownie aplikację{RESET}")
    print("   Po zmianie ustawień uprawnień, całkowicie zamknij i ponownie uruchom aplikację.")

def print_network_settings():
    """Wyświetla instrukcje dotyczące ustawień sieciowych"""
    print_header("USTAWIENIA SIECIOWE")
    
    local_ip = get_local_ip()
    print(f"Lokalny adres IP tego komputera: {GREEN}{local_ip}{RESET}")
    print(f"Adres serwera API powinien być skonfigurowany jako: {GREEN}http://{local_ip}:8000{RESET}")
    
    print("\nAby sprawdzić połączenie sieciowe na urządzeniu Android:")
    print(f"{GREEN}1. Upewnij się, że telefon jest połączony z tą samą siecią Wi-Fi{RESET}")
    print("   Sprawdź to w Ustawieniach -> Wi-Fi\n")
    
    print(f"{GREEN}2. Sprawdź czy możesz otworzyć serwer w przeglądarce{RESET}")
    print(f"   Otwórz przeglądarkę na telefonie i wpisz: {GREEN}http://{local_ip}:8000{RESET}")
    print("   Powinieneś zobaczyć stronę serwera lub odpowiedź API\n")
    
    # Generowanie kodu QR dla łatwiejszego dostępu
    qr_url = f"http://{local_ip}:8000/api/connection-test"
    print(f"{GREEN}3. Zeskanuj kod QR, aby szybko sprawdzić połączenie:{RESET}")
    qr_code = generate_qr_code(qr_url)
    print(qr_code)
    print(f"Ten kod QR prowadzi do: {qr_url}\n")
    
    print(f"{GREEN}4. Sprawdź ustawienia w aplikacji mobilnej{RESET}")
    print("   Upewnij się, że w aplikacji jest skonfigurowany poprawny adres serwera")
    print(f"   Powinno to być: {GREEN}http://{local_ip}:8000{RESET}")

def main():
    parser = argparse.ArgumentParser(
        description='Pomocnik diagnostyczny do aplikacji mobilnej Lista Obecności'
    )
    parser.add_argument(
        '--qr', 
        action='store_true', 
        help='Generuj kody QR dla łatwego testowania na urządzeniu'
    )
    
    args = parser.parse_args()
    
    print_colored("POMOCNIK DIAGNOSTYCZNY DO APLIKACJI MOBILNEJ", MAGENTA)
    print_colored("=" * 45, MAGENTA)
    
    print(f"Data: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {platform.system()} {platform.release()}")
    
    print_android_instructions()
    print_network_settings()
    
    # Pokaż dodatkowe informacje dla trybu QR
    if args.qr:
        print_header("DODATKOWE LINKI TESTOWE (KODY QR)")
        
        local_ip = get_local_ip()
        
        test_urls = [
            {
                "name": "Test połączenia",
                "url": f"http://{local_ip}:8000/api/connection-test"
            },
            {
                "name": "Konfiguracja mobilna",
                "url": f"http://{local_ip}:8000/api/mobile-config"
            },
            {
                "name": "Test na alternatywnym porcie",
                "url": f"http://{local_ip}:8002/api/connection-test"
            }
        ]
        
        for test in test_urls:
            print(f"\n{GREEN}{test['name']}: {test['url']}{RESET}")
            qr_code = generate_qr_code(test['url'])
            print(qr_code)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nPrzerwano przez użytkownika", YELLOW)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\nWystąpił błąd: {e}", RED)
        sys.exit(1)
