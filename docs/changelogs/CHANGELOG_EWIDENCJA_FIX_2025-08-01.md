# CHANGELOG - Lista Obecności

## [FIXED] 01.08.2025 - Poprawki widoku aktywnych pracowników i ewidencji

### ✅ Poprawiony widok aktywnych pracowników
- Pracownicy z aktywnymi zmianami są teraz prawidłowo oznaczani jako "Online"
- Dodano pole `status` w API, które jednoznacznie określa status pracownika
- Zaktualizowano front-end, aby uwzględniał nowe pole statusu

### ✅ Poprawiona ewidencja obecności
- Dodano brakujące pola w endpoincie `/api/attendance_summary`:
  - `days_present` - liczba dni obecności
  - `saturdays` - liczba sobót przepracowanych
  - `sundays` - liczba niedziel przepracowanych
  - `holidays` - liczba dni świątecznych (do przyszłej implementacji)
  - `rate` - stawka godzinowa pracownika

### ✅ Dodany moduł obsługi dziennika obecności
- Utworzono nowy plik `logs.py` z modułem obsługującym dziennik obecności
- Zaimplementowano endpoint `/api/logs` do dodawania pojedynczych wpisów
- Zaimplementowano endpoint `/api/logs/batch` do dodawania wielu wpisów jednocześnie
- Dodano obsługę przekierowań dla zachowania kompatybilności ze starszymi wersjami

### 🔄 Modularyzacja API
- Wydzielono routery z endpointami do osobnych plików
- Podłączono routery do głównej aplikacji

### 📝 Uwagi
- Dziennik obecności teraz wykorzystuje tabelę `shifts` zamiast starej tabeli `attendance_logs`
- Zaimplementowano pełną obsługę dodawania wpisów w dzienniku, zarówno pojedynczo, jak i zbiorowo
- Udoskonalono formatowanie czasu pracy w interfejsie
