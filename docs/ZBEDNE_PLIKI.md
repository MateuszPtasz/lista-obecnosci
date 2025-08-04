# Zbędne pliki do usunięcia

Poniżej znajduje się lista potencjalnie zbędnych plików lub duplikatów, które można usunąć w celu optymalizacji projektu:

## Kopie zapasowe głównego pliku aplikacji:
- main.py.backup_przed_poprawkami
- main.py.bak
- main.py.bak2
- main_backup.py
- main_optimized.py (o ile nie zawiera ważnych optymalizacji nieobecnych w głównym pliku)

## Stare kopie baz danych (jeśli nie są potrzebne do celów archiwalnych):
- database_backup_20250731-221443.db
- database_backup_20250802-094427.db

## Zduplikowane pliki konfiguracyjne:
- INSTRUKCJA_AKTUALIZACJI_APLIKACJI.md i INSTRUKCJA_AKTUALIZACJI_APLIKACJI_2025-08-03.md 
  (prawdopodobnie drugi plik jest nowszą wersją pierwszego)

## Stare wersje aplikacji mobilnej (zostawić tylko najnowszą):
- lista-obecnosci-app--001.apk
- lista-obecnosci-app-FINAL-CONFIG-DEBUG-20250727-2030.apk
- lista-obecnosci-app-20250802-001.apk (prawdopodobnie najnowsza, którą należy zachować)
- lista-obecnosci-app-FIXED-API-20250802.txt (nie plik APK, ale prawdopodobnie notatki)

## Zbędne pliki testowe (jeśli nie są używane aktywnie):
- check_user_1111.py (wygląda na test dla konkretnego użytkownika)
- test_*.py pliki (o ile nie są częścią regularnego procesu testowania)

## Przed usunięciem jakichkolwiek plików:
1. Wykonaj pełną kopię zapasową projektu
2. Upewnij się, że pliki nie są używane przez żaden aktywny proces
3. Sprawdź zależności między plikami, aby uniknąć usunięcia czegoś, co jest używane przez inne skrypty

**UWAGA:** Te pliki zostały zidentyfikowane jako potencjalnie zbędne na podstawie ich nazw. 
Przed faktycznym usunięciem należy sprawdzić zawartość każdego pliku, aby upewnić się, 
że nie zawiera unikalnych informacji, które mogą być potrzebne w przyszłości.
