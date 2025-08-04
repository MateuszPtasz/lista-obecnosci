"""
Skrypt do testowania zapisywania i odczytywania konfiguracji z uwierzytelnianiem
"""
import os
import sys
import json
import shutil
import requests
from datetime import datetime
import getpass

def test_config_save_with_auth():
    """Test zapisywania konfiguracji z uwierzytelnianiem"""
    print("\n===== TEST ZAPISYWANIA KONFIGURACJI (Z UWIERZYTELNIANIEM) =====")
    
    # Pobierz dane logowania administratora
    print("\n🔐 Logowanie administratora jest wymagane do zapisania konfiguracji")
    admin_username = input("Podaj ID administratora: ")
    admin_password = getpass.getpass("Podaj hasło administratora: ")
    
    # Zaloguj się jako administrator, aby uzyskać sesję
    session = requests.Session()
    try:
        login_url = "http://localhost:8002/api/login"
        login_data = {
            "username": admin_username,
            "password": admin_password
        }
        
        print(f"🔑 Logowanie jako administrator: {admin_username}")
        login_response = session.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Błąd logowania: {login_response.status_code} - {login_response.text}")
            return False
            
        print("✅ Logowanie udane!")
        
    except Exception as e:
        print(f"❌ Błąd podczas logowania: {e}")
        return False
    
    # Stworzenie kopii zapasowej config.py
    config_path = "config.py"
    if not os.path.exists(config_path):
        print(f"❌ Plik {config_path} nie istnieje!")
        return False
    
    backup_path = f"config_backup_test_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
    try:
        shutil.copy(config_path, backup_path)
        print(f"✅ Utworzono kopię zapasową: {backup_path}")
    except Exception as e:
        print(f"❌ Błąd podczas tworzenia kopii zapasowej: {e}")
        return False
    
    # Testowa konfiguracja
    test_config = {
        "MOBILE_APP_CONFIG": {
            "timer_enabled": True,
            "daily_stats": True,
            "monthly_stats": True,
            "field_blocking": True,
            "gps_verification": False,  # Zmieniamy wartość
            "widget_support": False,
            "notifications": True,  # Zmieniamy wartość
            "offline_mode": True,
            "debug_mode": True,
            "auto_updates": False,
            "forceUpdate": False,
            "test_timestamp": datetime.now().strftime("%Y%m%d%H%M%S")  # Dodajemy nowe pole
        }
    }
    
    # Wysłanie konfiguracji do API z sesją uwierzytelnioną
    try:
        api_url = "http://localhost:8002/api/mobile-config"
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"📤 Wysyłanie konfiguracji do: {api_url}")
        print(f"📋 Konfiguracja: {json.dumps(test_config, indent=2)}")
        
        # Używamy tej samej sesji, która ma już cookies uwierzytelniające
        response = session.post(api_url, json=test_config, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Sukces! Odpowiedź API: {response.json()}")
        else:
            print(f"❌ Błąd API {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania żądania: {e}")
        return False
    
    # Sprawdzenie czy plik został zaktualizowany
    print("\n📂 Sprawdzanie, czy plik config.py został zaktualizowany...")
    
    try:
        # Odczekaj chwilę, aby upewnić się, że zmiany zostały zapisane
        import time
        time.sleep(1)
        
        with open(config_path, "r", encoding="utf-8") as f:
            updated_content = f.read()
            
        # Sprawdzenie czy nasz znacznik czasu został dodany
        timestamp = test_config["MOBILE_APP_CONFIG"]["test_timestamp"]
        if timestamp in updated_content:
            print(f"✅ Znaleziono testowy znacznik czasu w pliku: {timestamp}")
            print("✅ Konfiguracja została pomyślnie zaktualizowana!")
        else:
            print(f"❌ Nie znaleziono testowego znacznika czasu w pliku!")
            print("Aktualna zawartość pliku:")
            print("-------------------")
            print(updated_content[:500] + "..." if len(updated_content) > 500 else updated_content)
            print("-------------------")
            return False
    except Exception as e:
        print(f"❌ Błąd podczas sprawdzania pliku konfiguracyjnego: {e}")
        return False
    
    return True

def test_config_read():
    """Test odczytywania konfiguracji"""
    print("\n===== TEST ODCZYTYWANIA KONFIGURACJI =====")
    
    endpoints = [
        "http://localhost:8000/api/mobile-config",
        "http://localhost:8002/api/mobile-config",
        "http://localhost:8080/api/mobile-config",
        "http://localhost:8000/mobile-config",
        "http://localhost:8002/mobile-config",
        "http://localhost:8080/mobile-config"
    ]
    
    all_success = True
    
    for endpoint in endpoints:
        print(f"\n🔍 Sprawdzanie endpointu: {endpoint}")
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sukces! Otrzymano odpowiedź: {json.dumps(data, indent=2)[:300]}...")
                
                # Sprawdzenie czy odpowiedź zawiera klucz "config"
                if "config" in data:
                    print("✅ Odpowiedź zawiera klucz 'config'")
                else:
                    print("❌ Odpowiedź nie zawiera klucza 'config'")
                    all_success = False
            else:
                print(f"❌ Błąd {response.status_code}: {response.text}")
                all_success = False
        except Exception as e:
            print(f"❌ Błąd podczas łączenia z {endpoint}: {e}")
            all_success = False
    
    return all_success

def main():
    """Główna funkcja testu"""
    print("=" * 49)
    print("   TEST ZAPISYWANIA I ODCZYTYWANIA KONFIGURACJI   ")
    print("=" * 49)
    
    # Test zapisywania konfiguracji
    save_success = test_config_save_with_auth()
    
    # Test odczytywania konfiguracji
    read_success = test_config_read()
    
    # Podsumowanie
    print("\n" + "=" * 49)
    print("                  PODSUMOWANIE")
    print("=" * 49)
    print(f"Test zapisu konfiguracji: {'✅ ZALICZONY' if save_success else '❌ NIEZALICZONY'}")
    print(f"Test odczytu konfiguracji: {'✅ ZALICZONY' if read_success else '❌ NIEZALICZONY'}")
    
    if not save_success or not read_success:
        print("\n⚠️ Wykryto problemy z konfiguracją!")
        print("📋 Sprawdź logi powyżej, aby znaleźć szczegółowe informacje o problemach.")
        print("🔍 Upewnij się, że:")
        print("  - Pliki konfiguracyjne mają odpowiednie uprawnienia")
        print("  - Serwery API są uruchomione")
        print("  - Endpointy /api/mobile-config działają poprawnie")
        print("  - Logika zapisywania konfiguracji działa poprawnie")
        print("\n🛠️ Sugerowane rozwiązania:")
        print("  1. Sprawdź logi serwera podczas zapisywania konfiguracji")
        print("  2. Sprawdź uprawnienia do pliku config.py")
        print("  3. Upewnij się, że serwery działają na portach 8000, 8002 i 8080")
        print("  4. Upewnij się, że jesteś zalogowany jako administrator")
    else:
        print("\n✅ Wszystkie testy przeszły pomyślnie!")
    
    return 0 if save_success and read_success else 1

if __name__ == "__main__":
    sys.exit(main())
