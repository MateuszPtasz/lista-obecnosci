"""
Narzędzie diagnostyczne dla konfiguracji aplikacji mobilnej
"""
import os
import re
import time
import datetime

def check_config_file():
    """Sprawdza plik config.py pod kątem poprawności i aktualności"""
    config_path = "config.py"
    
    # Sprawdź czy plik istnieje
    if not os.path.exists(config_path):
        print(f"BŁĄD: Plik {config_path} nie istnieje!")
        return False
        
    # Sprawdź uprawnienia do pliku
    try:
        # Sprawdź czy plik można odczytać
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✓ Plik {config_path} można odczytać")
        
        # Sprawdź czy plik można zapisać
        try:
            # Pobierz aktualny czas modyfikacji
            mod_time_before = os.path.getmtime(config_path)
            
            # Spróbuj dotknąć pliku
            with open(config_path, "a", encoding="utf-8") as f:
                pass
                
            # Sprawdź czy czas modyfikacji się zmienił
            mod_time_after = os.path.getmtime(config_path)
            if mod_time_after > mod_time_before:
                print(f"✓ Plik {config_path} można zapisać")
            else:
                print(f"⚠ Ostrzeżenie: Zapis do pliku {config_path} może nie działać prawidłowo")
        except Exception as e:
            print(f"⚠ Ostrzeżenie: Nie można zapisać do pliku {config_path}: {e}")
    except Exception as e:
        print(f"BŁĄD: Nie można odczytać pliku {config_path}: {e}")
        return False
    
    # Sprawdź zawartość pliku
    config_version_match = re.search(r'CONFIG_VERSION = "([^"]+)"', content)
    if not config_version_match:
        print("BŁĄD: Nie znaleziono CONFIG_VERSION w pliku konfiguracyjnym!")
        return False
    
    config_version = config_version_match.group(1)
    print(f"✓ Znaleziono CONFIG_VERSION: {config_version}")
    
    # Sprawdź czy MOBILE_APP_CONFIG istnieje
    if "MOBILE_APP_CONFIG" not in content:
        print("BŁĄD: Nie znaleziono MOBILE_APP_CONFIG w pliku konfiguracyjnym!")
        return False
    
    print("✓ Znaleziono MOBILE_APP_CONFIG")
    
    # Sprawdź czy APP_VERSION_INFO istnieje
    if "APP_VERSION_INFO" not in content:
        print("BŁĄD: Nie znaleziono APP_VERSION_INFO w pliku konfiguracyjnym!")
        return False
    
    print("✓ Znaleziono APP_VERSION_INFO")
    
    # Spróbuj zaimportować config.py
    try:
        import config
        print("✓ Moduł config.py można pomyślnie zaimportować")
        
        # Sprawdź wymagane zmienne
        if hasattr(config, "CONFIG_VERSION"):
            print(f"✓ CONFIG_VERSION: {config.CONFIG_VERSION}")
        else:
            print("BŁĄD: Brak zmiennej CONFIG_VERSION po zaimportowaniu!")
            
        if hasattr(config, "MOBILE_APP_CONFIG"):
            print(f"✓ MOBILE_APP_CONFIG zawiera {len(config.MOBILE_APP_CONFIG)} ustawień")
        else:
            print("BŁĄD: Brak zmiennej MOBILE_APP_CONFIG po zaimportowaniu!")
            
        if hasattr(config, "APP_VERSION_INFO"):
            print(f"✓ APP_VERSION_INFO znaleziono, wersja: {config.APP_VERSION_INFO.get('current_version', 'nieznana')}")
        else:
            print("BŁĄD: Brak zmiennej APP_VERSION_INFO po zaimportowaniu!")
            
    except Exception as e:
        print(f"BŁĄD: Nie można zaimportować config.py: {e}")
        return False
    
    # Test zapisu nowej wersji konfiguracji
    print("\n=== Test zapisu konfiguracji ===")
    try:
        # Utwórz kopię pliku
        backup_path = f"config_test_backup.py"
        import shutil
        shutil.copy(config_path, backup_path)
        print(f"✓ Utworzono kopię zapasową do {backup_path}")
        
        # Wygeneruj nową wersję
        new_version = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Odczytaj plik
        with open(config_path, "r", encoding="utf-8") as f:
            test_content = f.read()
            
        # Zastąp wersję
        test_content = re.sub(
            r'CONFIG_VERSION = "[^"]+"', 
            f'CONFIG_VERSION = "{new_version}"', 
            test_content
        )
        
        # Zapisz plik
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Weryfikacja zapisu
        time.sleep(1)  # Daj czas na zapisanie pliku
        with open(config_path, "r", encoding="utf-8") as f:
            verify_content = f.read()
        
        if new_version in verify_content:
            print(f"✓ Test zapisu udany: nowa wersja {new_version} została zapisana!")
        else:
            print(f"BŁĄD: Nie można zweryfikować zapisu nowej wersji!")
            
        # Przywróć kopię zapasową
        shutil.copy(backup_path, config_path)
        print("✓ Przywrócono oryginalną konfigurację")
        
        # Usuń kopię zapasową
        os.remove(backup_path)
        
    except Exception as e:
        print(f"BŁĄD podczas testu zapisu: {e}")
        # Spróbuj przywrócić kopię zapasową w przypadku błędu
        try:
            if os.path.exists(backup_path):
                shutil.copy(backup_path, config_path)
                print("✓ Przywrócono oryginalną konfigurację po błędzie")
        except:
            pass
        return False
    
    return True

def test_config_api_endpoints():
    """Testuje endpointy API związane z konfiguracją"""
    import requests
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/app-version",
        "/mobile-config",
        "/api/mobile-config"
    ]
    
    print("\n=== Test endpointów konfiguracji ===")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"Testowanie {url}...")
        
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✓ Endpoint {endpoint}: OK (200)")
                try:
                    data = response.json()
                    if endpoint == "/api/app-version" and "config_version" in data:
                        print(f"  ✓ config_version: {data['config_version']}")
                    elif "/mobile-config" in endpoint:
                        if "config" in data:
                            print(f"  ✓ Znaleziono obiekt konfiguracji")
                        elif "enable_location" in data:
                            print(f"  ⚠ Uwaga: Konfiguracja nie jest prawidłowo zagnieżdżona w obiekcie 'config'!")
                        else:
                            print(f"  ⚠ Nieoczekiwany format odpowiedzi!")
                except Exception as e:
                    print(f"  ⚠ Nie można sparsować odpowiedzi JSON: {e}")
            else:
                print(f"✗ Endpoint {endpoint}: BŁĄD ({response.status_code})")
        except Exception as e:
            print(f"✗ Endpoint {endpoint}: BŁĄD POŁĄCZENIA: {e}")

if __name__ == "__main__":
    print("=== Diagnostyka konfiguracji aplikacji mobilnej ===")
    print(f"Data i czas: {datetime.datetime.now()}")
    print("=" * 50)
    
    config_ok = check_config_file()
    
    if config_ok:
        print("\n✓ Plik konfiguracyjny jest poprawny i można go aktualizować")
        test_config_api_endpoints()
    else:
        print("\n✗ Plik konfiguracyjny ma problemy, które należy rozwiązać")
        
    print("\n=== Koniec diagnostyki ===")
