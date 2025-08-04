@echo off
echo ===================================================
echo     TEST ZAPISYWANIA I ODCZYTYWANIA KONFIGURACJI
echo ===================================================
echo.

REM Tworzymy kopię pliku konfiguracyjnego przed testem
echo Tworzenie kopii zapasowej pliku config.py...
copy config.py config_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.py >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Kopia zapasowa utworzona pomyslnie.
) else (
    echo [WARN] Nie mozna utworzyc kopii zapasowej. Kontynuuje bez niej...
)

REM Wykrywanie środowiska wirtualnego
echo Wykrywanie środowiska wirtualnego...
if exist venv_new\Scripts\activate (
    echo [INFO] Używam środowiska wirtualnego venv_new...
    call venv_new\Scripts\activate && python test_config_save.py
) else if exist venv\Scripts\activate (
    echo [INFO] Używam środowiska wirtualnego venv...
    call venv\Scripts\activate && python test_config_save.py
) else (
    echo [INFO] Nie wykryto środowiska wirtualnego. Używam domyślnego Pythona...
    python test_config_save.py
)

echo.
echo ===================================================
echo Naciśnij dowolny klawisz, aby zamknąć to okno...
pause >nul
