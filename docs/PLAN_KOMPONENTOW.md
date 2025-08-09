# Plan Rozwoju Komponentów UI - Lista Obecności

> Rewizja: 09 sierpnia 2025 — dokument wyrównany do aktualnego stanu. Nieaktualne wpisy zachowane i oznaczone, aby było widać co jeszcze wymaga pracy lub weryfikacji.

## 📊 STATUS PROJEKTU (09 sierpnia 2025)
- ✅ AKTUALNE — zgodne ze stanem repo
- ⚠️ DO WERYFIKACJI — może wymagać dopracowania lub potwierdzenia
- ❌ NIEAKTUALNE — informacje historyczne (pozostawione celowo)

---

## 🎯 AKTUALNIE ZREALIZOWANE KOMPONENTY

### ✅ Navbar Component (AKTUALNE)
- Lokalizacja: `frontend/components/navigation/navbar.html`
- Status: ✅ MAMY — kompletne (glassmorphism)

### ✅ App Version Management Component (AKTUALNE)
- Lokalizacja: `frontend/components/config/app-version-management.html`
- Status: ✅ MAMY — pełne zarządzanie wersjami
- API: `GET /api/app-version` (odczyt, z credentials); zapis: `POST /api/mobile-config` (APP_VERSION_INFO) — zgodnie z obecnym serwerem
- Uwaga: istnieje też strona narzędziowa: `frontend/app_version_management.html` (refaktoryzowana, zgodna z powyższym API)

### ✅ Mobile Config Component (AKTUALNE)
- Lokalizacja: `frontend/components/config/mobile-config.html`
- Status: ✅ MAMY — 11 opcji konfiguracyjnych
- API: `/api/mobile-config` (GET/POST)

### ✅ Status Message System (AKTUALNE)
- Lokalizacja: `frontend/components/common/status-message.html`
- Status: ✅ MAMY — uniwersalny system komunikatów
- Typy: Success, Error, Warning, Info, Loading + `hide/hideAll/updateProgress/updateMessage/completeLoading`
- Strona testowa: `frontend/status-message-test.html` (NOWA)

### ✅ Modern Header Component (AKTUALNE)
- Lokalizacja: `frontend/components/common/header.html`
- Status: ✅ MAMY — nowoczesny header

### ✅ Login Component (Szkielet) (AKTUALNE)
- Lokalizacja: `frontend/components/auth/login.html`
- Status: ✅ MAMY — szkielet, DO WERYFIKACJI pod kątem integracji

### ✅ Add Employee Component (EN) (AKTUALNE)
- Lokalizacja: `frontend/components/pages/add-employee.html`
- Status: ✅ MAMY

### ✅ Dodaj Pracownika (PL) (AKTUALNE)
- Lokalizacja: `frontend/components/pages/dodaj-pracownika.html`
- Status: ✅ MAMY — z walidacją PESEL

### ✅ Dashboard Components — ODBUDOWANE! (AKTUALNE)
- Lokalizacja: `frontend/components/dashboard/`
- Ukończone:
  - `stats-overview.html`
  - `quick-actions.html`
  - `recent-activity.html`
  - `work-management.html`
  - `active-workers.html`
  - `calendar-widget.html`
  - `worker-status-search.html`
  - `terminal.html`
- Strony testowe: m.in. `frontend/work-test.html`, `frontend/worker-status-search-test.html`

### 👥 Employees (ZMIANA STATUSU — AKTUALNE)
- Poprzednio: ❌ UTRACONE (NIEAKTUALNE)
- Faktyczny stan: folder istnieje, mamy komponent listy pracowników
  - `frontend/components/employees/employees-list.html` — AKTUALNE
  - Strona testowa: `frontend/employees-list-test.html`
- Brak bezpośrednich plików: `employee-search.html`, `employee-details.html` w tym folderze
  - Zamiast „search” używamy: `components/dashboard/worker-status-search.html` (AKTUALNE)
  - „Szczegóły pracownika” dostępne jako: `components/attendance/employee-details.html` (patrz niżej)
  - Zadanie: ⚠️ DO WERYFIKACJI czy potrzebny jest osobny komponent „employees/employee-details.html”, czy utrzymujemy wariant w attendance

### 📅 Attendance (ZMIANA STATUSU — AKTUALNE)
- Poprzednio: ❌ UTRACONE (NIEAKTUALNE)
- Faktyczny stan: folder istnieje, komponenty są gotowe
  - `components/attendance/attendance-day.html` — test: `frontend/attendance-day-test.html`
  - `components/attendance/attendance-summary.html` — test: `frontend/attendance-summary-test.html`
  - `components/attendance/employee-details.html` — test: `frontend/employee-details-test.html`

---

## 📁 AKTUALNA STRUKTURA KOMPONENTÓW (AKTUALNE)
```
frontend/components/
├── navigation/
│   └── navbar.html ✅
├── config/
│   ├── app-version-management.html ✅
│   └── mobile-config.html ✅
├── common/
│   ├── status-message.html ✅
│   └── header.html ✅
├── auth/
│   └── login.html ✅ (szkielet)
├── pages/
│   ├── add-employee.html ✅
│   ├── dodaj-pracownika.html ✅
│   └── obecnosc.html ⚠️ DO WERYFIKACJI użycia
├── dashboard/
│   ├── stats-overview.html ✅
│   ├── quick-actions.html ✅
│   ├── recent-activity.html ✅
│   ├── work-management.html ✅
│   ├── active-workers.html ✅
│   ├── calendar-widget.html ✅
│   ├── worker-status-search.html ✅
│   └── terminal.html ✅
└── employees/
    └── employees-list.html ✅
```

---

## 🧪 Strony testowe (AKTUALNE)
- `frontend/work-test.html`
- `frontend/worker-status-search-test.html`
- `frontend/employees-list-test.html`
- `frontend/attendance-day-test.html`
- `frontend/attendance-summary-test.html`
- `frontend/employee-details-test.html`
- `frontend/mobile-config-test.html`
- `frontend/status-message-test.html` (NOWA)

---

## 📝 Rzeczy DO WERYFIKACJI / DO ZROBIENIA
- Employees:
  - Czy tworzymy osobny `employees/employee-details.html`, czy zostaje `attendance/employee-details.html`? (decyzja arch.)
  - Ewentualny „employee-search” — obecnie pokryty przez `dashboard/worker-status-search.html` (czy potrzebny duplikat?)
- Login component: integracja z realnym backendem i flow (⚠️)
- Konsolidacja UI: globalne zmienne CSS/temat i spójność stylów (⚠️)
- App Version Mgmt: utrzymać zapis przez `POST /api/mobile-config` (APP_VERSION_INFO) do czasu pojawienia się oficjalnego `POST /api/app-version` (⚠️)
- Dokumenty API: ujednolicić nazwy endpointów attendance (tam gdzie istnieją legacy/nowe) (⚠️)

---

## ❌ Sekcje historyczne (NIEAKTUALNE – zostawione dla kontekstu)

### ❌ Employees Components - UTRACONE! (NIEAKTUALNE)
- Aktualny stan: patrz rozdział „Employees (ZMIANA STATUSU — AKTUALNE)”

### ❌ Attendance Components - UTRACONE! (NIEAKTUALNE)
- Aktualny stan: patrz rozdział „Attendance (ZMIANA STATUSU — AKTUALNE)”

---
Status: 🟢 Dashboard: komplet | 🟢 Attendance: komplet | 🟡 Employees: lista gotowa, decyzja ws. szczegółów | 🟢 Config/Common: komplet
