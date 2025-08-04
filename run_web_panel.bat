@echo off
echo Uruchamianie panelu webowego na porcie 8002...

REM Sprawdzenie, czy uruchamiamy z VS Code Terminal
if "%TERM_PROGRAM%"=="vscode" (
    echo Wykryto terminal VS Code - uruchamiam w tym samym oknie
    python run_web_panel.py
) else (
    REM Uruchamianie w osobnym oknie, jeśli nie jest to terminal VS Code
    echo Uruchamiam w nowym oknie CMD
    python run_web_panel.py
)
