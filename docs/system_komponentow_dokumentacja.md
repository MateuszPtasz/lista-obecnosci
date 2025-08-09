# System komponentów — aktualny stan (2025-08-09)

Ten projekt korzysta z lekkiego podejścia do komponentów frontendowych:
- Każdy komponent to pojedynczy plik HTML ze stylami i skryptem JS w środku.
- Komponent wystawia globalny obiekt window.NazwaKomponentu z metodą init().
- Nie używamy osobnego ComponentLoader/ComponentUtils — testy odbywają się na dedykowanych stronach testowych.

## Gotowe komponenty i strony testowe

Dashboard:
- components/dashboard/work-management.html — zarządzanie czasem pracy (Start/Stop/Awaryjne)
  - test: frontend/work-test.html
- components/dashboard/active-workers.html — aktywni pracownicy (pulpit główny)
- components/dashboard/worker-status-search.html — wyszukiwarka i statusy pracowników (tabela z akcjami)
  - test: frontend/worker-status-search-test.html
- components/dashboard/recent-activity.html — ostatnie aktywności (z fallbackiem endpointu)

Pracownicy:
- components/employees/employees-list.html — lista pracowników z akcjami
  - funkcje: odświeżanie, dodawanie (modal), edycja (modal), import CSV, usuwanie pojedyncze i grupowe
  - test: frontend/employees-list-test.html

Obecność:
- components/attendance/attendance-day.html — Obecność wybrany dzień
  - test: frontend/attendance-day-test.html
- components/attendance/attendance-summary.html — Ewidencja czasu pracy (zakres dat, suma, eksporty, dodawanie dni pracy)
  - test: frontend/attendance-summary-test.html
- components/attendance/employee-details.html — Szczegóły pracownika (lista wpisów, edycja, hurtowa edycja, eksporty)
  - test: frontend/employee-details-test.html

Konfiguracja:
- components/config/mobile-config.html — Konfiguracja aplikacji mobilnej (przełączniki funkcji, bezpieczeństwo, interfejs, zaawansowane, aktualizacje)
  - test: frontend/mobile-config-test.html

Wspólne:
- components/common/status-message.html — System komunikatów (StatusMessage: success/error/warning/info/loading; hide/hideAll; updateProgress/updateMessage/completeLoading)
  - test: frontend/status-message-test.html

## API wykorzystywane przez komponenty

Pracownicy:
- GET /api/workers — lista pracowników
- POST /api/workers — dodanie pracownika (modal Add)
- PUT /api/worker/{id} — edycja danych pracownika (modal Edit, pole new_id zmienia ID)
- DELETE /api/workers/{id} — usuwanie pojedynczego pracownika
- DELETE /api/workers/batch — usuwanie grupowe (tablica ID)
- POST /api/import_employees_csv — import CSV (format 4 kolumny: first_name,last_name,pin,hourly_rate)

Status/zmiany:
- POST /api/start, POST /api/stop, POST /api/admin/force-stop — akcje czasu pracy
- GET /api/workers/status — zbiorczy status pracowników (fallback: GET /api/employees + GET /api/active_workers)
- GET /api/active_workers — pracownicy aktualnie w pracy

Obecność:
- GET /api/attendance_by_date?date=YYYY-MM-DD — obecność dla dnia
- GET /api/attendance_summary?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD — ewidencja zbiorcza
- GET /api/attendance_details?worker_id={id}&date_from=...&date_to=... — szczegóły pracownika (logs + summary)
- GET /api/employees_without_logs?date_from=...&date_to=... — pracownicy bez logów w okresie (do dodania dni pracy)
- POST /api/logs/batch — dodawanie wielu dni pracy jednocześnie
- PATCH /api/logs/{id} — edycja wpisu (czas/typ dnia)
- DELETE /api/logs/{id} — usunięcie wpisu

Konfiguracja mobilna:
- GET /api/mobile-config — pobranie konfiguracji mobilnej (MOBILE_APP_CONFIG lub { config: {...} })
- POST /api/mobile-config — zapis konfiguracji mobilnej ({ MOBILE_APP_CONFIG: {...} })
- GET /api/app-version — pobranie informacji o wersji aplikacji (current/minimum/url/komunikat)
- POST /api/app-version — zapis informacji o wersji ({ version_info: {...} })

Uwagi dot. autoryzacji:
- W testowych stronach bez logowania żądania admina mogą zwracać 401 — operacje zapisu używają fetch z credentials:'include'.
- Tam gdzie to możliwe komponenty korzystają z danych już załadowanych (np. edycja pracownika z listy) by zredukować dodatkowe GET.

## Jak uruchomić test komponentu

- Otwórz stronę testową w przeglądarce, np.:
  - http://localhost:8080/frontend/work-test.html
  - http://localhost:8080/frontend/worker-status-search-test.html
  - http://localhost:8080/frontend/employees-list-test.html
  - http://localhost:8080/frontend/attendance-day-test.html
  - http://localhost:8080/frontend/attendance-summary-test.html
  - http://localhost:8080/frontend/employee-details-test.html
  - http://localhost:8080/frontend/mobile-config-test.html
  - http://localhost:8080/frontend/status-message-test.html
- Strony testowe dynamicznie dołączają plik komponentu i wywołują window.Komponent.init().

## Wzorzec komponentu (skrót)

```html
<div class="card">...UI...</div>
<script>(function(){
  const state = { bound:false };
  function init(){ if(state.bound) return; state.bound = true; /* bindowanie i start */ }
  window.PrzykladKomponentu = { init };
})();</script>
```

## Struktura plików (istotne fragmenty)

- frontend/components/dashboard/work-management.html
- frontend/components/dashboard/active-workers.html
- frontend/components/dashboard/worker-status-search.html
- frontend/components/dashboard/recent-activity.html
- frontend/components/employees/employees-list.html
- frontend/components/attendance/attendance-day.html
- frontend/components/attendance/attendance-summary.html
- frontend/components/attendance/employee-details.html
- frontend/components/config/mobile-config.html
- frontend/components/common/status-message.html
- frontend/work-test.html
- frontend/worker-status-search-test.html
- frontend/employees-list-test.html
- frontend/attendance-day-test.html
- frontend/attendance-summary-test.html
- frontend/employee-details-test.html
- frontend/mobile-config-test.html
- frontend/status-message-test.html

## Notatki implementacyjne

- Wszystkie wywołania API używają ścieżek względnych /api/... (ten sam origin), aby przeglądarka przesyłała ciasteczka sesji.
- Operacje modyfikujące (PUT/POST/DELETE) powinny stosować credentials:'include'.
- Modale (Add/Edit) są przenoszone pod <body> i mają wysoki z-index, aby uniknąć konfliktów z sticky headerami tabel.
