@echo off
echo ======================================================
echo Uruchamianie serwerów Lista Obecności w środowisku wirtualnym
echo ======================================================
echo.

echo Zatrzymywanie istniejących procesów serwera...
taskkill /F /IM python.exe /T 2>nul

echo.
echo Czyszczenie plików tymczasowych...
del /Q /F *.pyc 2>nul
del /Q /F __pycache__\*.pyc 2>nul

echo.
echo Aktywacja środowiska wirtualnego...
call venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo Błąd: Nie można aktywować środowiska wirtualnego!
    echo Sprawdź, czy folder venv istnieje i czy jest poprawnie skonfigurowany.
    echo.
    echo Tworzę nowe środowisko wirtualne...
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo Instaluję wymagane pakiety...
    pip install -r requirements.txt
)

echo.
echo Sprawdzanie wymaganych pakietów...
call venv\Scripts\activate.bat

pip show fastapi > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalowanie wymaganych pakietów dla API...
    pip install fastapi uvicorn sqlalchemy python-dotenv
)

echo.
echo Uruchamianie serwera API (port 8000) w środowisku wirtualnym...
start "API Server - Port 8000" cmd /k "call venv\Scripts\activate.bat && python main.py --port 8000"

echo.
echo Uruchamianie zapasowego serwera API (port 8002) w środowisku wirtualnym...
start "API Server - Port 8002" cmd /k "call venv\Scripts\activate.bat && python main.py --port 8002"

echo.
echo ======================================================
echo Serwery zostały uruchomione w środowisku wirtualnym!
echo ======================================================
echo Serwer główny:    http://localhost:8000
echo Serwer zapasowy:  http://localhost:8002
echo.
echo Aby sprawdzić status serwerów, użyj skryptu: diagnostyka_api.bat
echo.

pause
