# CHANGELOG - CENTRALNA KONFIGURACJA (2025-08-05)

## Zmiany wprowadzone

### 1. Centralna konfiguracja adresów IP i portów
- Utworzono nowy katalog `configs/` dla plików konfiguracyjnych
- Stworzono plik `configs/app_config.py` zawierający centralne ustawienia portów i adresów IP
- Zmienne konfiguracyjne:
  - `APP_PORT_MAIN`: główny port aplikacji (domyślnie 8000)
  - `APP_PORT_ALT`: alternatywny port aplikacji (domyślnie 8080)
  - `APP_DEFAULT_IP`: domyślny adres IP serwera (domyślnie 192.168.1.30)

### 2. Aktualizacja plików serwerowych
- Zaktualizowano `main.py` - wykorzystuje porty z centralnej konfiguracji
- Zaktualizowano `server_alt_port.py` - wykorzystuje porty z centralnej konfiguracji

### 3. Aktualizacja skryptów uruchomieniowych
- Zaktualizowano `start_servers.bat` - używa nowych portów z konfiguracji
- Zaktualizowano `start_all.bat` - używa nowych portów z konfiguracji
- Utworzono `start_api_servers.py` - nowy skrypt Python do uruchamiania serwerów

### 4. Aktualizacja konfiguracji firewalla
- Zaktualizowano `add_firewall_rule.ps1` - dynamiczne odczytywanie portów z konfiguracji
- Zaktualizowano `fix_firewall.bat` - wykorzystuje zaktualizowany skrypt PowerShell

### 5. Aktualizacja dokumentacji
- Zaktualizowano `FIREWALL_INSTRUKCJA.md` - dodano informacje o dynamicznej konfiguracji portów
- Zaktualizowano `INSTRUKCJA_URUCHOMIENIA_SYSTEMU.md` - dodano informacje o centralnej konfiguracji

## Powód zmian

Wprowadzenie centralnej konfiguracji adresów IP i portów ma na celu:
1. Ułatwienie zarządzania konfiguracją w jednym miejscu
2. Eliminację hardcodowanych wartości portów i adresów IP w kodzie
3. Uproszczenie procesu zmiany portów w przypadku konfliktów
4. Zwiększenie spójności konfiguracji w całej aplikacji

## Jak zaktualizować

1. W przypadku konieczności zmiany portów, wystarczy edytować plik `configs/app_config.py`
2. Po zmianie konfiguracji należy uruchomić ponownie serwery oraz zaktualizować reguły firewalla
3. Aplikacja mobilna musi zostać skonfigurowana z nowymi ustawieniami w przypadku zmiany portów
