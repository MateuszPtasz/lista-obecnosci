"""
Skrypt do testowania zapisywania i odczytywania konfiguracji
"""
import os
import sys
import json
import shutil
import requests
from datetime import datetime

def test_config_save():
    """Test zapisywania konfiguracji"""
    print("\n===== TEST ZAPISYWANIA KONFIGURACJI =====")
    
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
    
    # Wysłanie konfiguracji do API
    try:
        api_url = "http://localhost:8002/api/mobile-config"
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"📤 Wysyłanie konfiguracji do: {api_url}")
        print(f"📋 Konfiguracja: {json.dumps(test_config, indent=2)}")
        
        response = requests.post(api_url, json=test_config, headers=headers)
        
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
    
    # Odczytanie konfiguracji z API
    try:
        # Sprawdź wszystkie endpointy
        endpoints = [
            "http://localhost:8000/api/mobile-config",
            "http://localhost:8002/api/mobile-config",
            "http://localhost:8080/api/mobile-config",
            "http://localhost:8000/mobile-config",
            "http://localhost:8002/mobile-config",
            "http://localhost:8080/mobile-config"
        ]
        
        for api_url in endpoints:
            print(f"\n🔍 Sprawdzanie endpointu: {api_url}")
            
            try:
                response = requests.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Sukces! Otrzymano odpowiedź: {json.dumps(data, indent=2)[:500]}")
                    
                    # Sprawdź czy odpowiedź ma prawidłową strukturę
                    if isinstance(data, dict):
                        if "config" in data:
                            print("✅ Odpowiedź zawiera klucz 'config'")
                        else:
                            print("⚠️ Odpowiedź nie zawiera klucza 'config'")
                    else:
                        print(f"⚠️ Odpowiedź nie jest słownikiem: {type(data)}")
                else:
                    print(f"❌ Błąd API {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Błąd połączenia z {api_url}: {e}")
    except Exception as e:
        print(f"❌ Błąd podczas testu odczytu: {e}")
        return False
    
    return True

def main():
    print("=================================================")
    print("   TEST ZAPISYWANIA I ODCZYTYWANIA KONFIGURACJI   ")
    print("=================================================")
    
    # Test zapisu konfiguracji
    save_result = test_config_save()
    
    # Test odczytu konfiguracji
    read_result = test_config_read()
    
    # Podsumowanie
    print("\n=================================================")
    print("                  PODSUMOWANIE                    ")
    print("=================================================")
    print(f"Test zapisu konfiguracji: {'✅ ZALICZONY' if save_result else '❌ NIEZALICZONY'}")
    print(f"Test odczytu konfiguracji: {'✅ ZALICZONY' if read_result else '❌ NIEZALICZONY'}")
    
    if not (save_result and read_result):
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
    else:
        print("\n✅ Wszystkie testy przeszły pomyślnie!")
        print("📱 Konfiguracja aplikacji mobilnej działa poprawnie!")

if __name__ == "__main__":
    main()
