# Lista Obecności - System Ewidencji Czasu Pracy

## Opis
Kompleksowy system do ewidencji czasu pracy składający się z:
- **Aplikacji mobilnej Flutter** - dla pracowników
- **Panelu webowego** - dla administratorów 
- **API Backend** - FastAPI + SQLite
- **Systemu email** - automatyczne raporty
- **Zdalnej konfiguracji** - zarządzanie funkcjami aplikacji

## Funkcjonalności

### Aplikacja mobilna (Flutter)
- ✅ Logowanie/wylogowanie z lokalizacją GPS
- ✅ Timer czasu pracy w czasie rzeczywistym
- ✅ Sprawdzanie statusu pracy
- ✅ Zdalna konfiguracja funkcji
- ✅ Automatyczne sprawdzanie aktualizacji
- ✅ Obsługa offline

### Panel webowy
- ✅ Dashboard z aktywnymi pracownikami
- ✅ Zarządzanie zespołem (dodawanie/edycja pracowników)
- ✅ Ewidencja czasu pracy z szczegółami
- ✅ Generowanie raportów PDF
- ✅ Konfiguracja aplikacji mobilnej
- ✅ Wysyłanie raportów przez email

### Backend API
- ✅ FastAPI z dokumentacją OpenAPI
- ✅ Baza danych SQLite
- ✅ Endpoints dla aplikacji mobilnej i webowej
- ✅ System stawek (podstawowa, sobota, niedziela, noc, nadgodziny)
- ✅ Obliczenia urlopów i chorobowych
- ✅ Dual-port setup (8000 mobile, 8002 web)

## Struktura projektu

```
├── main.py              # Backend FastAPI
├── config.py            # Konfiguracja systemu
├── database.py          # Połączenie z bazą danych
├── models.py            # Modele SQLAlchemy
├── schemas.py           # Pydantic schemas
├── email_service.py     # System wysyłania email
├── frontend/            # Panel webowy HTML/JS
│   ├── index.html       # Dashboard
│   ├── employees.html   # Zarządzanie zespołem
│   ├── attendance_summary.html  # Ewidencja
│   ├── employee_details.html    # Szczegóły pracownika
│   └── mobile_config.html       # Konfiguracja aplikacji
└── mobile_app/          # Aplikacja Flutter
    ├── lib/
    │   ├── main.dart    # Główna aplikacja
    │   └── api.dart     # Komunikacja z API
    └── android/         # Build Android
```

## Instalacja i uruchomienie

### Backend
```bash
cd lista_obecnosci
pip install fastapi uvicorn sqlalchemy python-multipart jinja2
python init_db.py
python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
python -m uvicorn main:app --host 127.0.0.1 --port 8002 &
```

### Panel webowy
Otwórz: `http://127.0.0.1:8002/frontend/index.html`

### Aplikacja mobilna
```bash
cd mobile_app
flutter pub get
flutter run
```

## Konfiguracja

### Email (config.py)
```python
EMAIL_CONFIG = {
    "enabled": True,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "twoj-email@gmail.com",
    "smtp_password": "haslo-aplikacji",
    "sender_name": "System Obecności"
}
```

### Aplikacja mobilna (config.py)
```python
MOBILE_APP_CONFIG = {
    "timer_enabled": True,
    "daily_stats": False,
    "field_blocking": False,
    "gps_verification": False,
    # ... inne opcje
}
```

## Technologie

- **Backend**: Python 3.13, FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML5, JavaScript (ES6), CSS3
- **Mobile**: Flutter, Dart
- **Database**: SQLite
- **Email**: SMTP (Gmail/Outlook)
- **PDF**: jsPDF

## Wersje

- **v1.0** - Podstawowa funkcjonalność
- **v1.1** - System zdalnej konfiguracji, email reports
- **v1.2** - Naprawy kompatybilności, dual-port setup

## Autor
System stworzony do zarządzania czasem pracy zespołu.

## Backup
Kopia zapasowa: `lista_obecnosci_backup_2025-07-23_17-29`
