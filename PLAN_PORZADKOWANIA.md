# Plan porządkowania projektu "Lista obecności"

Poniżej przedstawiam plan uporządkowania projektu oraz listę plików, które można bezpiecznie usunąć. Wszystkie zmiany są bezpieczne, ponieważ repozytorium jest kontrolowane przez Git, co pozwala na łatwe przywrócenie usuniętych plików w razie potrzeby.

## Pliki do usunięcia:

### 1. Kopie zapasowe głównego pliku aplikacji
```
main.py.backup_przed_poprawkami
main.py.bak
main.py.bak2
main_backup.py
main_optimized.py
```

### 2. Stare kopie baz danych (jeśli nowsze wersje są aktualne)
```
database_backup_20250731-221443.db   # Starsza kopia - do usunięcia
database_backup_20250802-094427.db   # Nowsza kopia - można zachować jako ostatnią kopię zapasową
```

### 3. Stare pliki APK aplikacji mobilnej
```
lista-obecnosci-app--001.apk               # Starsza wersja - do usunięcia
lista-obecnosci-app-FINAL-CONFIG-DEBUG-20250727-2030.apk  # Starsza wersja - do usunięcia
lista-obecnosci-app-20250802-001.apk       # Najnowsza wersja - zachować
```

### 4. Zduplikowane dokumentacje i pliki konfiguracyjne
```
INSTRUKCJA_AKTUALIZACJI_APLIKACJI.md        # Starsza wersja - do usunięcia
INSTRUKCJA_AKTUALIZACJI_APLIKACJI_2025-08-03.md  # Nowsza wersja - zachować i zmienić nazwę na INSTRUKCJA_AKTUALIZACJI_APLIKACJI.md
```

### 5. Zduplikowane pliki migracji i naprawy
Wybrać jedną najnowszą/poprawną wersję z poniższych zbiorów plików:

Zarządzanie bazą danych:
```
fix_database.py          # Prawdopodobnie główny plik naprawczy
fix_database_direct.py   # Alternatywna wersja
fix_db_columns.py        # Plik do naprawy kolumn
fix_columns_with_log.py  # Plik do naprawy kolumn z logowaniem
```

Migracja danych:
```
migracja_db.py           # Główny plik migracji
migracja_z_logowaniem.py # Wersja z logowaniem (prawdopodobnie nowsza)
```

## Zalecenia dotyczące reorganizacji struktury projektu:

1. **Utworzenie katalogu `scripts/`** dla skryptów pomocniczych:
   ```
   scripts/
   ├── backup/           # Skrypty do tworzenia kopii zapasowych
   ├── maintenance/      # Skrypty konserwacyjne (fix_*, check_*)
   └── migration/        # Skrypty migracji
   ```

2. **Utworzenie katalogu `docs/`** dla dokumentacji:
   ```
   docs/
   ├── changelogs/       # Pliki CHANGELOG_*
   ├── instructions/     # Pliki INSTRUKCJA_*
   └── reports/          # Pliki RAPORT_*
   ```

3. **Utworzenie katalogu `releases/`** dla plików instalacyjnych:
   ```
   releases/
   └── mobile/           # Pliki .apk aplikacji mobilnej
   ```

4. **Utworzenie katalogu `configs/`** dla plików konfiguracyjnych:
   ```
   configs/
   ├── api.py            # Konfiguracja API
   └── firewall/         # Konfiguracja zapory
   ```

## Komenda do wykonania porządkowania:

```powershell
# Tworzenie katalogów
mkdir -p scripts/backup scripts/maintenance scripts/migration
mkdir -p docs/changelogs docs/instructions docs/reports
mkdir -p releases/mobile
mkdir -p configs/firewall

# Przenoszenie plików do odpowiednich katalogów
# [tutaj komendy przenoszące pliki]

# Usuwanie zbędnych kopii
Remove-Item main.py.backup_przed_poprawkami
Remove-Item main.py.bak
Remove-Item main.py.bak2
Remove-Item main_backup.py
Remove-Item main_optimized.py
Remove-Item database_backup_20250731-221443.db
Remove-Item lista-obecnosci-app--001.apk
Remove-Item lista-obecnosci-app-FINAL-CONFIG-DEBUG-20250727-2030.apk
Remove-Item INSTRUKCJA_AKTUALIZACJI_APLIKACJI.md
```
