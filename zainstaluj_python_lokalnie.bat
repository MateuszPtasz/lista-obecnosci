@echo off
echo ======================================================
echo Instalacja Pythona w folderze projektu
echo ======================================================
echo.

echo Pobieranie instalatora Python 3.10...
curl -L -o python_installer.exe https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe

echo.
echo Instalowanie Pythona w folderze projektu...
python_installer.exe /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir=%~dp0python_local

echo.
echo Tworzenie nowego środowiska wirtualnego...
%~dp0python_local\python.exe -m venv venv_new

echo.
echo Aktywacja środowiska wirtualnego i instalacja pakietów...
call venv_new\Scripts\activate.bat
venv_new\Scripts\pip.exe install fastapi uvicorn sqlalchemy httpx requests

echo.
echo ======================================================
echo Instalacja zakończona!
echo ======================================================
echo.
echo Aby aktywować środowisko, użyj:
echo call venv_new\Scripts\activate.bat
echo.
echo Aby uruchomić serwer API, użyj:
echo venv_new\Scripts\python.exe main.py --port 8000
echo.

pause
