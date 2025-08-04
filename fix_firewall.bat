@echo off
title Lista Obecnosci - Dodawanie reguly firewall
echo.
echo ========================================
echo   LISTA OBECNOSCI - KONFIGURACJA
echo ========================================
echo.
echo Dodawanie regul Windows Firewall...
echo.

REM Sprawdz czy ma uprawnienia administratora
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Uprawnienia administratora: OK
) else (
    echo [ERROR] Ten skrypt wymaga uprawnien administratora!
    echo Kliknij prawym przyciskiem i wybierz "Uruchom jako administrator"
    echo.
    pause
    exit /b 1
)

REM Uruchom skrypt PowerShell, który odczyta konfigurację portów
echo.
echo Uruchamianie konfiguracji firewalla...
powershell.exe -ExecutionPolicy Bypass -File "%~dp0add_firewall_rule.ps1"

echo.
echo ========================================
echo Nacisnij dowolny klawisz aby zamknac...
pause >nul
