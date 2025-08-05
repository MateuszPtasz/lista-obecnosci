# Instrukcja uruchamiania serwerów Lista Obecności

## Opcje uruchamiania serwerów

.\.venv\Scripts\activate; python start_api_servers.py

### 1. Automatyczne uruchamianie (zalecane)

Najłatwiejszym sposobem uruchomienia serwerów jest użycie skryptu wsadowego:

```
.\start_servers_new.bat
```

Lub używając skryptu Python (po aktywacji środowiska wirtualnego):
```powershell
# W PowerShell:
.\.venv\Scripts\activate; python start_api_servers.py

# W CMD:
.\.venv\Scripts\activate && python start_api_servers.py
```

Ten skrypt:
- Automatycznie wykrywa konfigurację z pliku `configs/app_config.py`
- Sprawdza czy istnieje środowisko wirtualne `venv_new`
- Uruchamia trzy serwery w oddzielnych procesach:
  - Serwer główny na porcie z ustawienia `APP_PORT_MAIN` (domyślnie 8000)
  - Serwer alternatywny na porcie z ustawienia `APP_PORT_ALT` (domyślnie 8080)
  - Serwer panelu webowego na porcie 8002 (obsługuje komunikację z panelem administracyjnym)

**UWAGA:** Automatyczne przeładowywanie serwerów zostało wyłączone, aby zapobiec problemom z niespodziewanym restartem. Po wprowadzeniu zmian w kodzie, należy ręcznie zrestartować serwery.

### 2. Ręczne uruchamianie

Jeśli automatyczne uruchamianie nie działa, możesz uruchomić serwery ręcznie:

#### a) Używając środowiska wirtualnego:

```
# Aktywuj środowisko wirtualne
.\venv_new\Scripts\activate

# Uruchom pierwszy serwer
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# W innym oknie terminala uruchom drugi serwer (alternatywny port)
python -m uvicorn main:app --host 0.0.0.0 --port 8080

# W trzecim oknie terminala uruchom serwer panelu webowego
python -m uvicorn main:app --host 0.0.0.0 --port 8002
```

#### b) Używając bezpośrednio uvicorn:

```
# Uruchom pierwszy serwer
uvicorn main:app --host 0.0.0.0 --port 8000

# W innym oknie terminala uruchom drugi serwer (alternatywny port)
uvicorn main:app --host 0.0.0.0 --port 8080

# W trzecim oknie terminala uruchom serwer panelu webowego
uvicorn main:app --host 0.0.0.0 --port 8002
```

#### c) Używając plików głównych aplikacji:

```
# Uruchom pierwszy serwer
python main.py

# W innym oknie terminala uruchom drugi serwer (alternatywny port)
python server_alt_port.py

# W trzecim oknie terminala uruchom serwer panelu webowego
python main.py --port 8002
```

## Dostępne narzędzia diagnostyczne

### 1. Diagnostyka konfiguracji aplikacji mobilnej

```
.\diagnoza_konfiguracji.bat
```

Ten skrypt sprawdza:
- Poprawność pliku konfiguracyjnego
- Możliwość importu konfiguracji
- Dostępność endpointów konfiguracji
- Format odpowiedzi API

**UWAGA:** Skrypt ten uruchomi diagnostykę w nowym oknie, aby nie zatrzymywać działających serwerów.

### 2. Test uprawnień do plików konfiguracyjnych

```
.\test_permissions.bat
```

Ten skrypt sprawdza:
- Czy procesy mają uprawnienia do zapisu plików
- Czy możliwe jest modyfikowanie plików konfiguracyjnych
- Czy zmiany są poprawnie zapisywane

### 3. Test zapisywania i odczytywania konfiguracji

```
# Automatyczny test z użyciem domyślnego konta administratora
python test_config_save_auto.py

# Interaktywny test z możliwością podania własnych danych logowania
python test_config_save_with_auth.py

# Test zapisywania konfiguracji z poziomu panelu webowego
python test_web_panel_config_save.py

# Test przeładowywania konfiguracji
python test_config_reload.py
```

Ten skrypt sprawdza:
- Możliwość logowania do systemu jako administrator
- Zapisywanie konfiguracji przez API
- Odczytywanie konfiguracji z różnych endpointów
- Faktyczną aktualizację plików konfiguracyjnych
- Poprawność struktury danych wysyłanej z panelu webowego
- Przeładowywanie konfiguracji po zmianach w pliku

### 4. Test połączeń API

```
python test_api_connection.py
```

Ten skrypt sprawdza:
- Dostępność serwerów API
- Możliwość połączenia z różnymi endpointami
- Poprawność odpowiedzi API

### 4. Pełna diagnostyka API mobilnego

```
python test_mobile_api.py --all-tests
```

Ten skrypt wykonuje kompleksowe testy:
- Wszystkich funkcji API
- Formatów odpowiedzi
- Obsługi błędów

## Instrukcja budowania aplikacji mobilnej

### 1. Wymagania wstępne

Przed rozpoczęciem budowania aplikacji mobilnej upewnij się, że:
- Zainstalowano Flutter SDK
- Zainstalowano Android SDK
- Skonfigurowano zmienne środowiskowe
- Podłączono urządzenie mobilne lub uruchomiono emulator

### 2. Budowanie aplikacji w trybie debug

