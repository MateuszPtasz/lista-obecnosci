# Instrukcja terminala webowego - rozwiązywanie problemów

## Typowe problemy w terminalu webowym

### 1. Problem: Polecenie `.\diagnoza_konfiguracji.bat` nie działa

**Rozwiązanie:**
```
python diagnoza_web_terminal.py
```

Terminal webowy nie obsługuje poleceń z kropką na początku (.\) lub plików .bat. Zamiast tego używaj bezpośrednio skryptów Python, które zostały specjalnie przygotowane dla terminala webowego.

### 2. Problem: Przycisk "sesja" nie działa

**Rozwiązanie:**

1. Sprawdź czy serwery są rzeczywiście uruchomione na komputerze (poza terminalem webowym)

2. Uruchom diagnostykę sesji:
   ```
   python naprawa_sesji.py
   ```

3. Spróbuj wyczyścić dane sesji w przeglądarce (ciasteczka i dane lokalne)

4. Zaloguj się ponownie w aplikacji

5. Jeśli problem nadal występuje, spróbuj zrestartować serwery:
   ```
   python restart_web_servers.py
   ```

## Dostępne narzędzia dla terminala webowego

| Polecenie w VS Code | Polecenie w terminalu webowym |
|---------------------|-------------------------------|
| `.\diagnoza_konfiguracji.bat` | `python diagnoza_web_terminal.py` |
| `.\test_permissions.bat` | `python test_permissions.py` |
| `.\restart_servers.bat` | `python restart_web_servers.py` |

## Diagnostyka połączenia z serwerami

Jeśli terminal webowy nie może połączyć się z serwerami, ale serwery są uruchomione, może to być spowodowane:

1. **Ograniczeniami bezpieczeństwa** - terminal webowy może mieć ograniczony dostęp do lokalnych portów
2. **Różnym kontekstem wykonania** - terminal webowy działa w innym kontekście sieciowym niż VS Code
3. **Blokowaniem cross-origin** - przeglądarka może blokować połączenia między różnymi domenami

**Rozwiązanie:**

W takiej sytuacji najlepiej używać standardowego terminala w VS Code do diagnostyki i zarządzania serwerami, a terminal webowy tylko do prostych zadań, które nie wymagają dostępu do lokalnych serwerów.

## Uruchamianie serwerów

Aby uruchomić serwery z poziomu VS Code, użyj:

```
.\start_servers_new.bat
```

lub

```powershell
# W PowerShell:
.\.venv\Scripts\activate; python start_api_servers.py
```

## Rozwiązywanie problemów z sesją

Jeśli masz problemy z sesją lub przyciskiem "sesja":

1. Sprawdź czy tabela sesji istnieje w bazie danych
2. Wyczyść dane sesji w przeglądarce
3. Zrestartuj serwery
4. Zaloguj się ponownie

Jeśli problem nadal występuje, może to wymagać interwencji administratora - być może tabela sesji nie została poprawnie utworzona w bazie danych.
