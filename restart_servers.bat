@echo off
echo ======================================================
echo Restart serwerów Lista Obecności
echo ======================================================
echo.

echo Zatrzymywanie istniejących procesów serwera...
taskkill /F /FI "WINDOWTITLE eq *Lista Obecności*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *uvicorn*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *start_api_servers*" /T >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *API Server*" /T >nul 2>&1

echo.
echo Czyszczenie plików tymczasowych...
del /Q /F *.pyc 2>nul
del /Q /F __pycache__\*.pyc 2>nul

echo.
echo Aktywacja środowiska wirtualnego...
call .\.venv\Scripts\activate

echo.
echo Uruchamianie wszystkich serwerów używając skryptu start_api_servers.py...
start "Lista Obecności - Serwery API" cmd /c "python start_api_servers.py"

echo.
echo ======================================================
echo Serwery zostały zrestartowane!
echo ======================================================
echo Serwer główny:        http://localhost:8000
echo Serwer alternatywny:  http://localhost:8080
echo Serwer panelu:        http://localhost:8002
echo.
echo Aby sprawdzić status serwerów, użyj: curl http://localhost:8000/api/ping
echo.
echo UWAGA: Po wprowadzeniu zmian w plikach kodu, należy 
echo ponownie uruchomić ten skrypt, aby zmiany zostały zastosowane.
echo.

pause
