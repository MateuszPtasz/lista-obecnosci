# Ten skrypt wykonuje aktualizację bazy danych SQLite
# Dodaje kolumny: status, is_holiday i is_sick do tabeli shifts

$databasePath = "database.db"
$logFile = "migracja_powershell_log.txt"

# Dodaj timestamp na początku loga
Add-Content -Path $logFile -Value "Rozpoczęcie migracji: $(Get-Date)"
Add-Content -Path $logFile -Value "----------------------"

# Sprawdź czy baza danych istnieje
if (-not (Test-Path $databasePath)) {
    Add-Content -Path $logFile -Value "BŁĄD: Baza danych $databasePath nie istnieje."
    exit 1
}

# Wykonaj zapytania
try {
    # Zainstaluj SQLite
    Add-Content -Path $logFile -Value "Przygotowywanie środowiska..."
    Add-Content -Path $logFile -Value ""
    
    # Dodaj kolumny używając SQLite
    Add-Content -Path $logFile -Value "Dodawanie kolumn do tabeli shifts..."
    $query1 = "ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny';"
    $query2 = "ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0;"
    $query3 = "ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0;"
    
    # Zapisz zapytania do pliku SQL
    $sqlFile = "migration_queries.sql"
    $query1 | Out-File -FilePath $sqlFile
    $query2 | Add-Content -Path $sqlFile
    $query3 | Add-Content -Path $sqlFile
    
    # Wykonaj zapytania na bazie danych
    Add-Content -Path $logFile -Value "Wykonuję zapytania SQL..."
    $result = sqlite3 $databasePath ".read $sqlFile"
    
    Add-Content -Path $logFile -Value "Zapytania wykonane."
    Add-Content -Path $logFile -Value ""
    
    # Sprawdź strukturę tabeli po migracji
    Add-Content -Path $logFile -Value "Sprawdzam strukturę tabeli po migracji..."
    $tableInfo = sqlite3 $databasePath ".schema shifts"
    Add-Content -Path $logFile -Value $tableInfo
    
    Add-Content -Path $logFile -Value ""
    Add-Content -Path $logFile -Value "Migracja zakończona pomyślnie."
}
catch {
    Add-Content -Path $logFile -Value "Wystąpił błąd podczas migracji:"
    Add-Content -Path $logFile -Value $_.Exception.Message
}

# Pokaż komunikat o zakończeniu
Add-Content -Path $logFile -Value ""
Add-Content -Path $logFile -Value "Zakończenie migracji: $(Get-Date)"
