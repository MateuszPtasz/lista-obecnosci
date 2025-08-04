@echo off
echo ======================================================
echo Narzędzie diagnostyczne dla Lista Obecności API
echo ======================================================

echo Aktywacja środowiska wirtualnego...
call venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo Błąd: Nie można aktywować środowiska wirtualnego!
    echo Sprawdź, czy folder venv istnieje i czy jest poprawnie skonfigurowany.
    echo.
    echo Tworzę nowe środowisko wirtualne...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Sprawdzenie zainstalowanych pakietów
echo Sprawdzanie wymaganych pakietów...
pip show requests > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalowanie pakietu requests...
    pip install requests
) else (
    echo Pakiet requests jest już zainstalowany.
)

echo.
echo ======================================================
echo Uruchamianie diagnostyki połączenia...
echo ======================================================
echo.

.\venv\Scripts\python.exe test_api_connection.py

echo.
echo ======================================================
echo Diagnostyka zakończona.
echo ======================================================
echo.
echo Jeśli widzisz problemy z połączeniem:
echo 1. Upewnij się, że serwer API jest uruchomiony
echo 2. Sprawdź ustawienia firewalla
echo 3. Sprawdź czy porty 8000 i 8002 są otwarte
echo 4. Sprawdź plik config.py dla konfiguracji API
echo.

pause