```
# Przejdź do katalogu aplikacji mobilnej
cd m:\Programowanie\lista_obecnosci\mobile_app

# Aktualizacja zależności
flutter pub get

# Budowanie aplikacji w trybie debug
flutter build apk --debug

# Kopiowanie pliku APK do głównego katalogu projektu
copy build\app\outputs\flutter-apk\app-debug.apk ..\lista-obecnosci-app-debug.apk
```

### 3. Budowanie aplikacji w trybie release

```
# Przejdź do katalogu aplikacji mobilnej
cd m:\Programowanie\lista_obecnosci\mobile_app

# Aktualizacja zależności
flutter pub get

# Budowanie aplikacji w trybie release
flutter build apk --release

# Kopiowanie pliku APK do głównego katalogu projektu
copy build\app\outputs\flutter-apk\app-release.apk ..\lista-obecnosci-app-release.apk
```

### 4. Instalacja na urządzeniu

```
# Instalacja na podłączonym urządzeniu
flutter install

# Alternatywnie można zainstalować bezpośrednio plik APK
adb install ..\lista-obecnosci-app-debug.apk
```

### 5. Automatyczne budowanie

Możesz również użyć przygotowanego skryptu:

```
# Uruchom skrypt automatycznego budowania
.\build_mobile_app.bat
```

Ten skrypt przeprowadzi cały proces budowania i skopiuje gotowy plik APK do głównego katalogu projektu.

## Restarty i zarządzanie serwerami

### Bezpieczny restart serwerów

Jeśli wprowadzono zmiany w kodzie lub napotykasz problemy z działaniem serwerów, możesz użyć skryptu do bezpiecznego restartu:

```
.\restart_servers.bat
```

Ten skrypt:
1. Bezpiecznie zatrzymuje wszystkie uruchomione serwery
2. Czyści pliki tymczasowe (*.pyc)
3. Aktywuje środowisko wirtualne
4. Uruchamia skrypt start_api_servers.py w nowym oknie

**UWAGA:** Zawsze używaj tego skryptu do restartu serwerów po wprowadzeniu zmian w kodzie, aby uniknąć problemów z niekontrolowanymi restartami.

## Najczęstsze problemy i rozwiązania

### 1. Problem z zapisem konfiguracji

Jeśli zmiany w konfiguracji nie są zapisywane:
- Uruchom `test_permissions.bat` aby sprawdzić uprawnienia
- Sprawdź czy plik `config.py` nie jest tylko do odczytu
- Uruchom serwer z uprawnieniami administratora

### 2. Problemy z portami

Jeśli porty są zajęte:
- Zmień porty w `configs/app_config.py`
- Uruchom `netstat -ano | findstr :8000` aby sprawdzić zajęte porty
- Zakończ procesy używające tych portów lub wybierz inne

### 3. Problemy z połączeniem aplikacji mobilnej

Jeśli aplikacja mobilna nie może połączyć się z serwerem:
- Sprawdź czy firewall jest odpowiednio skonfigurowany (`fix_firewall.bat`)
- Upewnij się, że telefon i komputer są w tej samej sieci
- Sprawdź czy w aplikacji mobilnej ustawiono poprawny adres IP i port

### 4. Problemy z automatycznym wyłączaniem się serwerów

Jeśli serwery nieoczekiwanie się wyłączają:
- Użyj skryptu `restart_servers.bat` do ponownego uruchomienia serwerów
- Sprawdź logi serwerów w poszukiwaniu błędów
- Upewnij się, że żaden edytor kodu nie powoduje zmian w plikach podczas działania serwera
- Po zakończeniu edycji plików źródłowych, użyj skryptu `restart_servers.bat`

### 4. Problemy z konfiguracją

Jeśli konfiguracja nie jest aktualizowana:
- Sprawdź logi serwera, czy nie ma błędów podczas zapisu
- Upewnij się, że serwer ma uprawnienia do modyfikacji plików
- Uruchom `diagnoza_konfiguracji.bat` aby zbadać problem
- Upewnij się, że masz uprawnienia administratora (jesteś zalogowany jako admin)
- Sprawdź format danych wysyłanych do serwera (musi być zgodny z oczekiwaną strukturą)
- Uruchom `python test_web_panel_config_save.py` aby przetestować zapis konfiguracji z panelu
- Po wprowadzeniu zmian w konfiguracji, zrestartuj serwery aby zmiany zostały uwzględnione
- Sprawdź czy konfiguracja jest poprawnie przeładowywana przez API używając `python test_config_reload.py`

### 5. Błędy 400 Bad Request przy zapisie konfiguracji mobilnej

Jeśli przy zapisie konfiguracji mobilnej występuje błąd 400 Bad Request:
- Upewnij się, że dane wysyłane do endpointu `/mobile-config` mają poprawną strukturę
- Wymagana struktura JSON dla endpointu `/mobile-config`:
  ```json
  {
    "APP_VERSION_INFO": {
      "current_version": "1.0.0",
      "minimum_version": "1.0.0",
      "update_required": false,
      "update_message": "Dostępna nowa wersja aplikacji z ulepszeniami!",
      "play_store_url": "https://play.google.com/store/apps/details?id=com.example.lista_obecnosci",
      "update_features": ["Funkcja 1", "Funkcja 2"]
    },
    "MOBILE_APP_CONFIG": {
      "timer_enabled": true,
      "daily_stats": true,
      "monthly_stats": true,
      ...
    }
  }
  ```
- Uruchom `test_mobile_config.bat` aby przetestować poprawność formatu danych
