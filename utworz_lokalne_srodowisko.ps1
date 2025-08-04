# Skrypt do tworzenia lokalnego środowiska Python
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "     Tworzenie lokalnego środowiska Python" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Ścieżka do folderu projektu
$projectPath = Get-Location

# Sprawdzenie, czy Python jest już zainstalowany
$pythonInstalled = $false
$pythonPath = ""

# Sprawdzenie typowych lokalizacji
$possiblePaths = @(
    "C:\Python310\python.exe",
    "C:\Python39\python.exe",
    "C:\Python38\python.exe",
    "C:\Program Files\Python310\python.exe",
    "C:\Program Files\Python39\python.exe",
    "C:\Program Files\Python38\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python38\python.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $pythonInstalled = $true
        $pythonPath = $path
        break
    }
}

if ($pythonInstalled) {
    Write-Host "Znaleziono Python w: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "Nie znaleziono Pythona w systemie." -ForegroundColor Yellow
    Write-Host "Czy chcesz pobrać i zainstalować Python 3.10? (T/N)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "T" -or $response -eq "t") {
        # Pobieranie i instalacja Python
        Write-Host "Pobieranie instalatora Python 3.10..." -ForegroundColor Yellow
        $installerPath = Join-Path $projectPath "python_installer.exe"
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe" -OutFile $installerPath
        
        # Tworzenie folderu na lokalną instalację
        $pythonLocalFolder = Join-Path $projectPath "python_local"
        if (-not (Test-Path $pythonLocalFolder)) {
            New-Item -Path $pythonLocalFolder -ItemType Directory
        }
        
        # Instalacja Python lokalnie
        Write-Host "Instalowanie Python w folderze: $pythonLocalFolder" -ForegroundColor Yellow
        Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=0", "Include_test=0", "TargetDir=$pythonLocalFolder" -Wait
        
        # Sprawdzenie czy instalacja się powiodła
        $pythonPath = Join-Path $pythonLocalFolder "python.exe"
        if (Test-Path $pythonPath) {
            Write-Host "Python został pomyślnie zainstalowany w: $pythonPath" -ForegroundColor Green
        } else {
            Write-Host "Instalacja Pythona nie powiodła się!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Instalacja anulowana przez użytkownika." -ForegroundColor Yellow
        exit 0
    }
}

# Tworzenie nowego środowiska wirtualnego
Write-Host ""
Write-Host "Tworzenie nowego środowiska wirtualnego..." -ForegroundColor Yellow
$venvPath = Join-Path $projectPath "venv_new"

# Usunięcie starego środowiska, jeśli istnieje
if (Test-Path $venvPath) {
    Write-Host "Usuwanie istniejącego środowiska wirtualnego..." -ForegroundColor Yellow
    Remove-Item -Path $venvPath -Recurse -Force
}

# Tworzenie nowego środowiska
& $pythonPath -m venv $venvPath

if (Test-Path (Join-Path $venvPath "Scripts\python.exe")) {
    Write-Host "Środowisko wirtualne zostało utworzone pomyślnie!" -ForegroundColor Green
    
    # Aktywacja środowiska i instalacja pakietów
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    Write-Host "Aktywacja środowiska wirtualnego..." -ForegroundColor Yellow
    & $activateScript
    
    $pipPath = Join-Path $venvPath "Scripts\pip.exe"
    Write-Host "Instalowanie wymaganych pakietów..." -ForegroundColor Yellow
    & $pipPath install fastapi uvicorn sqlalchemy httpx requests
    
    Write-Host ""
    Write-Host "====================================================" -ForegroundColor Cyan
    Write-Host "     Środowisko zostało skonfigurowane!" -ForegroundColor Cyan
    Write-Host "====================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Aby aktywować środowisko, użyj:" -ForegroundColor White
    Write-Host "   .\venv_new\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Aby uruchomić serwer API, użyj:" -ForegroundColor White
    Write-Host "   .\venv_new\Scripts\python.exe main.py --port 8000" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Tworzenie środowiska wirtualnego nie powiodło się!" -ForegroundColor Red
}

Write-Host "Naciśnij dowolny klawisz, aby kontynuować..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
