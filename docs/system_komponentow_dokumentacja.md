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

Uwagi dot. autoryzacji:
- W testowych stronach bez logowania żądania admina (np. PUT /api/worker/{id}) mogą zwracać 401.
- Komponent employees-list ładuje dane do edycji z aktualnej listy (brak GET /api/worker/{id}); zapis (PUT) używa fetch z credentials:'include'.

## Jak uruchomić test komponentu

- Otwórz stronę testową w przeglądarce, np.:
  - http://localhost:8080/frontend/work-test.html
  - http://localhost:8080/frontend/worker-status-search-test.html
  - http://localhost:8080/frontend/employees-list-test.html
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
- frontend/work-test.html
- frontend/worker-status-search-test.html
- frontend/employees-list-test.html

## Notatki implementacyjne

- Wszystkie wywołania API używają ścieżek względnych /api/... (ten sam origin), aby przeglądarka przesyłała ciasteczka sesji.
- Operacje modyfikujące (PUT/POST/DELETE) powinny stosować credentials:'include'.
- Modale (Add/Edit) są przenoszone pod <body> i mają wysoki z-index, aby uniknąć konfliktów z sticky headerami tabel.
