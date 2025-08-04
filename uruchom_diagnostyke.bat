@echo off
echo ======================================================
echo Lista Obecności - Kompleksowa diagnostyka systemu
echo ======================================================
echo.

REM Ustawienie kolorów
color 0A

REM Uruchamianie diagnostyki konfiguracji
echo [1/4] Diagnostyka konfiguracji aplikacji mobilnej...
echo ======================================================
call diagnoza_konfiguracji.bat
echo.

REM Test uprawnień do plików konfiguracyjnych
echo [2/4] Test uprawnień do plików konfiguracyjnych...
echo ======================================================
call test_permissions.bat
echo.

REM Test połączeń API
echo [3/4] Test połączeń API...
echo ======================================================
python test_api_connection.py
echo.

REM Test API mobilnego (tylko podstawowy test)
echo [4/4] Podstawowy test API mobilnego...
echo ======================================================
python test_mobile_api.py
echo.

echo ======================================================
echo Diagnostyka zakończona!
echo ======================================================
echo Pełne raporty i logi zostały zapisane w katalogu logs/
echo (Jeśli katalog nie istnieje, oznacza to że nie wystąpiły błędy)
echo.
echo Aby uruchomić pełne testy API mobilnego, użyj:
echo python test_mobile_api.py --all-tests
echo.

pause
