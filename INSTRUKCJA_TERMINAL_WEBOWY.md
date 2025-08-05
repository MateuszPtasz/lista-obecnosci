# Narzędzia diagnostyczne dla terminala webowego

## Problem
Terminal na stronie pulpitu nie obsługuje standardowych poleceń `.bat` oraz ma problemy z przyciskiem "sesja".

## Rozwiązanie - nowe skrypty diagnostyczne
Przygotowano specjalne skrypty dostosowane do pracy w terminalu webowym:

### 1. Diagnostyka konfiguracji
```
python diagnoza_web_terminal.py
```
Ten skrypt:
- Sprawdza plik konfiguracyjny
- Testuje import konfiguracji
- Sprawdza dostępność API
- Analizuje środowisko terminala

### 2. Naprawa sesji
```
python naprawa_sesji.py
```
Ten skrypt:
- Diagnozuje problemy z sesją
- Sprawdza połączenie z bazą danych
- Testuje API autoryzacji
- Usuwa wygasłe sesje z bazy danych
- Sugeruje rozwiązania problemu z przyciskiem "sesja"

### 3. Diagnostyka środowiska terminala
```
powershell -ExecutionPolicy Bypass -File diagnostyka_terminal.ps1
```
Ten skrypt:
- Analizuje środowisko PowerShell
- Sprawdza uprawnienia do plików
- Testuje wykonywanie poleceń
- Identyfikuje problemy z terminalem

## Instrukcje użycia

### W terminalu VS Code:
Standardowo używaj plików .bat:
```
.\diagnoza_konfiguracji.bat
.\test_permissions.bat
```

### W terminalu webowym:
Używaj skryptów Python:
```
python diagnoza_web_terminal.py
python naprawa_sesji.py
```

## Rozwiązywanie problemów z przyciskiem "sesja"

1. Uruchom diagnostykę sesji:
   ```
   python naprawa_sesji.py
   ```

2. Zrestartuj serwery:
   ```
   python restart_web_servers.py
   ```

3. Wyczyść dane sesji w przeglądarce (ciasteczka i dane lokalne)

4. Zaloguj się ponownie w aplikacji

## Informacje dodatkowe

- Problemy z przyciskiem "sesja" mogą wynikać z konfliktów w bazie danych sesji lub nieprawidłowej autoryzacji
- Terminal webowy działa w innym kontekście niż terminal VS Code, co może powodować problemy z uruchamianiem plików .bat
- W przypadku dalszych problemów z sesją, wykonaj pełny restart serwerów i przeglądarki
