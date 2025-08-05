"""
Test logowania i aktualizacji konfiguracji mobilnej
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/login"
CONFIG_ENDPOINT = "/api/mobile-config"
SESSION = requests.Session()  # Używamy sesji, aby zachować ciasteczka

def test_login():
    """Test logowania na konto administratora"""
    print("=== Test logowania ===")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"Logowanie jako: {login_data['username']}")
    
    try:
        response = SESSION.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}", 
            json=login_data
        )
        
        if response.status_code == 200:
            print("✅ Logowanie udane!")
            print(f"Odpowiedź: {response.json()}")
            return True
        else:
            print(f"❌ Błąd logowania! Kod: {response.status_code}")
            print(f"Treść odpowiedzi: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Wyjątek podczas logowania: {str(e)}")
        return False

def test_mobile_config_update():
    """Test aktualizacji konfiguracji aplikacji mobilnej"""
    print("\n=== Test aktualizacji konfiguracji mobilnej ===")
    
    # Generowanie nowej wersji konfiguracji
    now = datetime.now()
    new_config_version = now.strftime("%Y%m%d-%H%M%S")
    
    # Przygotowanie danych konfiguracyjnych
    config_data = {
        "APP_VERSION_INFO": {
            "current_version": "1.0.0",
            "minimum_version": "1.0.0",
            "update_required": False,
            "update_message": "Dostępna nowa wersja aplikacji z ulepszeniami!",
            "play_store_url": "https://play.google.com/store/apps/details?id=com.example.lista_obecnosci",
            "update_features": ["Nowy system konfiguracji zdalnej", "Ulepszony timer pracy", "Poprawki błędów i optymalizacja"]
        },
        "MOBILE_APP_CONFIG": {
            "timer_enabled": True,
            "daily_stats": True,
            "monthly_stats": True,
            "show_departments": True,
            "offline_mode_enabled": True,
            "sync_interval_minutes": 15
        },
        "CONFIG_VERSION": new_config_version
    }
    
    print(f"Wysyłanie nowej konfiguracji z wersją: {new_config_version}")
    
    try:
        response = SESSION.post(
            f"{BASE_URL}{CONFIG_ENDPOINT}", 
            json=config_data
        )
        
        if response.status_code == 200:
            print("✅ Aktualizacja konfiguracji udana!")
            print(f"Odpowiedź: {response.json()}")
            return True
        else:
            print(f"❌ Błąd aktualizacji konfiguracji! Kod: {response.status_code}")
            print(f"Treść odpowiedzi: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Wyjątek podczas aktualizacji konfiguracji: {str(e)}")
        return False

def main():
    """Główna funkcja testowa"""
    print("=== TEST LOGOWANIA I AKTUALIZACJI KONFIGURACJI ===")
    print("=" * 45)
    
    # Logowanie
    if not test_login():
        print("\n❌ Test zakończony niepowodzeniem na etapie logowania")
        return
        
    # Poczekaj chwilę przed wysłaniem aktualizacji konfiguracji
    time.sleep(1)
    
    # Aktualizacja konfiguracji
    if not test_mobile_config_update():
        print("\n❌ Test zakończony niepowodzeniem na etapie aktualizacji konfiguracji")
        return
    
    print("\n✅ Test zakończony pomyślnie!")
    print("=" * 45)

if __name__ == "__main__":
    main()
