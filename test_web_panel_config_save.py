"""
Skrypt do testowania zapisywania konfiguracji z poziomu panelu webowego
"""
import os
import sys
import json
import requests
from datetime import datetime

def test_web_panel_config_save():
    """Test zapisywania konfiguracji z poziomu panelu webowego"""
    print("\n===== TEST ZAPISYWANIA KONFIGURACJI Z POZIOMU PANELU WEBOWEGO =====")
    
    # Dane logowania administratora
    admin_username = "admin"
    admin_password = "admin123"
    
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
    
    # Pobierz aktualną konfigurację
    print("\n🔍 Pobieranie aktualnej konfiguracji...")
    try:
        config_url = "http://localhost:8002/api/mobile-config"
        config_response = session.get(config_url)
        
        if config_response.status_code != 200:
            print(f"❌ Błąd pobierania konfiguracji: {config_response.status_code} - {config_response.text}")
            return False
            
        current_config = config_response.json()
        print(f"✅ Pobrano aktualną konfigurację")
        
        # Pokaż aktualne wartości
        print("\n📊 Aktualna konfiguracja:")
        for key, value in current_config.get('config', {}).items():
            print(f"  - {key}: {value}")
            
    except Exception as e:
        print(f"❌ Błąd podczas pobierania konfiguracji: {e}")
        return False
    
    # Przygotuj nową konfigurację
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"\n🛠️ Przygotowywanie nowej konfiguracji (znacznik czasu: {timestamp})...")
    
    # Symuluj dane wysyłane przez frontend panelu webowego
    new_mobile_config = {
        "timer_enabled": True,
        "daily_stats": True, 
        "monthly_stats": True,
        "field_blocking": True,
        "gps_verification": False,  # Zmieniona wartość
        "widget_support": True,  # Zmieniona wartość
        "notifications": False,  # Zmieniona wartość
        "offline_mode": True,
        "debug_mode": True,
        "auto_updates": False,
        "forceUpdate": False,
        "test_timestamp": timestamp
    }
    
    # Stwórz prawidłową strukturę danych zgodną z oczekiwaną przez serwer
    new_config = {
        "MOBILE_APP_CONFIG": new_mobile_config
    }
    
    # Wyślij nową konfigurację
    print("\n📤 Wysyłanie nowej konfiguracji...")
    print(f"📋 Konfiguracja: {json.dumps(new_config, indent=2)}")
    
    try:
        update_response = session.post(config_url, json=new_config)
        
        if update_response.status_code != 200:
            print(f"❌ Błąd aktualizacji konfiguracji: {update_response.status_code} - {update_response.text}")
            return False
            
        update_result = update_response.json()
        print(f"✅ Konfiguracja zaktualizowana: {update_result}")
        
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania konfiguracji: {e}")
        return False
    
    # Sprawdź czy konfiguracja została zaktualizowana
    print("\n🔍 Sprawdzanie czy konfiguracja została zaktualizowana...")
    try:
        config_path = "config.py"
        if not os.path.exists(config_path):
            print(f"❌ Plik {config_path} nie istnieje!")
            return False
            
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
            
        # Sprawdzenie czy nasz znacznik czasu został dodany
        if timestamp in config_content:
            print(f"✅ Znaleziono testowy znacznik czasu w pliku: {timestamp}")
            print("✅ Konfiguracja została pomyślnie zaktualizowana!")
        else:
            print(f"❌ Nie znaleziono testowego znacznika czasu w pliku!")
            print("Aktualna zawartość pliku:")
            print("-------------------")
            print(config_content[:500] + "..." if len(config_content) > 500 else config_content)
            print("-------------------")
            return False
            
    except Exception as e:
        print(f"❌ Błąd podczas sprawdzania pliku konfiguracyjnego: {e}")
        return False
        
    # Pobierz konfigurację ponownie, aby sprawdzić czy zmiany są widoczne
    print("\n🔍 Pobieranie zaktualizowanej konfiguracji...")
    try:
        updated_response = session.get(config_url)
        
        if updated_response.status_code != 200:
            print(f"❌ Błąd pobierania zaktualizowanej konfiguracji: {updated_response.status_code} - {updated_response.text}")
            return False
            
        updated_config = updated_response.json()
        print(f"✅ Pobrano zaktualizowaną konfigurację")
        
        # Pokaż nowe wartości
        print("\n📊 Zaktualizowana konfiguracja:")
        for key, value in updated_config.get('config', {}).items():
            print(f"  - {key}: {value}")
            
        # Sprawdzenie czy zmiany zostały zastosowane
        config = updated_config.get('config', {})
        if (config.get('enable_location') == new_mobile_config.get('gps_verification') and
            config.get('notify_on_success') == new_mobile_config.get('notifications')):
            print("\n✅ Zmiany zostały pomyślnie zastosowane i są widoczne w konfiguracji!")
        else:
            print("\n❌ Zmiany nie zostały prawidłowo zastosowane lub nie są widoczne!")
            print("Oczekiwano:")
            print(f"  - enable_location: {new_mobile_config.get('gps_verification')}")
            print(f"  - notify_on_success: {new_mobile_config.get('notifications')}")
            print("Otrzymano:")
            print(f"  - enable_location: {config.get('enable_location')}")
            print(f"  - notify_on_success: {config.get('notify_on_success')}")
            
    except Exception as e:
        print(f"❌ Błąd podczas pobierania zaktualizowanej konfiguracji: {e}")
        return False
        
    return True

if __name__ == "__main__":
    if test_web_panel_config_save():
        print("\n✅ Test zakończony pomyślnie!")
        sys.exit(0)
    else:
        print("\n❌ Test zakończony niepowodzeniem!")
        sys.exit(1)
