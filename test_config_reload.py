"""
Skrypt do testowania przeładowywania konfiguracji
"""
import sys
import importlib
import time

def test_config_reload():
    """Test przeładowywania konfiguracji"""
    print("\n===== TEST PRZEŁADOWYWANIA KONFIGURACJI =====")
    
    # 1. Sprawdzenie początkowej wartości
    print("\n1. Sprawdzenie początkowej wartości konfiguracji:")
    try:
        import config
        print(f"   Konfiguracja przed modyfikacją:")
        print(f"   - notifications: {config.MOBILE_APP_CONFIG.get('notifications')}")
        print(f"   - test_timestamp: {config.MOBILE_APP_CONFIG.get('test_timestamp', 'nie ustawiono')}")
        initial_value = config.MOBILE_APP_CONFIG.get('notifications')
    except ImportError:
        print("   ❌ Nie można zaimportować modułu config!")
        return False
    
    # 2. Modyfikacja pliku konfiguracyjnego
    print("\n2. Modyfikacja pliku konfiguracyjnego:")
    try:
        import os
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generuj nowy znacznik czasu
        new_timestamp = f"test_reload_{int(time.time())}"
        
        # Sprawdź czy wartość notifications jest obecnie True czy False
        new_notifications_value = not initial_value
        
        print(f"   - Zmiana notifications z {initial_value} na {new_notifications_value}")
        print(f"   - Ustawienie test_timestamp na {new_timestamp}")
        
        # Zamień wartość notifications
        if '"notifications": True' in content:
            content = content.replace('"notifications": True', '"notifications": False')
        elif '"notifications": False' in content:
            content = content.replace('"notifications": False', '"notifications": True')
        else:
            print("   ❌ Nie znaleziono parametru notifications w pliku konfiguracyjnym!")
        
        # Dodaj lub zaktualizuj test_timestamp
        if '"test_timestamp":' in content:
            import re
            content = re.sub(
                r'"test_timestamp": "[^"]+"', 
                f'"test_timestamp": "{new_timestamp}"', 
                content
            )
        else:
            # Dodaj przed ostatnią linią w MOBILE_APP_CONFIG
            pos = content.find("}")
            if pos > 0:
                content = content[:pos] + f'    "test_timestamp": "{new_timestamp}",\n' + content[pos:]
        
        # Zapisz zmodyfikowany plik
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Plik konfiguracyjny został zmodyfikowany")
    except Exception as e:
        print(f"   ❌ Błąd podczas modyfikacji pliku: {e}")
        return False
    
    # 3. Ponowny import bez przeładowania
    print("\n3. Ponowny import bez przeładowania:")
    try:
        import config as config2
        print(f"   Konfiguracja po modyfikacji (bez przeładowania):")
        print(f"   - notifications: {config2.MOBILE_APP_CONFIG.get('notifications')}")
        print(f"   - test_timestamp: {config2.MOBILE_APP_CONFIG.get('test_timestamp', 'nie ustawiono')}")
        
        # Sprawdź czy wartości się zmieniły
        if config2.MOBILE_APP_CONFIG.get('notifications') == initial_value:
            print("   ⚠️ Wartość notifications nie zmieniła się - buforowanie modułu aktywne!")
        else:
            print("   ✅ Wartość notifications została zaktualizowana bez przeładowania")
            
        if config2.MOBILE_APP_CONFIG.get('test_timestamp') == new_timestamp:
            print("   ✅ Wartość test_timestamp została zaktualizowana bez przeładowania")
        else:
            print("   ⚠️ Wartość test_timestamp nie zmieniła się - buforowanie modułu aktywne!")
    except ImportError:
        print("   ❌ Nie można zaimportować modułu config!")
        return False
    
    # 4. Import z wymuszonym przeładowaniem
    print("\n4. Import z wymuszonym przeładowaniem:")
    try:
        # Usuń moduł z pamięci podręcznej
        if 'config' in sys.modules:
            print("   Usuwanie modułu config z pamięci podręcznej...")
            del sys.modules['config']
        
        # Zaimportuj ponownie
        import config as config3
        importlib.reload(config3)
        
        print(f"   Konfiguracja po modyfikacji (z przeładowaniem):")
        print(f"   - notifications: {config3.MOBILE_APP_CONFIG.get('notifications')}")
        print(f"   - test_timestamp: {config3.MOBILE_APP_CONFIG.get('test_timestamp', 'nie ustawiono')}")
        
        # Sprawdź czy wartości się zmieniły
        if config3.MOBILE_APP_CONFIG.get('notifications') == new_notifications_value:
            print("   ✅ Wartość notifications została zaktualizowana po przeładowaniu")
        else:
            print("   ❌ Wartość notifications nie zmieniła się mimo przeładowania!")
            
        if config3.MOBILE_APP_CONFIG.get('test_timestamp') == new_timestamp:
            print("   ✅ Wartość test_timestamp została zaktualizowana po przeładowaniu")
        else:
            print("   ❌ Wartość test_timestamp nie zmieniła się mimo przeładowania!")
    except ImportError:
        print("   ❌ Nie można zaimportować modułu config!")
        return False
    
    # 5. Testowanie z funkcją pomocniczą
    print("\n5. Testowanie z funkcją pomocniczą:")
    def reload_config():
        if 'config' in sys.modules:
            del sys.modules['config']
        import config as reloaded_config
        importlib.reload(reloaded_config)
        return reloaded_config.MOBILE_APP_CONFIG
    
    reloaded_config = reload_config()
    print(f"   Konfiguracja po wywołaniu funkcji reload_config():")
    print(f"   - notifications: {reloaded_config.get('notifications')}")
    print(f"   - test_timestamp: {reloaded_config.get('test_timestamp', 'nie ustawiono')}")
    
    if reloaded_config.get('notifications') == new_notifications_value:
        print("   ✅ Wartość notifications została poprawnie załadowana przez funkcję")
    else:
        print("   ❌ Funkcja reload_config() nie załadowała prawidłowej wartości notifications!")
    
    return True

if __name__ == "__main__":
    test_config_reload()
