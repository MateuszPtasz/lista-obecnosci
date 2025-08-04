#!/usr/bin/env python3
# optimize_db_connections.ps1
# Skrypt do optymalizacji połączeń z bazą danych i rozwiązania problemów z wydajnością

# Zatrzymaj istniejący proces
Write-Host "Sprawdzanie działających instancji aplikacji..."
$processName = "python"
$processes = Get-Process -Name $processName -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

if ($processes) {
    Write-Host "Znaleziono działające procesy aplikacji. Zatrzymywanie..."
    $processes | ForEach-Object { 
        Write-Host "Zatrzymywanie procesu PID: $($_.Id)"
        Stop-Process -Id $_.Id -Force 
    }
}

# Optymalizacja bazy danych SQLite
Write-Host "Optymalizacja bazy danych SQLite..."
$databasePath = "database.db"
if (Test-Path $databasePath) {
    Write-Host "Wykonywanie kopii zapasowej bazy danych..."
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item $databasePath -Destination "database_backup_$timestamp.db"
    
    Write-Host "Wykonywanie VACUUM na bazie danych..."
    sqlite3 $databasePath "VACUUM;"
    sqlite3 $databasePath "PRAGMA optimize;"
    sqlite3 $databasePath "PRAGMA integrity_check;"
    
    Write-Host "Optymalizacja bazy danych ukończona."
} else {
    Write-Host "Nie znaleziono pliku bazy danych: $databasePath"
}

# Czyszczenie zbędnych plików
Write-Host "Czyszczenie plików tymczasowych i cache..."
$foldersToClean = @(
    "__pycache__"
)

foreach ($folder in $foldersToClean) {
    if (Test-Path $folder) {
        Write-Host "Czyszczenie folderu: $folder"
        Get-ChildItem -Path $folder -File | ForEach-Object {
            Remove-Item -Path $_.FullName -Force
        }
    }
}

# Sprawdź konflikty rozszerzeń VS Code
Write-Host "Sprawdzanie potencjalnych konfliktów rozszerzeń VS Code..."
Write-Host "Sugerowane akcje:"
Write-Host "1. Tymczasowo wyłącz nieużywane rozszerzenia VS Code"
Write-Host "2. Uruchom VS Code w trybie bezpiecznym (--disable-extensions)"
Write-Host "3. Zmniejsz liczbę otwartych plików i kart"
Write-Host "4. Upewnij się, że system ma wystarczającą ilość dostępnej pamięci RAM"

Write-Host "Optymalizacja zakończona. Zalecamy ponowne uruchomienie aplikacji."
