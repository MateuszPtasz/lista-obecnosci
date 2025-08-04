# Skrypt diagnostyczny do sprawdzania instalacji Pythona
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "     Diagnostyka instalacji Pythona" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Sprawdzenie zmiennej PATH
Write-Host "Sprawdzanie ścieżek w zmiennej PATH:" -ForegroundColor Yellow
$env:PATH -split ';' | Where-Object { $_ -like "*python*" -or $_ -like "*Python*" }
Write-Host ""

# Wyszukiwanie Python w całym systemie
Write-Host "Szukanie plików python.exe w systemie (może trwać kilka minut):" -ForegroundColor Yellow
try {
    $pythonPaths = Get-ChildItem -Path "C:\" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue -Force | Select-Object -First 10
    $pythonPaths | ForEach-Object { Write-Host $_.FullName }
} catch {
    Write-Host "Wystąpił błąd podczas szukania: $_" -ForegroundColor Red
}
Write-Host ""

# Sprawdzenie środowiska wirtualnego
Write-Host "Sprawdzanie środowiska wirtualnego:" -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Środowisko wirtualne znalezione." -ForegroundColor Green
    if (Test-Path "venv\Scripts\python.exe") {
        Write-Host "Python w środowisku wirtualnym: venv\Scripts\python.exe" -ForegroundColor Green
    } else {
        Write-Host "Nie znaleziono python.exe w środowisku wirtualnym!" -ForegroundColor Red
        Get-ChildItem "venv\Scripts\" -Filter "*.exe"
    }
} else {
    Write-Host "Brak środowiska wirtualnego w projekcie." -ForegroundColor Red
}

# Rozwiązanie problemu
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "     Proponowane rozwiązanie" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "1. Pobierz instalator Python 3.10 ze strony: https://www.python.org/downloads/release/python-3109/"
Write-Host "2. Zainstaluj Python bezpośrednio w folderze projektu:"
Write-Host "   python-3.10.9-amd64.exe /quiet InstallAllUsers=0 PrependPath=0 TargetDir=C:\path\to\project\python_local"
Write-Host "3. Utwórz nowe środowisko wirtualne przy pomocy lokalnego Pythona:"
Write-Host "   C:\path\to\project\python_local\python.exe -m venv venv_new"
Write-Host "4. Aktywuj nowe środowisko:"
Write-Host "   .\venv_new\Scripts\activate"
Write-Host "5. Zainstaluj wymagane pakiety:"
Write-Host "   .\venv_new\Scripts\pip.exe install fastapi uvicorn sqlalchemy httpx requests"
Write-Host ""
Write-Host "Naciśnij dowolny klawisz, aby kontynuować..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
