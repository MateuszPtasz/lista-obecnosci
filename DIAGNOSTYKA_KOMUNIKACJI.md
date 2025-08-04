# DIAGNOSTYKA KOMUNIKACJI APLIKACJI

## Narzędzia do diagnostyki

W systemie Lista Obecności dodano nowe narzędzia diagnostyczne, które pomagają w rozwiązywaniu problemów z komunikacją między aplikacją mobilną a serwerem API.

### 1. Endpoint diagnostyczny `/api/connection-test`

Dodano nowy endpoint, który pozwala na sprawdzenie komunikacji z API:

```
GET /api/connection-test
```

Przykładowa odpowiedź:
```json
{
  "status": "ok",
  "message": "API działa poprawnie",
  "timestamp": "2025-08-04 12:34:56.789012",
  "hostname": "SERVER-01",
  "server_info": {
    "api_version": "1.2.5",
    "python_version": "3.10.5",
    "endpoints_available": [
      "/api/workers",
      "/api/mobile-config",
      "/api/app-version",
      "/api/connection-test"
    ]
  }
}
```

### 2. Diagnostyka API w aplikacji mobilnej

W aplikacji mobilnej dodano nowy ekran diagnostyczny, który pozwala na sprawdzenie wszystkich aspektów komunikacji z serwerem:

- Test połączenia internetowego
- Test podstawowego połączenia z serwerem
- Test diagnostyczny API
- Test pobierania konfiguracji
- Test zapisywania konfiguracji
- Test pobierania wersji aplikacji
- Test endpointu pracowników

Aby uruchomić diagnostykę w aplikacji mobilnej:
1. Przejdź do ekranu ustawień
2. Wybierz opcję "Diagnostyka API"
3. Naciśnij przycisk odświeżania, aby uruchomić testy

### 3. Narzędzie diagnostyczne dla administratorów

Dla administratorów systemu przygotowano skrypt diagnostyczny, który sprawdza połączenie z serwerem:

```
diagnostyka_api.bat
```

Ten skrypt:
- Sprawdza wymagane pakiety Pythona
- Testuje połączenie z każdym serwerem API (porty 8000 i 8002)
- Sprawdza dostępność wszystkich endpointów API
- Generuje szczegółowy raport diagnostyczny

## Rozwiązywanie typowych problemów

### Problem: "Method Not Allowed" podczas zapisywania konfiguracji

Ten błąd występuje, gdy:
1. Aplikacja próbuje użyć metody POST na endpoincie, który obsługuje tylko GET
2. Adresy URL w aplikacji mobilnej nie mają spójnego formatowania (brak lub nadmiar prefiksu `/api/`)

**Rozwiązanie:**
- Upewnij się, że endpoint `/api/mobile-config` obsługuje metodę POST
- Sprawdź w pliku `api.dart`, czy funkcja `saveMobileConfig` używa poprawnego adresu URL
- Użyj funkcji pomocniczej `buildApiUrl` do tworzenia poprawnych adresów URL

### Problem: Brak komunikacji między aplikacją mobilną a serwerem

**Rozwiązanie:**
1. Uruchom narzędzie diagnostyczne w aplikacji mobilnej
2. Sprawdź czy serwer API jest uruchomiony (`diagnostyka_api.bat`)
3. Upewnij się, że adres IP serwera w aplikacji mobilnej jest poprawny
4. Sprawdź ustawienia firewalla na serwerze

## Logi diagnostyczne

Wszystkie problemy z komunikacją są zapisywane w pliku `api_logs.log`. Aby włączyć szczegółowe logowanie diagnostyczne, ustaw `ENABLE_DIAGNOSTICS = True` w pliku `api_config.py`.
