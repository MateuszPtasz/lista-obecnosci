# Lista obecności - Bieżące prace i zalecenia

## Aktualny status prac (2 sierpnia 2025)

### Wykonane zadania:
1. ✅ Porządkowanie struktury projektu
2. ✅ Identyfikacja i usunięcie zbędnych plików
3. ✅ Analiza konfiguracji portów komunikacyjnych
4. ✅ Przygotowanie dokumentacji

### W toku:
1. 🔄 Przywracanie działania aplikacji po reorganizacji projektu
2. 🔄 Testowanie komunikacji między aplikacją mobilną a serwerem

### Do zrobienia:
1. ⏱️ Testowanie API po zmianach
2. ⏱️ Sprawdzenie poprawności działania aplikacji webowej
3. ⏱️ Wdrożenie rekomendacji bezpieczeństwa
4. ⏱️ Centralizacja konfiguracji portów

## Priorytetowe zadania

1. **Przywrócenie działania aplikacji**
   - Sprawdzić, czy wszystkie ścieżki importu działają poprawnie po reorganizacji
   - Zweryfikować dostępność wszystkich zasobów
   - Uruchomić serwery na odpowiednich portach

2. **Testowanie komunikacji**
   - Przetestować komunikację między aplikacją mobilną a serwerem (port 8000)
   - Przetestować działanie panelu webowego (port 8002)
   - Sprawdzić działanie alternatywnego portu (8080) w razie blokady

## Zalecenia techniczne

### Krótkoterminowe (do natychmiastowego wdrożenia)
1. **Centralizacja konfiguracji**:
   ```python
   # W pliku configs/app_config.py
   MOBILE_API_PORT = 8000
   WEB_PANEL_PORT = 8002
   ALTERNATIVE_PORT = 8080
   SERVER_IP = "192.168.1.30"
   ```

2. **Aktualizacja importów**:
   Sprawdzić wszystkie ścieżki importu w plikach, które zostały przeniesione do nowych katalogów.

3. **Monitorowanie logów**:
   Rozszerzyć logowanie, aby lepiej monitorować problemy z komunikacją.

### Średnioterminowe (do wdrożenia po stabilizacji)
1. **Dynamiczna konfiguracja adresu w aplikacji mobilnej**:
   ```dart
   // Propozycja zmian w mobile_app/lib/api.dart
   class ApiConfig {
     static String serverIp = "192.168.1.30";
     static int serverPort = 8000;
     
     static String get baseUrl => 'http://$serverIp:$serverPort';
     
     static Future<void> saveConfig(String ip, int port) async {
       // Zapisanie konfiguracji w SharedPreferences
     }
   }
   ```

2. **Zabezpieczenie API**:
   ```python
   # W pliku main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://192.168.1.30", "http://localhost"],
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"]
   )
   ```

3. **Mechanizm automatycznego wyboru portu**:
   ```python
   def find_available_port(preferred_port, max_attempts=10):
       """Znajdź dostępny port, zaczynając od preferowanego."""
       for port_offset in range(max_attempts):
           port = preferred_port + port_offset
           try:
               sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               sock.bind(("0.0.0.0", port))
               sock.close()
               return port
           except OSError:
               continue
       raise RuntimeError(f"Nie można znaleźć dostępnego portu po {max_attempts} próbach")
   ```

## Pytania i decyzje do podjęcia

1. **Czy utrzymywać dwa oddzielne porty dla API mobilnego i panelu webowego?**
   - Zalety: separacja ruchu, możliwość niezależnego skalowania
   - Wady: większa złożoność konfiguracji, więcej portów do zarządzania

2. **Czy przejść na dynamiczną konfigurację IP w aplikacji mobilnej?**
   - Zalety: łatwiejsza konfiguracja przez użytkowników, większa elastyczność
   - Wady: dodatkowy ekran konfiguracyjny, potencjalne problemy z walidacją

## Następne kroki

1. Uruchomienie serwerów z nową strukturą katalogów:
   ```powershell
   python start_api_servers.py
   ```

2. Test komunikacji aplikacji mobilnej:
   ```
   adb install releases/mobile/lista-obecnosci-app-20250802-001.apk
   ```

3. Dokumentacja zmian w repozytorium Git:
   ```powershell
   git add .
   git commit -m "Reorganizacja struktury projektu, optymalizacja komunikacji"
   git push origin feature/ui-improvements
   ```
