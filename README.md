# Lista Obecności - Enhanced Security & Production-Ready System

Kompleksowy system do ewidencji czasu pracy z zaawansowanymi funkcjami bezpieczeństwa, autoryzacji i gotowością produkcyjną.

## 🚀 Nowe Funkcje v2.0

### 🔐 Bezpieczeństwo i Autoryzacja
- **JWT Authentication** - Bezpieczny dostęp do API dla aplikacji mobilnej
- **Session-based Authentication** - Autoryzacja sesyjna dla panelu webowego  
- **Protected Endpoints** - Wszystkie wrażliwe endpointy zabezpieczone
- **Role-based Access** - Rozróżnienie uprawnień administratora i użytkownika
- **Password Hashing** - Bezpieczne przechowywanie haseł (bcrypt)

### 📊 Eksport i Raporty
- **CSV Export** - Alternatywa do eksportu PDF
- **Enhanced Email Service** - Ulepszona obsługa SMTP z zaawansowaną obsługą błędów
- **Multiple Report Formats** - Podsumowania, szczegóły, raporty dzienne
- **Secure Report Access** - Raporty dostępne tylko po uwierzytelnieniu

### 🐳 Wdrożenie Produkcyjne
- **Docker Support** - Kompletny setup Docker Compose
- **Nginx Reverse Proxy** - Load balancing, SSL, rate limiting
- **Comprehensive Logging** - Strukturalne logowanie z rotacją plików
- **Automated Backups** - System kopii zapasowych z kompresją
- **Health Checks** - Monitoring zdrowia aplikacji

### 🛠️ Narzędzia Administracyjne
- **Backup System** - Narzędzie do tworzenia i przywracania kopii zapasowych
- **Email Testing** - Testowanie konfiguracji SMTP
- **Configuration Management** - Zdalne zarządzanie konfiguracją aplikacji mobilnej

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
