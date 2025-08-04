# Instrukcja aktualizacji aplikacji Lista Obecności

## Dla administratorów systemu

### 1. Aktualizacja serwera

1. Wykonaj kopię zapasową bazy danych:
   ```powershell
   Copy-Item "database.db" "database_backup_$(Get-Date -Format 'yyyyMMdd-HHmmss').db"
   ```

2. Zaktualizuj pliki serwera:
   - Upewnij się, że plik `main.py` zawiera najnowszą wersję kodu
   - Sprawdź poprawność endpointów `/api/mobile-config` i `/api/app-version`

3. Uruchom skrypt aktualizacji bazy danych, jeśli wymagany:
   ```
   python check_db_structure.py
   ```

4. Uruchom serwer w trybie debugowania, aby sprawdzić czy działa poprawnie:
   ```
   python main.py
   ```

### 2. Aktualizacja aplikacji mobilnej

1. Upewnij się, że posiadasz najnowszy plik APK:
   - `lista-obecnosci-app-FIXED-API-20250802.apk` lub nowszy

2. Instalacja na urządzeniach testowych:
   - Uruchom skrypt `install_app_on_device.ps1` dla urządzeń podłączonych przez USB
   - Alternatywnie prześlij plik APK bezpośrednio na urządzenia i zainstaluj

3. Weryfikacja działania:
   - Sprawdź logowanie z użyciem PIN
   - Sprawdź rejestrację rozpoczęcia/zakończenia pracy
   - Sprawdź synchronizację w trybie offline

### 3. Rozwiązywanie problemów

1. Problem: Aplikacja nie komunikuje się z serwerem
   - Sprawdź czy serwer jest uruchomiony i dostępny
   - Sprawdź ustawienia adresu IP w aplikacji (plik `api.dart`)
   - Upewnij się, że zapora sieciowa pozwala na połączenie

2. Problem: Błędy w bazie danych
   - Użyj skryptu `fix_database.py` do naprawy struktury
   - Sprawdź logi w pliku `database.log`

3. Problem: Błędy weryfikacji urządzenia
   - Uruchom `debug_active_workers.py` aby sprawdzić status urządzeń
   - W razie potrzeby użyj `fix_active_workers.py`

## Dla użytkowników aplikacji

### 1. Instalacja nowej wersji

1. Usuń poprzednią wersję aplikacji:
   - Przejdź do Ustawienia > Aplikacje > Lista Obecności > Odinstaluj
   - Alternatywnie, nowa wersja może być zainstalowana bezpośrednio (zastąpi starą)

2. Zainstaluj nową wersję:
   - Pobierz plik APK ze wskazanego miejsca
   - Otwórz plik APK i postępuj zgodnie z instrukcjami instalacji
   - Może być wymagane zezwolenie na instalację z nieznanych źródeł

3. Pierwsze uruchomienie:
   - Przy pierwszym uruchomieniu aplikacja może poprosić o nadanie uprawnień
   - Należy zaakceptować wszystkie wymagane uprawnienia

### 2. Problemy i rozwiązania

1. Aplikacja wyświetla błąd połączenia:
   - Upewnij się, że masz dostęp do sieci WiFi lub danych komórkowych
   - Sprawdź czy serwer jest dostępny (skontaktuj się z administratorem)
   - Sprawdź adres serwera w ustawieniach aplikacji

2. Aplikacja zatrzymuje się:
   - Wyczyść dane aplikacji: Ustawienia > Aplikacje > Lista Obecności > Dane aplikacji > Wyczyść dane
   - Uruchom ponownie urządzenie
   - Zainstaluj aplikację ponownie

3. Problem z rejestracją obecności:
   - Upewnij się, że masz włączoną lokalizację
   - Sprawdź, czy urządzenie jest autoryzowane w systemie
   - Spróbuj wylogować się i zalogować ponownie

W razie dalszych problemów skontaktuj się z administratorem systemu.

---

**Data ostatniej aktualizacji instrukcji:** 2025-08-03
