import requests
import json

def get_mobile_config():
    """Pobierz konfigurację z serwera"""
    try:
        response = requests.get("http://localhost:8000/api/mobile-config")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Błąd: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Wyjątek: {e}")
        return None

if __name__ == "__main__":
    config = get_mobile_config()
    if config:
        print("=== AKTUALNA KONFIGURACJA MOBILNA ===")
        print(json.dumps(config, indent=4, ensure_ascii=False))
        print("\n=== SZCZEGÓŁY CHECKBOXÓW ===")
        for key, value in config["config"].items():
            if isinstance(value, bool):
                print(f"{key}: {value}")
    else:
        print("Nie udało się pobrać konfiguracji")
