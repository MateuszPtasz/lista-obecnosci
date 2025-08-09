# API Registry - Lista Obecności System

## Rejestr wszystkich używanych endpoints API

### 💬 Status Message Component API
**Komponent**: `frontend/components/common/status-message.html`  
**Strona testowa**: `frontend/status-message-test.html`

**Specjalność**: Komponent nie wymaga dedykowanych endpointów API
- **Funkcja**: Uniwersalny system wyświetlania komunikatów systemowych
- **Wykorzystanie**: Używany przez inne komponenty do wyświetlania statusów operacji
- **Metody JavaScript**:
  - `StatusMessage.success(message, options)` - komunikaty sukcesu  
  - `StatusMessage.error(message, options)` - komunikaty błędów
  - `StatusMessage.warning(message, options)` - komunikaty ostrzeżeń
  - `StatusMessage.info(message, options)` - komunikaty informacyjne
  - `StatusMessage.loading(message, options)` - komunikaty ładowania
- **Kompatybilność**: `showMessage(message, type, duration)` - stara funkcja

### 🎨 Modern Header Component API
**Komponent**: `frontend/components/common/header.html`

**Specjalność**: Samodzielny komponent bez endpointów API
- **Funkcja**: Animowany nagłówek systemu z efektami glassmorphism
- **Features**: Gradient text, hover shimmer, emoji pulse (📊), responsive design
- **Klasa JavaScript**: `ModernHeaderComponent`
- **Animacje**: Slide-in przy załadowaniu, shimmer hover effect, emoji pulse co 5s
- **Design**: Linear gradient (#667eea → #764ba2), backdrop-filter blur
- **Wykorzystanie**: Header dla głównych stron systemu

### 🏠 Dashboard API
- `GET /api/dashboard/stats` - podstawowe statystyki dashboard
- `GET /api/dashboard/recent-activity` - ostatnie aktywności
- `GET /api/dashboard/notifications` - powiadomienia

### 👥 Employee Management API  
- `GET /api/employees` - lista wszystkich pracowników
- `POST /api/employees` - dodaj nowego pracownika
- `GET /api/employees/{id}` - szczegóły pracownika
- `PUT /api/employees/{id}` - aktualizuj pracownika
- `DELETE /api/employees/{id}` - usuń pracownika
- `POST /api/employees/bulk-import` - import z pliku

### 📅 Attendance API
- `GET /api/attendance_by_date?date={YYYY-MM-DD}` - obecność na dzień
- `GET /api/attendance/summary` - podsumowanie obecności
- `POST /api/attendance/check-in` - odnotuj wejście
- `POST /api/attendance/check-out` - odnotuj wyjście
- `GET /api/attendance/employee/{id}` - obecność pracownika
- `GET /api/attendance/monthly/{year}/{month}` - miesięczne podsumowanie

### ⏰ Time Rounding API
- `GET /api/time-rounding-config` - aktualna konfiguracja zaokrąglania
- `POST /api/time-rounding-config` - zapisz konfigurację zaokrąglania
- `POST /api/time-rounding/test` - testuj zaokrąglanie dla czasu

### 📱 Mobile App API
- `GET /api/mobile/config` - konfiguracja aplikacji mobilnej
- `POST /api/mobile/config` - zapisz konfigurację mobilną
- `GET /api/mobile/version` - informacje o wersji
- `POST /api/mobile/version` - aktualizuj wersję
- `GET /api/mobile/apk-info` - informacje o pliku APK

### 🔐 Authentication API
- `POST /api/login` - logowanie użytkownika
- `POST /api/logout` - wylogowanie użytkownika
- `GET /api/auth/check` - sprawdź status sesji
- `POST /api/auth/refresh` - odśwież token

### 🛡️ Security API
- `GET /api/security/devices` - lista urządzeń
- `POST /api/security/device-check` - sprawdź urządzenie
- `GET /api/security/logs` - logi bezpieczeństwa

### 🔧 System API
- `GET /api/system/health` - status systemu
- `GET /api/system/version` - wersja systemu
- `POST /api/system/backup` - utwórz backup
- `GET /api/system/logs` - logi systemowe

### 📧 Notification API (jeśli istnieje)
- `POST /api/notifications/send` - wyślij powiadomienie
- `GET /api/notifications/templates` - szablony powiadomień
- `POST /api/notifications/email-test` - test wysyłania email

## Komponenty i ich zależności API

### Dashboard Components
- **stats-overview.html** → `/api/dashboard/stats`
- **recent-activity.html** → `/api/dashboard/recent-activity`
- **quick-actions.html** → multiple APIs (depends on actions)

### Attendance Components  
- **daily-view.html** → `/api/attendance_by_date`
- **summary-table.html** → `/api/attendance/summary`
- **calendar-picker.html** → `/api/attendance/monthly/{year}/{month}`

### Employee Components
- **employee-list.html** → `/api/employees`
- **employee-card.html** → `/api/employees/{id}`
- **add-employee-form.html** → `POST /api/employees`

### Config Components
- **time-rounding.html** → `/api/time-rounding-config`
- **mobile-config.html** → `/api/mobile-config` (GET/POST) (NEW!)
- **app-version-management.html** → `/api/app-version`, `/api/mobile-config`

## Nowe Komponenty (Etap 2)

### Mobile Config Component (NEW!)
- **Ścieżka**: `components/config/mobile-config.html`
- **Strona testowa**: `test-mobile-config.html`
- **API Endpoints**:
  - `GET /api/mobile-config` - pobiera aktualną konfigurację MOBILE_APP_CONFIG
  - `POST /api/mobile-config` - zapisuje nową konfigurację mobilną
- **Konfigurowane opcje (11)**:
  - `timer_enabled` - timer czasu pracy na głównym ekranie
  - `daily_stats` - podsumowanie pracy z bieżącego dnia
  - `monthly_stats` - podsumowanie pracy z bieżącego miesiąca
  - `field_blocking` - blokada edycji ID pracownika podczas pracy
  - `gps_verification` - wymaganie aktywnej lokalizacji
  - `widget_support` - widget na ekran główny telefonu
  - `notifications` - powiadomienia o ważnych wydarzeniach
  - `offline_mode` - praca bez połączenia internetowego
  - `debug_mode` - dodatkowe informacje techniczne
  - `auto_updates` - automatyczne sprawdzanie aktualizacji
  - `forceUpdate` - wymuszenie aktualizacji dla wszystkich
- **Funkcjonalność**:
  - Panel informacyjny z statusem systemu i wersją
  - 4 sekcje konfiguracyjne z logicznym grupowaniem
  - Nowoczesne toggle switches z animacjami
  - Test konfiguracji przed zapisem
  - Licznik aktywnych ustawień
  - Pełna responsywność mobile-first
- **Status**: ✅ Gotowy - pełna funkcjonalność z API

### App Version Management Component (NEW!)
- **Ścieżka**: `components/config/app-version-management.html`
- **Strona testowa**: `test-app-version-management.html`
- **API Endpoints**:
  - `GET /api/app-version` - pobiera aktualne informacje o wersji
  - `POST /api/mobile-config` - zapisuje nową konfigurację wersji
- **Funkcjonalność**:
  - Wyświetla aktualny status wersji aplikacji mobilnej
  - Umożliwia konfigurację nowej wersji z walidacją
  - Zarządza listą nowych funkcji i ulepszeń
  - Opcja wymuszenia aktualizacji
  - System testowania konfiguracji
  - Auto-refresh statusu po zapisie
- **Status**: ✅ Gotowy - pełna funkcjonalność z API

## Dla Aplikacji Mobilnej

Wszystkie powyższe API są dostępne dla aplikacji mobilnej. Kluczowe endpoints:

### Podstawowe dla aplikacji mobilnej:
1. `POST /api/login` - logowanie
2. `GET /api/employees/{id}` - dane pracownika  
3. `POST /api/attendance/check-in` - wejście
4. `POST /api/attendance/check-out` - wyjście
5. `GET /api/attendance/employee/{id}` - historia obecności
6. `GET /api/mobile/config` - konfiguracja aplikacji

## Uwagi dla rozwoju:
- Wszystkie API używają JSON
- Authentication przez session/token
- CORS skonfigurowany dla localhost
- Rate limiting może być aktywne
- API documentation dostępne pod `/api/docs` (jeśli istnieje)

---
*Ostatnia aktualizacja: 2025-08-07*
*Wersja: 2.0.0*
