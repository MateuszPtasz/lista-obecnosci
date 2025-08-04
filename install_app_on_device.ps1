# Skrypt do instalacji aplikacji na urządzeniu testowym przez ADB
# Wymaga zainstalowanego Android SDK Platform Tools
# Autor: GitHub Copilot, 2025-08-03

# Znajdź najnowszy plik APK w głównym katalogu
$newestAppFile = Get-ChildItem -Path "." -Filter "lista-obecnosci-app-*.apk" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Ścieżki do plików APK (sprawdzane po kolei)
$apkPaths = @()

# Najpierw sprawdź najnowszy plik z numerem porządkowym
if ($newestAppFile) {
    $apkPaths += $newestAppFile.Name
}

# Dodaj pozostałe możliwe lokalizacje
$apkPaths += @(
    "lista-obecnosci-app.apk",  # Stary format w głównym katalogu (dla kompatybilności)
    "mobile_app\releases\lista-obecnosci-app-FIXED-API-20250802.apk",  # Stary format w katalogu releases
    "mobile_app\build\app\outputs\flutter-apk\app-release.apk"  # Oryginalny plik wygenerowany przez Flutter
)

# Znajdź pierwszy istniejący plik APK
$apkPath = $null
foreach ($path in $apkPaths) {
    if (Test-Path -Path $path) {
        $apkPath = $path
        break
    }
}

# Sprawdź czy znaleziono plik APK
if ($null -eq $apkPath) {
    Write-Host "BŁĄD: Nie znaleziono pliku APK w żadnej z oczekiwanych lokalizacji:" -ForegroundColor Red
    foreach ($path in $apkPaths) {
        Write-Host "  - $path" -ForegroundColor Red
    }
    Write-Host "Upewnij się, że aplikacja została zbudowana poprawnie." -ForegroundColor Yellow
    exit 1
}

Write-Host "Znaleziono plik APK: $apkPath" -ForegroundColor Green

# Sprawdź czy urządzenie jest podłączone
Write-Host "Sprawdzanie podłączonych urządzeń..." -ForegroundColor Cyan
$devices = adb devices

if ($devices -match "device$") {
    Write-Host "Znaleziono urządzenie. Instalowanie aplikacji..." -ForegroundColor Green
    
    # Instalacja aplikacji
    Write-Host "Instalowanie $apkPath..." -ForegroundColor Yellow
    adb install -r $apkPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Aplikacja zainstalowana pomyślnie!" -ForegroundColor Green
        
        # Uruchomienie aplikacji
        $appPackage = "com.example.lista_obecnosci"
        $appActivity = "com.example.lista_obecnosci.MainActivity"
        
        Write-Host "Uruchamianie aplikacji..." -ForegroundColor Yellow
        adb shell am start -n "$appPackage/$appActivity"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Aplikacja uruchomiona pomyślnie!" -ForegroundColor Green
        } else {
            Write-Host "BŁĄD: Nie udało się uruchomić aplikacji." -ForegroundColor Red
        }
    } else {
        Write-Host "BŁĄD: Nie udało się zainstalować aplikacji." -ForegroundColor Red
    }
} else {
    Write-Host "BŁĄD: Nie znaleziono podłączonego urządzenia." -ForegroundColor Red
    Write-Host "Podłącz urządzenie przez USB i upewnij się, że USB Debugging jest włączony." -ForegroundColor Yellow
}
