@echo off
echo ===================================================
echo Uruchamianie serwerow aplikacji Lista Obecnosci
echo ===================================================

REM Uruchamiamy serwer glowny w nowym oknie
start powershell.exe -Command "python main.py"

REM Uruchamiamy serwer alternatywny w nowym oknie
start powershell.exe -Command "python server_alt_port.py"

echo.
echo Serwery uruchomione! Pamietaj o konfiguracji firewalla.
echo Zobacz plik FIREWALL_INSTRUKCJA.md aby dowiedziec sie wiecej.
echo.
echo Wcisnij dowolny klawisz, aby zamknac to okno...
pause > nul
