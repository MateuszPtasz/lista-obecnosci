# Instrukcja aktualizacji aplikacji mobilnej "Lista obecności" (02.08.2025)

## Wersja 1.2.3+5 (02.08.2025)

### Zmiany w najnowszej wersji:
- Naprawiono problem z połączeniem w zakładce "Konfiguracja"
- Dodano lepszą obsługę błędów sieciowych
- Dodano system automatycznych ponownych prób połączenia
- Zwiększono stabilność połączenia z serwerem

### Instrukcja instalacji:

1. **Dla pracowników działu IT:**
   ```
   adb install -r releases/mobile/lista-obecnosci-app-20250802-002.apk
   ```

2. **Dla użytkowników:**
   - Odinstaluj poprzednią wersję aplikacji
   - Pobierz najnowszą wersję z wewnętrznego portalu firmy
   - Zainstaluj pobrany plik APK

### Rozwiązane problemy:
- Problem z błędem połączenia w zakładce "Konfiguracja"
- Problem z długim czasem oczekiwania przy problemach z połączeniem
- Problem z brakiem obsługi błędów sieciowych

### Uwagi:
- Po instalacji należy ponownie się zalogować
- W przypadku problemów z połączeniem, upewnij się że serwer na porcie 8000 jest dostępny
