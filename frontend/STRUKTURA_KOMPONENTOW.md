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

## 🌐 API używane przez komponenty
- GET /api/workers; POST /api/workers; PUT /api/worker/{id}; DELETE /api/workers/{id}; DELETE /api/workers/batch; POST /api/import_employees_csv
- POST /api/start; POST /api/stop; POST /api/admin/force-stop
- GET /api/workers/status; GET /api/active_workers

## 🧪 Strony testowe
- frontend/work-test.html — test work-management
- frontend/worker-status-search-test.html — test statusów
- frontend/employees-list-test.html — test listy pracowników

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
- Edycja pracownika w komponencie używa danych z listy (bez GET /api/worker/{id}); zapis przez PUT z credentials:'include'.

## 📌 Uwagi
- Używamy ścieżek względnych /api/... dla zgodności ciasteczek.
- Modale przenosimy pod body i nadajemy wysoki z-index (uniknięcie kolizji ze sticky header).
- Guardy init zapobiegają wielokrotnemu bindowaniu zdarzeń.
