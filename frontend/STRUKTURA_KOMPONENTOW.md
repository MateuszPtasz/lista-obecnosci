# 🧩 Struktura Komponentów - Lista Obecności

## 📁 Organizacja Katalogów

```
frontend/
├── components/
│   ├── common/           # Komponenty wielokrotnego użytku
│   ├── dashboard/        # Komponenty pulpitu głównego
│   ├── employees/        # Komponenty zarządzania pracownikami
│   ├── attendance/       # Komponenty obecności (daily-view, summary-table)
│   └── config/          # Komponenty konfiguracji (planowane)
├── assets/              # Systemy ładowania komponentów
├── js/                  # Narzędzia JS (ComponentUtils)
└── styles/              # Style CSS
```

## ✅ Gotowe Komponenty

### 🏠 Dashboard Components (`/components/dashboard/`)

#### 1. **stats-overview.html** 
- **Cel**: Wyświetlanie głównych statystyk systemu
- **API**: `/api/dashboard/stats`
- **Funkcje**: 
  - Liczba pracowników
  - Aktywne sesje
  - Dzisiejsze zakończone zmiany
  - Przepracowane godziny
- **Auto-odświeżanie**: Co 30 sekund

#### 2. **quick-actions.html**
- **Cel**: Szybkie akcje administracyjne
- **Funkcje**:
  - Dodaj nowego pracownika
  - Przejdź do ewidencji
  - Panel administracyjny
  - Raporty systemu
- **Nawigacja**: Linki do różnych sekcji

#### 3. **recent-activity.html**
- **Cel**: Historia ostatnich aktywności
- **API**: `/api/recent-activities`
- **Funkcje**:
  - Ostatnie logowania/wylogowania
  - Zmiany w systemie
  - Timeline wydarzeń
- **Auto-odświeżanie**: Co 60 sekund

#### 4. **work-management.html**
- **Cel**: Zarządzanie czasem pracy pracowników
- **API**: `/api/start`, `/api/stop`, `/api/emergency-stop`
- **Funkcje**:
  - Rozpocznij pracę dla pracownika
  - Zakończ pracę
  - Awaryjne zakończenie
- **Formularze**: Obsługa PIN i lokalizacji

#### 5. **active-workers.html**
- **Cel**: Monitoring obecnie pracujących osób
- **API**: `/api/active_workers`
- **Funkcje**:
  - Lista aktywnych pracowników
  - Czas pracy w czasie rzeczywistym
  - Możliwość zakończenia pracy
- **Auto-odświeżanie**: Co 15 sekund

### 🌐 Common Components (`/components/common/`)

#### 6. **calendar-widget.html**
- **Cel**: Kalendarz z wskaźnikami obecności
- **API**: `/api/attendance/calendar`
- **Funkcje**:
  - Nawigacja miesięczna
  - Kolorowe wskaźniki obecności
  - Responsywny grid
- **Integracja**: Uniwersalne użycie w różnych stronach

### 👥 Employees Components (`/components/employees/`)

#### 7. **employee-search.html**
- **Cel**: Wyszukiwanie i filtrowanie pracowników
- **API**: `/api/employees/search`, `/api/employees/counts`
- **Funkcje**:
  - Wyszukiwanie po imieniu/nazwisku/PIN
  - Szybkie filtry (aktywni, nieaktywni, nowi)
  - Live search z debouncing
- **Wydarzenia**: Komunikacja z employee-list

#### 8. **employee-list.html**
- **Cel**: Lista pracowników z zarządzaniem
- **API**: `/api/employees`, `/api/employees/{id}`
- **Funkcje**:
  - Karty pracowników z detalami
  - Paginacja wyników
  - Modal szczegółów
  - Akcje (edycja, aktywacja, dezaktywacja)
- **Responsywność**: Adaptuje się do różnych rozdzielczości

#### 9. **employee-details.html**
- **Cel**: Szczegółowy widok pojedynczego pracownika z obecnością
- **API**: `/api/worker/{id}`, `/api/attendance_details`, `/logs`
- **Funkcje**:
  - Profil pracownika z stawkami
  - Tabela obecności z edycją
  - Dodawanie nowych wpisów
  - Eksport i drukowanie
  - Podsumowanie godzin i kwot

## 🛠️ Systemy Wspierające

### Component Loader (`/assets/component-loader.js`)
- **Funkcja**: Dynamiczne ładowanie komponentów HTML
- **Cache**: Optymalizacja powtórnych ładowań
- **Error Handling**: Obsługa błędów ładowania

### Component Utils (`/js/component-utils.js`)
- **API Calls**: Bezpieczne wywołania API z obsługą błędów
- **Formatting**: Narzędzia formatowania dat i liczb
- **Logging**: System logowania dla debugowania
- **UI Helpers**: Animacje, notyfikacje, spinner

