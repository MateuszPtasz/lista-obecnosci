# Struktura projektu "Lista obecności"

## Główne katalogi i pliki

```
├── .vscode/ ├── configs/                       # Katalog centralnej konfiguracji
│   └── app_config.py              # Centralna konfiguracja portów i IP
├── ZALECENIA_OPTYMALIZACJI.md     # Zalecenia optymalizacji
```

## Główne komponenty systemu

1. **Backend (Python)**
   - Główny moduł aplikacji: `main.py`
   - Obsługa bazy danych: `database.py`
   - Autoryzacja: `auth.py`
   - Modele danych: `models.py`
   - Centralna konfiguracja: `configs/app_config.py`            # Konfiguracja Visual Studio Code
├── __pycache__/                   # Pliki kompilowane Python
├── backup_20250727-213630/        # Archiwum kopii zapasowej z 27.07.2025
│   ├── frontend/                  # Frontend z kopii zapasowej
│   ├── mobile_app/                # Aplikacja mobilna z kopii zapasowej
│   └── ...                        # Inne pliki z kopii
├── frontend/                      # Pliki frontendu aplikacji
│   ├── attendance_day.html        # Widok obecności dziennej
│   ├── attendance_summary.html    # Podsumowanie obecności
│   ├── calendar.js                # Skrypt kalendarza
│   ├── employee_add.html          # Formularz dodawania pracownika
│   ├── employee_edit.html         # Formularz edycji pracownika
│   ├── employees.html             # Lista pracowników
│   ├── employees.js               # Logika obsługi pracowników
│   ├── index.html                 # Główna strona
│   ├── login.html                 # Strona logowania
│   ├── script.js                  # Główny skrypt JavaScript
│   ├── sidebar.js                 # Skrypt menu bocznego
│   ├── style.css                  # Główny arkusz stylów
│   └── ...                        # Inne pliki frontendu
├── mobile_app/                    # Aplikacja mobilna (Flutter/Dart)
│   ├── android/                   # Konfiguracja Android
│   ├── lib/                       # Kod źródłowy aplikacji
│   └── ...                        # Inne pliki aplikacji mobilnej
├── venv/                          # Wirtualne środowisko Python
├── add_auth_columns.py            # Skrypt dodający kolumny autoryzacji
├── add_columns.py                 # Skrypt dodający kolumny do bazy
├── add_employee.html              # Formularz dodawania pracownika
├── add_firewall_rule.ps1          # Skrypt PowerShell konfiguracji zapory
├── add_pin_column.py              # Skrypt dodający kolumnę PIN
├── add_sample_employees.py        # Skrypt dodający przykładowych pracowników
├── add_worker.py                  # Skrypt dodający pracownika
├── api_config.py                  # Konfiguracja API
├── app_client_logs.log            # Logi klienta aplikacji
├── attendance.py                  # Moduł obecności
├── auth.py                        # Moduł autoryzacji
├── build_and_log.bat              # Skrypt budowania z logowaniem
├── build_log.txt                  # Log budowania
├── build_mobile_app.bat           # Skrypt budowania aplikacji mobilnej
├── CHANGELOG_*.md                 # Pliki ze zmianami w wersjach
├── check_*.py                     # Różne skrypty diagnostyczne
├── config.py                      # Konfiguracja aplikacji
├── create_tables.py               # Skrypt tworzenia tabel w bazie
├── create_test_admin.py           # Skrypt tworzenia administratora testowego
├── database.db                    # Baza danych SQLite
├── database.log                   # Log bazy danych
├── database.py                    # Moduł bazy danych
├── database_backup_*.db           # Kopie zapasowe bazy danych
├── database_fixed.py              # Poprawiona wersja modułu bazy danych
├── debug_active_workers.py        # Skrypt debugowania aktywnych pracowników
├── device_logs_report.py          # Raport logów urządzeń
├── dodaj_kolumny.sql              # SQL dla dodania kolumn
├── email_service.py               # Serwis e-mail
├── employees.py                   # Moduł pracowników
├── FIREWALL_INSTRUKCJA.md         # Instrukcja konfiguracji zapory
├── fix_*.py                       # Różne skrypty naprawcze
├── fix_*.bat                      # Skrypty naprawcze wsadowe
├── fix_*.sql                      # Skrypty naprawcze SQL
├── init_db.py                     # Inicjalizacja bazy danych
├── install_app_on_device.ps1      # Skrypt instalacji aplikacji na urządzeniu
├── INSTRUKCJA_*.md                # Różne instrukcje
├── lista-obecnosci-app-*.apk      # Pliki instalacyjne aplikacji mobilnej
├── logs.py                        # Moduł logowania
├── main.py                        # Główny moduł aplikacji
├── main_*.py                      # Różne wersje głównego modułu
├── migracja_*.py                  # Skrypty migracji
├── migracja_*.ps1                 # Skrypty migracji PowerShell
├── migration_add_pin.py           # Migracja dodająca PIN
├── models.py                      # Definicje modeli danych
├── optimize_*.py                  # Skrypty optymalizacji
├── optimize_*.ps1                 # Skrypty optymalizacji PowerShell
├── pin_access_logs.py             # Logi dostępu PIN
├── quick_add.py                   # Szybkie dodawanie
├── RAPORT_*.md                    # Pliki raportów
├── README.md                      # Plik README
├── rebuild_shifts_*.py            # Przebudowa tabeli zmian
├── rebuild_shifts.sql             # SQL przebudowy zmian
├── reset_admin_password.py        # Reset hasła administratora
├── RESTART_INSTRUCTIONS.md        # Instrukcje restartu
├── schemas.py                     # Definicje schematów
├── server_alt_port.py             # Serwer na alternatywnym porcie
├── shifts.db                      # Baza danych zmian
├── start_*.bat                    # Skrypty startowe
├── start_*.py                     # Skrypty startowe Python
├── wykonaj_migracje.py            # Wykonywanie migracji
└── ZALECENIA_OPTYMALIZACJI.md     # Zalecenia optymalizacji
```

## Główne komponenty systemu

1. **Backend (Python)**
   - Główny moduł aplikacji: `main.py`
   - Obsługa bazy danych: `database.py`
   - Autoryzacja: `auth.py`
   - Modele danych: `models.py`

2. **Frontend (HTML/JS/CSS)**
   - Pliki interfejsu użytkownika w katalogu `frontend/`
   - Główne widoki: `index.html`, `employees.html`, `attendance_day.html`
   - Arkusze stylów: `style.css`
   - Skrypty JavaScript: `script.js`, `employees.js`, `calendar.js`

3. **Aplikacja mobilna (Flutter/Dart)**
   - Kod źródłowy w katalogu `mobile_app/`
   - Pliki instalacyjne APK: `lista-obecnosci-app-*.apk`

4. **Baza danych**
   - Główna baza: `database.db` (SQLite)
   - Tabela zmian: `shifts.db`
   - Skrypty tworzenia tabel: `create_tables.py`
   - Skrypty migracji: różne pliki `migracja_*.py`

5. **Narzędzia i skrypty**
   - Skrypty diagnostyczne: `check_*.py`
   - Skrypty naprawcze: `fix_*.py`
   - Skrypty budowania: `build_and_log.bat`, `build_mobile_app.bat`
   - Skrypty startowe: `start_*.bat`, `start_*.py`

6. **Dokumentacja**
   - Instrukcje: pliki `INSTRUKCJA_*.md`
   - Raporty: pliki `RAPORT_*.md`
   - Historia zmian: pliki `CHANGELOG_*.md`
   - Zalecenia optymalizacyjne: `ZALECENIA_OPTYMALIZACJI.md`

## Uruchamianie systemu

### 1. Uruchomienie serwerów API

Masz kilka opcji uruchomienia serwerów API:

a) **Skrypt wsadowy** - najłatwiejszy sposób:
   - Kliknij dwukrotnie na plik `start_all.bat`
   - System otworzy okna PowerShell z uruchomionymi serwerami

b) **Skrypt Python**:
   - Otwórz terminal/PowerShell
   - Uruchom komendę: `python start_api_servers.py`
   - Ten sposób pozwala na łatwe zatrzymanie serwerów za pomocą Ctrl+C

c) **Ręczne uruchomienie**:
   - Otwórz terminal/PowerShell
   - Uruchom komendę: `python main.py` (serwer główny na porcie 8000)
   - W drugim oknie terminala uruchom: `python server_alt_port.py` (serwer alternatywny na porcie 8080)
   - W trzecim oknie terminala uruchom: `python -m uvicorn main:app --host 0.0.0.0 --port 8002` (serwer panelu webowego)

### 2. Konfiguracja firewalla

Po uruchomieniu serwerów API należy skonfigurować Windows Firewall:

a) **Automatyczna konfiguracja**:
   - Kliknij prawym przyciskiem myszy na `fix_firewall.bat`
   - Wybierz "Uruchom jako administrator"
   - Postępuj zgodnie z instrukcjami na ekranie

b) **Szczegółowe instrukcje** znajdują się w pliku `FIREWALL_INSTRUKCJA.md`

### 3. Dostęp do aplikacji

a) **Interfejs webowy**:
   - Otwórz przeglądarkę i przejdź pod adres: 
     - http://localhost:8000 - główny interfejs API
     - http://localhost:8002 - panel administracyjny web

b) **Aplikacja mobilna**:
   - Zainstaluj plik APK na urządzeniu Android
   - W ustawieniach aplikacji ustaw adres serwera: http://192.168.1.xxx:8000
   - Gdzie xxx to ostatnia część adresu IP twojego komputera

### 4. Centralna konfiguracja

Jeśli musisz zmienić porty lub adresy IP, edytuj plik `configs/app_config.py`, a następnie:

1. Uruchom ponownie serwery API
2. Uruchom ponownie skrypt konfiguracji firewalla
3. Zaktualizuj ustawienia w aplikacji mobilnej
