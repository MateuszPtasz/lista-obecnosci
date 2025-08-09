# 🧩 Struktura Komponentów - Lista Obecności (aktualizacja 2025-08-09)

## 📁 Organizacja Katalogów

```
frontend/
├── components/
│   ├── common/
│   ├── dashboard/
│   ├── employees/
│   ├── attendance/
│   └── config/
├── styles/
├── js/
└── assets/
```

## ✅ Gotowe Komponenty (rzeczywiste)

### Dashboard (`/components/dashboard/`)
- work-management.html — sterowanie start/stop/awaryjne; guard na podwójne bindowanie
- active-workers.html — lista aktywnych z czasem trwania; odświeżanie
- worker-status-search.html — wyszukiwarka statusów, tabela z akcjami (Start/Stop/Emergency), tooltips, debouncing; fallbacki API
- recent-activity.html — ostatnie aktywności (z fallbackiem endpointu)

### Employees (`/components/employees/`)
- employees-list.html — nowoczesna lista pracowników
  - Toolbar: Odśwież, Dodaj (modal), Import CSV, Usuń zaznaczonych
  - Tabela: zaznaczanie, Edytuj (modal), Usuń (pojedynczo)
  - Import: POST /api/import_employees_csv (walidacja CSV)
  - Add: POST /api/workers (modal)
  - Edit: PUT /api/worker/{id} (modal, new_id zmienia ID, credentials:'include')
  - UX: modal pod body, wysoki z-index, body.scroll lock, sticky header fix

### Attendance (`/components/attendance/`)
- attendance-day.html — Obecność wybrany dzień (GET /api/attendance_by_date)
  - test: frontend/attendance-day-test.html
- attendance-summary.html — Ewidencja (GET /api/attendance_summary, employees_without_logs, POST /api/logs/batch)
  - test: frontend/attendance-summary-test.html
- employee-details.html — Szczegóły pracownika (GET /api/attendance_details, PATCH/DELETE /api/logs/{id})
  - test: frontend/employee-details-test.html

## 🌐 API używane przez komponenty
- GET /api/workers; POST /api/workers; PUT /api/worker/{id}; DELETE /api/workers/{id}; DELETE /api/workers/batch; POST /api/import_employees_csv
- POST /api/start; POST /api/stop; POST /api/admin/force-stop
- GET /api/workers/status; GET /api/active_workers
- GET /api/attendance_by_date; GET /api/attendance_summary; GET /api/attendance_details; GET /api/employees_without_logs; POST /api/logs/batch; PATCH/DELETE /api/logs/{id}

## 🧪 Strony testowe
- frontend/work-test.html — test work-management
- frontend/worker-status-search-test.html — test statusów
- frontend/employees-list-test.html — test listy pracowników
- frontend/attendance-day-test.html — test obecności dnia
- frontend/attendance-summary-test.html — test ewidencji
- frontend/employee-details-test.html — test szczegółów pracownika

## 🧱 Wzorzec komponentu (lightweight)
```html
<div class="card">...</div>
<script>(function(){
  const state={bound:false};
  function init(){ if(state.bound) return; state.bound=true; /* ... */ }
  window.NazwaKomponentu={ init };
})();</script>
```

## 🔐 Autoryzacja w trybie testowym
- Strony testowe nie wymuszają logowania admina.
- Operacje zapisu używają credentials:'include'.

## 📌 Uwagi
- Używamy ścieżek względnych /api/... dla zgodności ciasteczek.
- Guardy init zapobiegają wielokrotnemu bindowaniu zdarzeń.
- Komponenty mają spójny wizualnie styl; w przyszłości można podmienić globalny temat przez CSS variables.
