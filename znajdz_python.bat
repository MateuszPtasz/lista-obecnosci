@echo off
echo ======================================================
echo Wyszukiwanie instalacji Pythona w systemie
echo ======================================================
echo.

echo Sprawdzanie zmiennych środowiskowych...
echo PATH: %PATH%
echo.

echo Wyszukiwanie plików wykonywalnych Python...
where python
where python3
where py
echo.

echo Sprawdzanie typowych lokalizacji...
if exist "C:\Python*" dir "C:\Python*" /B
if exist "C:\Program Files\Python*" dir "C:\Program Files\Python*" /B
if exist "C:\Program Files (x86)\Python*" dir "C:\Program Files (x86)\Python*" /B
if exist "%LOCALAPPDATA%\Programs\Python" dir "%LOCALAPPDATA%\Programs\Python" /B /S

echo.
echo ======================================================
echo Sprawdzanie środowiska wirtualnego
echo ======================================================
echo.

if exist "venv" (
    echo Środowisko wirtualne istnieje:
    dir venv\Scripts\*.exe
) else (
    echo Nie znaleziono środowiska wirtualnego w katalogu projektu.
)

echo.
echo ======================================================
echo Skrypt diagnostyczny
echo ======================================================

pause