### Unified Styling (`/styles/components.css`)
- **Consistent Design**: Zunifikowany wygląd wszystkich komponentów
- **Responsive Grid**: Elastyczne układy
- **Theme System**: Spójne kolory i typografia

## 📋 Planowane Komponenty

### Dashboard Extensions
- [ ] **system-health.html** - Monitoring zdrowia systemu
- [ ] **notifications-panel.html** - Panel powiadomień
- [ ] **weather-widget.html** - Widget pogodowy

### Employee Management
- [x] **employee-details.html** - Szczegółowy widok pracownika z obecnością
- [ ] **employee-stats.html** - Statystyki pracownika
- [ ] **employee-actions.html** - Akcje zarządzania
- [ ] **employee-schedule.html** - Harmonogram pracy

### Attendance Tracking
- [x] **daily-view.html** - Widok obecności dla wybranego dnia
- [x] **summary-table.html** - Ewidencja obecności z zakresem dat i eksportem
- [ ] **attendance-calendar.html** - Kalendarz obecności
- [ ] **attendance-reports.html** - Raporty obecności
- [ ] **time-tracking.html** - Śledzenie czasu

### Configuration
- [ ] **mobile-config.html** - Konfiguracja aplikacji mobilnej
- [ ] **system-settings.html** - Ustawienia systemowe
- [ ] **user-preferences.html** - Preferencje użytkownika

## 🏗️ Architektural Patterns

### Component Structure
```html
<div class="component [component-name]-component">
  <div class="component-header">
    <h3><i class="fas fa-icon"></i> Tytuł</h3>
    <div class="component-actions"><!-- Akcje --></div>
  </div>
  <div class="component-body">
    <!-- Zawartość komponentu -->
  </div>
</div>
```

### JavaScript Pattern
```javascript
(function() {
  'use strict';
  
  // State management
  let componentState = {};
  
  // Initialization
  function initComponent() {
    ComponentUtils.log('Component: Inicjalizacja', 'info');
    bindEvents();
    loadData();
  }
  
  // Event binding
  function bindEvents() { /* ... */ }
  
  // Data loading
  async function loadData() { /* ... */ }
  
  // Auto-initialization
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComponent);
  } else {
    initComponent();
  }
})();
```

### CSS Naming Convention
```css
/* Component wrapper */
.component-name-component { }

/* Component sections */
.component-name-component .component-header { }
.component-name-component .component-body { }

/* Component elements */
.component-name-component .element-name { }
.component-name-component .element-name.modifier { }

/* States */
.component-name-component.loading { }
.component-name-component.error { }
```

## 🔧 Usage Examples

### Loading Single Component
```html
<div id="stats-container" class="component-container">
  <div class="loading-spinner">Ładowanie...</div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async function() {
  await window.ComponentLoader.loadComponent(
    'components/dashboard/stats-overview.html',
    '#stats-container'
  );
});
</script>
```

### Loading Multiple Components
```javascript
const components = [
  { file: 'components/dashboard/stats-overview.html', container: '#stats' },
  { file: 'components/dashboard/quick-actions.html', container: '#actions' },
  { file: 'components/dashboard/recent-activity.html', container: '#activity' }
];

const loadPromises = components.map(comp => 
  window.ComponentLoader.loadComponent(comp.file, comp.container)
);

await Promise.all(loadPromises);
```

## 📊 Component Status Matrix

| Component | Status | API Ready | Tests | Documentation |
|-----------|---------|-----------|-------|---------------|
| stats-overview | ✅ Done | ✅ Yes | 🟡 Basic | ✅ Complete |
| quick-actions | ✅ Done | ✅ Yes | 🟡 Basic | ✅ Complete |
| recent-activity | ✅ Done | ✅ Yes | 🟡 Basic | ✅ Complete |
| work-management | ✅ Done | ✅ Yes | 🟡 Basic | ✅ Complete |
| active-workers | ✅ Done | ✅ Yes | 🟡 Basic | ✅ Complete |
| calendar-widget | ✅ Done | 🟡 Partial | 🟡 Basic | ✅ Complete |
| employee-search | ✅ Done | 🔴 No | 🔴 None | ✅ Complete |
| employee-list | ✅ Done | 🔴 No | 🔴 None | ✅ Complete |

**Legenda:**
- ✅ Done/Complete
- 🟡 Partial/In Progress  
- 🔴 Not Started/Missing

## 🚀 Next Steps

1. **API Integration**: Dokończyć endpointy dla employee components
2. **Testing**: Dodać testy jednostkowe dla komponentów  
3. **Performance**: Optymalizacja ładowania i cache
4. **Documentation**: Dodać przykłady użycia i troubleshooting
5. **Monitoring**: Dodać metrics i performance tracking

---

*Ostatnia aktualizacja: 7 sierpnia 2025*
