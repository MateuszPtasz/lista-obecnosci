@echo off
echo ======================================================
echo Lista Obecności - Uruchamianie serwerów API
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

REM Sprawdź czy środowisko wirtualne istnieje
if exist venv_new\Scripts\activate (
    echo Znaleziono środowisko wirtualne: venv_new
    echo Uruchamiam serwery z użyciem venv_new...
    
    echo Uruchamianie głównego serwera API (port %APP_PORT_MAIN%)...
    start cmd /k "title Serwer Główny (PORT %APP_PORT_MAIN%) && call .\venv_new\Scripts\activate && python -m uvicorn main:app --host 0.0.0.0 --port %APP_PORT_MAIN%"
    
    echo Uruchamianie alternatywnego serwera API (port %APP_PORT_ALT%)...
    start cmd /k "title Serwer Alternatywny (PORT %APP_PORT_ALT%) && call .\venv_new\Scripts\activate && python -m uvicorn main:app --host 0.0.0.0 --port %APP_PORT_ALT%"
    
    echo Uruchamianie serwera panelu webowego (port 8002)...
    start cmd /k "title Serwer Panel Webowy (PORT 8002) && call .\venv_new\Scripts\activate && python -m uvicorn main:app --host 0.0.0.0 --port 8002"
) else (
    echo UWAGA: Nie znaleziono środowiska wirtualnego venv_new
    echo Używam systemowego Pythona...
    
    echo Uruchamianie głównego serwera API (port %APP_PORT_MAIN%)...
    start cmd /k "title Serwer Główny (PORT %APP_PORT_MAIN%) && python -m uvicorn main:app --host 0.0.0.0 --port %APP_PORT_MAIN%"
    
    echo Uruchamianie alternatywnego serwera API (port %APP_PORT_ALT%)...
    start cmd /k "title Serwer Alternatywny (PORT %APP_PORT_ALT%) && python -m uvicorn main:app --host 0.0.0.0 --port %APP_PORT_ALT%"
    
    echo Uruchamianie serwera panelu webowego (port 8002)...
    start cmd /k "title Serwer Panel Webowy (PORT 8002) && python -m uvicorn main:app --host 0.0.0.0 --port 8002"
)

echo ======================================================
echo Serwery uruchomione! Naciśnij dowolny klawisz, aby zamknąć to okno.
echo Aby zatrzymać serwery, zamknij otwarte okna cmd.
echo ======================================================
pause
