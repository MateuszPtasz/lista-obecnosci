# Changelog aplikacji mobilnej - 02.08.2025

## Wersja 1.2.3+5 (02.08.2025)

### Dodano
- System automatycznych ponownych prób połączenia
- Konfigurowalny limit czasu połączenia
- Obsługa błędów sieciowych z wyświetlaniem komunikatów

### Naprawiono
- Problem z połączeniem w zakładce "Konfiguracja"
- Problem z długim czasem oczekiwania przy problemach z połączeniem
- Problem z brakiem obsługi błędów sieciowych

### Zmiany techniczne
- Zaktualizowano klasę `ApiService` z dodaniem metody `fetchWithRetry`
- Dodano stałą `timeoutSeconds` do konfiguracji API
- Zaktualizowano logikę obsługi błędów w endpoincie `/mobile-config` po stronie serwera

### Pliki instalacyjne
- Nowy plik APK: `lista-obecnosci-app-20250802-002.apk`
- Poprzedni plik APK: `lista-obecnosci-app-20250802-001.apk`
