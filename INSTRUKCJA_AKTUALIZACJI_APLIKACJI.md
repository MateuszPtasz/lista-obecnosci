# INSTRUKCJA AKTUALIZACJI APLIKACJI LISTA OBECNOŚCI

## 1. Uruchamianie serwerów

### Metoda 1: Skrypt automatyczny

Użyj skryptu `start_servers_new.bat`, który automatycznie uruchomi wszystkie potrzebne serwery:

1. Kliknij prawym przyciskiem myszy na plik `start_servers_new.bat` i wybierz "Uruchom jako administrator"
2. Skrypt automatycznie odczyta konfigurację z pliku `configs/app_config.py`
3. Zostaną uruchomione trzy serwery:
   - Serwer główny (domyślnie port 8000)
   - Serwer alternatywny (domyślnie port 8080)
   - Serwer panelu webowego (port 8002)

### Metoda 2: Skrypt Python

Możesz również użyć skryptu Python do uruchomienia serwerów:

1. Otwórz wiersz poleceń lub PowerShell jako administrator
2. Przejdź do katalogu głównego projektu
3. Uruchom:
   ```
   python start_api_servers.py
   ```
4. Skrypt automatycznie uruchomi wszystkie potrzebne serwery

### Metoda 3: Ręczne uruchamianie

Jeśli wolisz ręcznie uruchomić każdy serwer:

1. Serwer główny:
   ```
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. Serwer alternatywny:
   ```
   python -m uvicorn main:app --host 0.0.0.0 --port 8080
   ```
   lub
   ```
   python server_alt_port.py
   ```

3. Serwer panelu webowego:
   ```
   python -m uvicorn main:app --host 0.0.0.0 --port 8002
   ```

## 2. Konfiguracja zapory sieciowej

Aby aplikacja działała poprawnie w sieci, konieczne jest skonfigurowanie zapory sieciowej.

### Automatyczna konfiguracja zapory:

1. Kliknij prawym przyciskiem myszy na plik `fix_firewall.bat` i wybierz "Uruchom jako administrator"
2. Skrypt automatycznie doda wszystkie potrzebne reguły do zapory Windows

### Ręczna konfiguracja zapory:

1. Otwórz Zaawansowane ustawienia zabezpieczeń zapory sieciowej Windows
2. Utwórz nowe reguły przychodzące dla TCP dla portów:
   - 8000 (serwer główny)
   - 8080 (serwer alternatywny)
   - 8002 (serwer panelu webowego)

## 3. Kompilacja aplikacji mobilnej

### Metoda 1: Używanie skryptu automatycznego

1. Upewnij się, że masz zainstalowane narzędzie Flutter
2. Kliknij dwukrotnie na `build_mobile_app.bat`, który automatycznie skompiluje aplikację
3. Wynikowy plik .apk pojawi się w katalogu głównym

### Metoda 2: Ręczna kompilacja

1. Otwórz terminal w katalogu projektu aplikacji mobilnej
2. Wykonaj polecenia:
   ```
   flutter clean
   flutter pub get
   flutter build apk --release
   ```
3. Skopiuj wynikowy plik .apk z katalogu `build/app/outputs/flutter-apk/app-release.apk` do katalogu głównego

## 4. Testowanie połączenia

Aby sprawdzić, czy wszystkie serwery działają poprawnie:

1. Otwórz przeglądarkę i przejdź pod adres:
   - `http://localhost:8000/docs` - dokumentacja głównego API
   - `http://localhost:8080/docs` - dokumentacja alternatywnego API
   - `http://localhost:8002/docs` - dokumentacja API panelu webowego

2. Upewnij się, że na każdym porcie otrzymujesz poprawną odpowiedź

## 5. Rozwiązywanie problemów

### Problem z połączeniem z aplikacji mobilnej:

1. Sprawdź, czy wszystkie serwery są uruchomione
2. Upewnij się, że w aplikacji mobilnej jest skonfigurowany prawidłowy adres IP
3. Sprawdź, czy zapora sieciowa ma dodane odpowiednie reguły
4. Użyj skryptu `diagnoza_konfiguracji.py` aby zweryfikować poprawność konfiguracji

### Problem z uprawnieniami:

1. Upewnij się, że skrypty są uruchamiane z uprawnieniami administratora
2. Sprawdź logi w pliku `database.log`
