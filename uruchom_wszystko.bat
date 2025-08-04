@echo off
echo ======================================================
echo Lista Obecności - Pełna diagnostyka i uruchomienie
echo ======================================================
echo.

REM Ustawienie zmiennych środowiskowych na podstawie configs/app_config.py
for /f "tokens=3" %%a in ('findstr "APP_PORT_MAIN =" configs\app_config.py') do set APP_PORT_MAIN=%%a
for /f "tokens=3" %%a in ('findstr "APP_PORT_ALT =" configs\app_config.py') do set APP_PORT_ALT=%%a
for /f "tokens=3 delims== " %%a in ('findstr "APP_DEFAULT_IP =" configs\app_config.py') do set APP_DEFAULT_IP=%%a

echo Wykryto konfigurację:
echo - Port główny: %APP_PORT_MAIN%
echo - Port alternatywny: %APP_PORT_ALT%
echo - Domyślne IP: %APP_DEFAULT_IP%
echo.

echo UWAGA: Wykryto problemy z automatycznym uruchomieniem.
echo Zostanie wyświetlona instrukcja ręcznego uruchomienia.
echo.

echo ======================================================
echo INSTRUKCJA RĘCZNEGO URUCHOMIENIA SERWERÓW
echo ======================================================
echo 1. Otwórz nowy terminal i przejdź do katalogu projektu:
echo    cd m:\Programowanie\lista_obecnosci                
echo                    deactivate
echo.
echo 2. Aktywuj środowisko wirtualne:
echo    .\venv_new\Scripts\activate
echo.
echo 3. Uruchom serwer API na porcie głównym:
echo    .\venv_new\Scripts\python.exe main.py
echo    uvicorn main:app --host 0.0.0.0 --port %APP_PORT_MAIN%
echo    python -m uvicorn main:app --host 0.0.0.0
echo.
echo 4. Otwórz drugi terminal i powtórz kroki 1 i 2
echo.
echo 5. Uruchom serwer API na porcie alternatywnym:
echo    .\venv_new\Scripts\python.exe server_alt_port.py
echo    uvicorn main:app --host 0.0.0.0 --port %APP_PORT_ALT%
echo.

echo ======================================================
echo INSTRUKCJA RĘCZNEGO BUDOWANIA APLIKACJI MOBILNEJ
echo ======================================================
echo 1. Otwórz nowy terminal i przejdź do katalogu aplikacji:
echo    cd m:\Programowanie\lista_obecnosci\mobile_app
echo.
echo 2. Pobierz zależności:
echo    flutter pub get
echo.
echo 3. Zbuduj aplikację:
echo    flutter build apk --debug
echo.
echo 4. Skopiuj plik APK:
echo    copy build\app\outputs\flutter-apk\app-debug.apk ..\lista-obecnosci-app-debug.apk
echo.

echo ======================================================
echo INSTRUKCJA RĘCZNEGO URUCHOMIENIA DIAGNOSTYKI
echo ======================================================
echo 1. Po uruchomieniu serwerów otwórz nowy terminal
echo 2. Aktywuj środowisko wirtualne:
echo    .\venv_new\Scripts\activate
echo.
echo 3. Uruchom skrypty diagnostyczne:
echo    python test_api_connection.py
echo    python test_mobile_api.py --all-tests
echo.

echo ======================================================
echo INSTRUKCJA DIAGNOSTYKI APLIKACJI MOBILNEJ
echo ======================================================
echo 1. Sprawdź uprawnienia aplikacji w ustawieniach telefonu:
echo    Ustawienia → Aplikacje → Lista Obecności → Uprawnienia
echo    Upewnij się, że włączone są uprawnienia:
echo    - Internet (kluczowe!)
echo    - Lokalizacja (jeśli wymagana)
echo.
echo 2. Sprawdź czy telefon nie jest w trybie oszczędzania energii
echo    Wyłącz tryb oszczędzania baterii dla aplikacji.
echo.
echo 3. Upewnij się, że telefon ma dostęp do sieci WiFi
echo    i jest w tej samej sieci lokalnej co serwer.
echo.
echo 4. Sprawdź czy aplikacja nie ma blokad firewalla:
echo    Spróbuj wyłączyć na chwilę zaporę sieciową na telefonie.
echo.
echo 5. Upewnij się, że w aplikacji używany jest prawidłowy adres IP
echo    serwera. Adres lokalny tego komputera to najprawdopodobniej:
echo    ipconfig | findstr IPv4
echo.

echo ======================================================
echo DOSTĘPNE SKRYPTY DIAGNOSTYCZNE
echo ======================================================
echo 1. Diagnostyka konfiguracji aplikacji mobilnej:
echo    diagnoza_konfiguracji.bat
echo    - Sprawdza poprawność pliku konfiguracyjnego
echo    - Testuje dostęp do endpointów konfiguracji
echo.
echo 2. Test uprawnień do plików konfiguracyjnych:
echo    test_permissions.bat
echo    - Sprawdza czy procesy mają uprawnienia do zapisu
echo    - Testuje możliwość modyfikacji plików konfiguracyjnych
echo.
echo 3. Test połączeń API:
echo    test_api_connection.py
echo    - Sprawdza czy serwery API są dostępne
echo    - Testuje poszczególne endpointy
echo.
echo 4. Pełna diagnostyka API mobilnego:
echo    test_mobile_api.py --all-tests
echo    - Kompleksowe testy wszystkich funkcji API
echo.

echo ======================================================
echo DODATKOWE INFORMACJE
echo ======================================================
echo Problemy z uruchomieniem mogą wynikać z:
echo - Niepoprawnej ścieżki do interpretera Python w środowisku wirtualnym
echo - Brakujących pakietów (fastapi, uvicorn, httpx)
echo - Konfliktu portów (8000, 8002)
echo - Blokad firewalla w systemie Windows lub na urządzeniu mobilnym
echo.
echo Aby zainstalować wymagane pakiety:
echo .\venv_new\Scripts\pip.exe install fastapi uvicorn sqlalchemy httpx
echo.
echo Jeśli nadal występują problemy, uruchom serwer na innym porcie:
echo python main.py --port 8888
echo.

echo ======================================================
echo Pełna dokumentacja w pliku:
echo DOCS\INSTRUKCJA_URUCHOMIENIA_SYSTEMU.md
echo ======================================================

pause
