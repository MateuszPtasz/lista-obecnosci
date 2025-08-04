# CHANGELOG - Lista Obecności

## [FIXED] 26.07.2025 - Naprawa aplikacji mobilnej

### ✅ Problem rozwiązany: Błąd połączenia w aplikacji mobilnej

**Przyczyna:**
- Brak uprawnień `INTERNET` w AndroidManifest.xml
- Aktywne sesje pracy blokujące nowe starty

**Rozwiązanie:**
1. Dodano uprawnienie `<uses-permission android:name="android.permission.INTERNET"/>` do AndroidManifest.xml
2. Dodano endpoint root `/` zwracający status API
3. Wyczyszczono aktywne sesje pracy w bazie danych
4. Zbudowano nową wersję APK z pełną funkcjonalnością

**Pliki zmienione:**
- `mobile_app/android/app/src/main/AndroidManifest.xml` - dodano uprawnienia internetowe
- `main.py` - dodano endpoint root, ulepszona walidacja sesji
- `check_active_sessions.py` - narzędzie do zarządzania aktywnymi sesjami

**Wersje działające:**
- `lista-obecnosci-app-INTERNET-20250726-2222.apk` - główna aplikacja
- `test-connection-app-INTERNET.apk` - aplikacja testowa

**Status:** ✅ APLIKACJA MOBILNA DZIAŁA POPRAWNIE
- Może rozpoczynać pracę
- Może kończyć pracę
- Połączenie z serwerem działa
- Walidacja pracowników działa
- Zapisywanie lokalizacji działa

**Kopia zapasowa:** `lista_obecnosci_WORKING_BACKUP_20250726-2229`
