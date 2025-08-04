# Skrypt do dodania reguly firewalla dla aplikacji Lista Obecnosci
# Uruchom ten plik jako Administrator!

Write-Host "Dodawanie reguly firewalla dla Lista Obecnosci..." -ForegroundColor Green

try {
    # Dodaj regule dla portu 8000
    netsh advfirewall firewall add rule name="Lista Obecnosci Server - Port 8000" dir=in action=allow protocol=TCP localport=8000
    
    Write-Host "SUCCESS: Regula firewalla zostala dodana pomyslnie!" -ForegroundColor Green
    Write-Host "Serwer Lista Obecnosci powinien byc teraz dostepny z sieci lokalnej." -ForegroundColor Green
    
    # Sprawdz czy regula zostala dodana
    Write-Host "`nSprawdzenie reguły:" -ForegroundColor Yellow
    netsh advfirewall firewall show rule name="Lista Obecnosci Server - Port 8000"
}
catch {
    Write-Host "ERROR: Blad podczas dodawania reguly firewalla: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Upewnij sie, ze uruchamiasz ten skrypt jako Administrator!" -ForegroundColor Red
}

Write-Host "`nNacisnij Enter aby zamknac..." -ForegroundColor Cyan
Read-Host
