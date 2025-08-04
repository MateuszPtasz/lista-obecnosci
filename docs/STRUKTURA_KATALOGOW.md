# Struktura katalogów po reorganizacji projektu "Lista obecności"

## Główna struktura katalogów

```
├── configs/                     # Konfiguracje aplikacji
│   └── firewall/                # Konfiguracje zapory sieciowej
├── docs/                        # Dokumentacja projektu
│   ├── BIEZACE_PRACE.md         # Plik roboczy z bieżącymi pracami i zaleceniami
│   ├── KONFIGURACJA_PORTOW.md   # Analiza konfiguracji portów komunikacyjnych
│   ├── PLAN_PORZADKOWANIA.md    # Plan porządkowania projektu
│   ├── PODSUMOWANIE_PORZADKOWANIA.md # Podsumowanie wykonanych prac porządkowych
│   ├── README.md                # Główny plik README projektu
│   ├── ZBEDNE_PLIKI.md          # Lista zbędnych plików zidentyfikowanych w projekcie
│   ├── changelogs/              # Historia zmian w wersjach
│   │   ├── CHANGELOG_2025-07-25.md
│   │   ├── CHANGELOG_EWIDENCJA_FIX_2025-08-01.md
│   │   ├── CHANGELOG_MOBILE_APP_2025-08-03.md
│   │   ├── CHANGELOG_MOBILE_FIXED.md
│   │   ├── CHANGELOG_STATYSTYKI_FIX_2025-07-27.md
│   │   └── CHANGELOG_STATYSTYKI_FIX_2025-08-01.md
│   ├── instructions/            # Instrukcje obsługi i konfiguracji
│   │   ├── FIREWALL_INSTRUKCJA.md
│   │   ├── INSTRUKCJA_AKTUALIZACJI_APLIKACJI_2025-08-03.md
│   │   ├── INSTRUKCJA_URUCHOMIENIA_SYSTEMU.md
│   │   └── RESTART_INSTRUCTIONS.md
│   └── reports/                 # Raporty i zalecenia
│       ├── RAPORT_PROBLEMOW_UI.md
│       ├── RAPORT_TESTOW_AKTUALIZACJI.md
│       ├── STATYSTYKI_PIN_DOKUMENTACJA.md
│       ├── SYSTEM_AKTUALIZACJI_UKOŃCZONY.md
│       └── ZALECENIA_OPTYMALIZACJI.md
├── frontend/                    # Pliki frontendu aplikacji webowej
│   ├── attendance_day.html
│   ├── attendance_summary.html
│   ├── employee_add.html
│   ├── employees.html
│   ├── index.html
│   ├── login.html
│   ├── script.js
│   ├── style.css
│   └── ...
├── mobile_app/                  # Aplikacja mobilna (Flutter/Dart)
│   ├── android/                 # Konfiguracja Android
│   ├── lib/                     # Kod źródłowy aplikacji mobilnej
│   │   ├── api.dart             # Konfiguracja API (zawiera adres IP i port)
│   │   └── ...
│   └── ...
├── releases/                    # Pliki instalacyjne i wydania
│   └── mobile/                  # APK aplikacji mobilnej
│       ├── lista-obecnosci-app-20250802-001.apk  # Poprzednia wersja aplikacji
│       └── lista-obecnosci-app-20250802-002.apk  # Najnowsza wersja z poprawkami komunikacji (02.08.2025)
├── scripts/                     # Skrypty pomocnicze
│   ├── backup/                  # Kopie zapasowe i skrypty backup
│   │   └── database_backup_20250802-094427.db  # Najnowsza kopia zapasowa bazy
│   ├── maintenance/             # Skrypty konserwacyjne i naprawcze
│   │   ├── fix_active_workers.py
│   │   ├── fix_columns_with_log.py
│   │   ├── fix_database.py
│   │   └── ...
│   └── migration/               # Skrypty migracji danych
│       ├── migracja_db.py
│       ├── migracja_z_logowaniem.py
│       ├── migration_add_pin.py
│       └── wykonaj_migracje.py
├── static/                      # Statyczne zasoby (obrazy, czcionki, itp.)
├── templates/                   # Szablony HTML
├── venv/                        # Wirtualne środowisko Python
├── add_auth_columns.py          # Skrypt dodający kolumny autoryzacji
├── add_columns.py               # Skrypt dodający kolumny do bazy
├── add_worker.py                # Skrypt dodający pracownika
├── api_config.py                # Konfiguracja API
├── attendance.py                # Moduł obecności
├── auth.py                      # Moduł autoryzacji
├── config.py                    # Konfiguracja aplikacji
├── create_tables.py             # Skrypt tworzenia tabel w bazie
├── database.db                  # Baza danych SQLite
├── database.py                  # Moduł bazy danych
├── employees.py                 # Moduł pracowników
├── logs.py                      # Moduł logowania
├── main.py                      # Główny moduł aplikacji
├── models.py                    # Definicje modeli danych
├── pin_access_logs.py           # Logi dostępu PIN
├── requirements.txt             # Lista zależności projektu
├── schemas.py                   # Definicje schematów
├── server_alt_port.py           # Serwer na alternatywnym porcie 8080
├── shifts.db                    # Baza danych zmian
├── start_all.bat                # Skrypt startowy dla wszystkich komponentów
├── start_api_servers.py         # Skrypt startowy dla serwerów API
└── start_servers.bat            # Skrypt startowy dla serwerów
```

## Konfiguracja portów komunikacyjnych

| Komponent | Port | Plik konfiguracyjny | Uwagi |
|-----------|------|---------------------|-------|
| API dla aplikacji mobilnej | **8000** | `main.py` + `start_api_servers.py` | Główny port API używany przez aplikację mobilną |
| Panel webowy | **8002** | `start_api_servers.py` | Port używany przez panel webowy |
| Port alternatywny | **8080** | `server_alt_port.py` | Port alternatywny używany w przypadku blokowania portu 8000 |

## Uruchomienie systemu

Aby uruchomić system po reorganizacji, należy:

1. **Uruchomienie serwerów API**:
   ```powershell
   # W terminalu VS Code lub CMD
   .\run_servers.bat
   ```
   Uruchomi to API dla aplikacji mobilnej na porcie 8000 bezpośrednio w terminalu.

   **Alternatywnie** można uruchomić serwery pojedynczo:
   ```powershell
   # Tylko API mobilne (port 8000)
   python main.py
   
   # Tylko panel webowy (port 8002)
   python run_web_panel.py
   ```

2. **Port alternatywny** (jeśli 8000 jest blokowany):
   ```powershell
   python server_alt_port.py
   ```

3. **Instalacja aplikacji mobilnej**:
   ```powershell
   adb install releases/mobile/lista-obecnosci-app-20250802-002.apk
   ```
   **UWAGA: Należy instalować najnowszą wersję 002 z poprawkami komunikacji z 02.08.2025.**

## Status projektu

Aktualne informacje o statusie projektu i zaleceniach znajdują się w pliku `docs/BIEZACE_PRACE.md`.
