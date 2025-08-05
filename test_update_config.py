import requests
import json
from datetime import datetime

def login():
    """Logowanie jako admin"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post("http://localhost:8000/api/login", json=login_data)
    if response.status_code == 200:
        print("✅ Logowanie udane!")
        return response.cookies
    else:
        print(f"❌ Błąd logowania: {response.status_code} - {response.text}")
        return None

def update_config(cookies):
    """Aktualizacja konfiguracji mobilnej"""
    # Generowanie wersji konfiguracji
    now = datetime.now()
    new_version = now.strftime("%Y%m%d-%H%M%S")
    
    # Dane konfiguracyjne
    config_data = {
        "APP_VERSION_INFO": {
            "current_version": "1.0.5",
            "minimum_version": "1.0.0",
            "update_required": False,
            "update_message": "Dostępna nowa wersja aplikacji z ulepszeniami!",
            "play_store_url": "https://play.google.com/store/apps/details?id=com.example.lista_obecnosci",
            "update_features": ["Funkcja 1", "Funkcja 2"]
        },
        "MOBILE_APP_CONFIG": {
            "timer_enabled": True,
            "daily_stats": True,
            "monthly_stats": True,
            "field_blocking": False, # Zmieniono na False
            "gps_verification": False,
            "widget_support": False,
            "notifications": False,
            "offline_mode": False,
            "debug_mode": True,
            "auto_updates": False,
            "forceUpdate": False,
        }
    }
    
    # Wysłanie żądania
    response = requests.post("http://localhost:8000/mobile-config", json=config_data, cookies=cookies)
    if response.status_code == 200:
        print(f"✅ Aktualizacja konfiguracji udana!")
        print(f"Odpowiedź: {response.json()}")
        return True
    else:
        print(f"❌ Błąd aktualizacji konfiguracji: {response.status_code} - {response.text}")
        return False

def get_config():
    """Pobranie aktualnej konfiguracji"""
    response = requests.get("http://localhost:8000/api/mobile-config")
    if response.status_code == 200:
        config = response.json()
        print("=== AKTUALNA KONFIGURACJA MOBILNA ===")
        print(json.dumps(config, indent=4, ensure_ascii=False))
        print("\n=== SZCZEGÓŁY CHECKBOXÓW ===")
        for key, value in config["config"].items():
            if isinstance(value, bool):
                print(f"{key}: {value}")
        return True
    else:
        print(f"❌ Błąd pobierania konfiguracji: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    print("=== TEST AKTUALIZACJI I POBIERANIA KONFIGURACJI MOBILNEJ ===")
    print("=" * 60)
    
    # Logowanie
    print("1. Logowanie jako admin")
    cookies = login()
    if not cookies:
        exit(1)
    
    # Aktualizacja konfiguracji
    print("\n2. Aktualizacja konfiguracji mobilnej (field_blocking = False)")
    if not update_config(cookies):
        exit(1)
    
    # Pobieranie zaktualizowanej konfiguracji
    print("\n3. Pobieranie zaktualizowanej konfiguracji")
    get_config()
