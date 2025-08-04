@echo off
echo ===================================================
echo Uruchamianie systemu Lista Obecnosci
echo ===================================================

REM Uruchamiamy serwer glowny w nowym oknie
start powershell.exe -Command "python main.py"

REM Uruchamiamy serwer alternatywny w nowym oknie
start powershell.exe -Command "python server_alt_port.py"

REM Uruchamiamy serwer panelu webowego w nowym oknie
start powershell.exe -Command "python -m uvicorn main:app --host 0.0.0.0 --port 8002"

echo.
echo Serwery uruchomione! Pamietaj o konfiguracji firewalla.
echo Zobacz plik FIREWALL_INSTRUKCJA.md aby dowiedziec sie wiecej.
echo.
echo Mozesz zamknac to okno, a serwery beda dzialac w tle.
echo Aby zatrzymac serwery, zamknij otwarte okna powershell.
echo.
