import sys
import time
from configs.app_config import APP_PORT_MAIN, APP_PORT_ALT, APP_DEFAULT_IP

print("Test konfiguracji aplikacji:")
print(f"- Port główny: {APP_PORT_MAIN}")
print(f"- Port alternatywny: {APP_PORT_ALT}")
print(f"- Adres IP: {APP_DEFAULT_IP}")

try:
    print("\nSprawdzanie importu z main.py...")
    from main import app
    print("✓ Import z main.py działa poprawnie!")
    
    print("\nSprawdzanie konfiguracji serwerów...")
    import uvicorn
    print("✓ Biblioteka uvicorn jest dostępna!")
    
    # Sprawdzenie czy main.py używa portów z konfiguracji
    import inspect
    import main
    main_src = inspect.getsource(main)
    
    if "APP_PORT_MAIN" in main_src and "configs.app_config" in main_src:
        print("✓ Główny plik main.py używa centralnej konfiguracji!")
    else:
        print("⚠ Uwaga: main.py może nie używać centralnej konfiguracji!")
        
    print("\nTest zakończony pomyślnie!")
    
except ImportError as e:
    print(f"❌ Błąd importu: {e}")
except Exception as e:
    print(f"❌ Błąd: {e}")
    
print("\nTest zakończony.")
