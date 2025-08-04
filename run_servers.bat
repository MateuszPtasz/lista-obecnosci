@echo off
echo Zatrzymywanie uruchomionych serwerow Python...
taskkill /F /IM python.exe /T >nul 2>nul

echo Uruchamianie serwerow API na porcie 8000...

REM Sprawdzenie, czy uruchamiamy z VS Code Terminal
if "%TERM_PROGRAM%"=="vscode" (
    echo Wykryto terminal VS Code - uruchamiam w tym samym oknie
    python main.py
) else (
    REM Uruchamianie w osobnym oknie, jeśli nie jest to terminal VS Code
    echo Uruchamiam w nowym oknie CMD
    python main.py
)
