# Zmiany w systemie (2025-08-01)

## Poprawiono wyświetlanie statusu aktywnych pracowników

### Problem
Pracownicy z aktywnymi zmianami (tzn. rozpoczęli pracę, ale jej nie zakończyli) byli oznaczani jako "offline" w interfejsie, pomimo że w bazie danych byli prawidłowo zapisani jako aktywni.

### Rozwiązanie

1. Dodano pole `status` z wartością "online" w odpowiedzi endpointu `/api/active_workers` dla aktywnych pracowników.

   ```python
   # Zmodyfikowano funkcję get_active_workers w pliku attendance.py
   active_workers.append({
       "id": employee.id,
       "name": employee.name,
       "start_time": shift.start_time.strftime("%H:%M") if shift.start_time else "-",
       "shift_id": shift.id,
       "location": shift.start_location or "Nieznana",
       "status": "online",  # Dodany status online
       "coordinates": {
           "lat": shift.start_latitude,
           "lon": shift.start_longitude
       } if shift.start_latitude and shift.start_longitude else None
   })
   ```

2. Poprawiono logikę w interfejsie użytkownika, aby wykorzystać pole `status` lub domyślnie uznać pracowników za aktywnych.

   ```javascript
   // Zmieniona logika w pliku index.html
   const statusBadge = (worker.status === "online" || !worker.status) 
       ? '<span class="status status-present"><i class="fas fa-circle"></i> Online</span>'
       : '<span class="status status-absent"><i class="fas fa-circle"></i> Offline</span>';
   ```

### Dodatkowe narzędzia diagnostyczne

Stworzono następujące narzędzia diagnostyczne:

1. `check_active_workers_db.py` - do sprawdzania aktywnych zmian bezpośrednio w bazie danych
2. `debug_active_workers.py` - do testowania logiki endpointu aktywnych pracowników

### Weryfikacja

Potwierdzono, że wszystkie 3 aktywne zmiany (dla pracowników: admin, 1111, 2222) są prawidłowo widoczne jako "Online" w interfejsie.
