# Zmiany w aplikacji mobilnej (2025-08-03)

## Poprawki API i komunikacji z serwerem

### Zmiany w endpointach serwera
- Zaktualizowano endpoint `/api/mobile-config` do zwracania standardowego formatu konfiguracji
- Zaktualizowano endpoint `/api/app-version` do zwracania informacji o wersji w spójnym formacie
- Dodano obsługę danych urządzenia przy weryfikacji dostępu

### Zmiany w aplikacji mobilnej
- Zaktualizowano bibliotekę HTTP do wersji 1.2.1 (z 0.13.6)
- Zaktualizowano bibliotekę Geolocator do wersji 11.0.0 (z 10.1.0)
- Zaktualizowano bibliotekę Permission Handler do wersji 11.3.0 (z 11.0.0)
- Zaktualizowano bibliotekę URL Launcher do wersji 6.2.5 (z 6.2.2)
- Poprawiono obsługę odpowiedzi z API w różnych formatach
- Ulepszono obsługę błędów i wyświetlanie powiadomień użytkownikowi
- Dodano nowe funkcje bezpieczeństwa weryfikacji PIN i urządzenia

### Naprawione błędy
- Naprawiono problem z parsowaniem odpowiedzi z serwera przy nowym formacie JSON
- Naprawiono wyświetlanie pustych danych przy braku aktywnych zmian
- Poprawiono obsługę błędów połączenia i ponownych prób
- Poprawiono logikę synchronizacji danych w trybie offline

## Instrukcja aktualizacji
1. Zainstaluj najnowszą wersję aplikacji z pliku APK
2. Upewnij się, że serwer został zaktualizowany do najnowszej wersji
3. Przy pierwszym uruchomieniu możesz zostać poproszony o weryfikację urządzenia

## Znane problemy
- Na starszych urządzeniach (Android 6.0 i starsze) mogą występować problemy z lokalizacją
- W przypadku problemów z logowaniem, wyczyść dane aplikacji i zaloguj się ponownie

## Kolejne kroki rozwoju
- Dodanie widoku statystyk miesięcznych dla pracowników
- Poprawa interfejsu użytkownika dla ekranu głównego
- Dodanie wsparcia dla wielu języków
