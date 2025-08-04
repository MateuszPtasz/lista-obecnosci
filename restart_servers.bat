@echo off
echo ======================================================
echo Restart serwerów Lista Obecności
echo ======================================================
echo.

echo Zatrzymywanie istniejących procesów serwera...
taskkill /F /IM python.exe /T 2>nul

echo.
echo Czyszczenie plików tymczasowych...
del /Q /F *.pyc 2>nul
del /Q /F __pycache__\*.pyc 2>nul

echo.
echo Uruchamianie serwera API (port 8000)...
start "API Server - Port 8000" cmd /c "python main.py --port 8000"

echo.
echo Uruchamianie zapasowego serwera API (port 8002)...
start "API Server - Port 8002" cmd /c "python main.py --port 8002"

echo.
echo ======================================================
echo Serwery zostały zrestartowane!
echo ======================================================
echo Serwer główny:    http://localhost:8000
echo Serwer zapasowy:  http://localhost:8002
echo.
echo Aby sprawdzić status serwerów, użyj skryptu: diagnostyka_api.bat
echo.

pause
