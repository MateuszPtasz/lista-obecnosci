# Skrypt do dodania reguly firewalla dla aplikacji Lista Obecnosci
# Uruchom ten plik jako Administrator!

# Wczytaj porty z pliku konfiguracyjnego Pythona
$configFile = Join-Path $PSScriptRoot "configs\app_config.py"
$configContent = Get-Content $configFile -Raw
$mainPortMatch = [regex]::Match($configContent, 'APP_PORT_MAIN\s*=\s*(\d+)')
$altPortMatch = [regex]::Match($configContent, 'APP_PORT_ALT\s*=\s*(\d+)')

if ($mainPortMatch.Success -and $altPortMatch.Success) {
    $mainPort = $mainPortMatch.Groups[1].Value
    $altPort = $altPortMatch.Groups[1].Value

    Write-Host "Znaleziono porty w konfiguracji: główny=$mainPort, alternatywny=$altPort" -ForegroundColor Cyan
} else {
    # Awaryjne wartości domyślne
    $mainPort = 8000
    $altPort = 8080
    Write-Host "Nie udało się odczytać portów z konfiguracji. Używam domyślnych: główny=$mainPort, alternatywny=$altPort" -ForegroundColor Yellow
}

Write-Host "Dodawanie reguł firewalla dla Lista Obecnosci..." -ForegroundColor Green

try {
    # Dodaj regułę dla portu głównego
    netsh advfirewall firewall add rule name="Lista Obecnosci Server - Port $mainPort" dir=in action=allow protocol=TCP localport=$mainPort
    Write-Host "✅ Dodano regułę dla portu głównego $mainPort" -ForegroundColor Green
    
    # Dodaj regułę dla portu alternatywnego
    netsh advfirewall firewall add rule name="Lista Obecnosci Server - Port $altPort" dir=in action=allow protocol=TCP localport=$altPort
    Write-Host "✅ Dodano regułę dla portu alternatywnego $altPort" -ForegroundColor Green
    
    # Dodaj regułę dla portu panelu webowego (8002)
    netsh advfirewall firewall add rule name="Lista Obecnosci Server - Port 8002" dir=in action=allow protocol=TCP localport=8002
    Write-Host "✅ Dodano regułę dla portu panelu webowego 8002" -ForegroundColor Green
    
    Write-Host "`nSUCCESS: Reguły firewalla zostały dodane pomyślnie!" -ForegroundColor Green
    Write-Host "Serwer Lista Obecnosci powinien być teraz dostępny z sieci lokalnej." -ForegroundColor Green
    
    # Sprawdź czy reguły zostały dodane
    Write-Host "`nSprawdzenie reguł:" -ForegroundColor Yellow
    netsh advfirewall firewall show rule name="Lista Obecnosci Server - Port $mainPort"
    netsh advfirewall firewall show rule name="Lista Obecnosci Server - Port $altPort"
    netsh advfirewall firewall show rule name="Lista Obecnosci Server - Port 8002"
}
catch {
    Write-Host "ERROR: Błąd podczas dodawania reguł firewalla: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Upewnij się, że uruchamiasz ten skrypt jako Administrator!" -ForegroundColor Red
}

Write-Host "`nNaciśnij Enter aby zamknąć..." -ForegroundColor Cyan
Read-Host
