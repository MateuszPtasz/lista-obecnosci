# Instrukcja konfiguracji firewalla dla systemu Lista Obecności

## Problemy z połączeniem aplikacji mobilnej

Jeśli aplikacja mobilna nie może połączyć się z serwerem API, najprawdopodobniej Windows Firewall blokuje połączenia przychodzące. Poniższe instrukcje pomogą skonfigurować firewall, aby umożliwić komunikację z aplikacją mobilną.

## Automatyczna konfiguracja firewalla

Najłatwiejszy sposób to użycie dołączonego skryptu automatycznej konfiguracji:

1. Kliknij prawym przyciskiem myszy na plik `fix_firewall.bat` w katalogu głównym aplikacji
2. Wybierz "Uruchom jako administrator"
3. Potwierdź okno kontroli konta użytkownika (UAC) jeśli się pojawi
4. Poczekaj na zakończenie konfiguracji - powinien pojawić się komunikat o sukcesie

Ten skrypt automatycznie doda reguły dla portów używanych przez system (obecnie port główny i alternatywny zdefiniowane w `configs/app_config.py`).

## Ręczna konfiguracja firewalla

Jeśli automatyczny skrypt nie działa, możesz skonfigurować firewall ręcznie:

1. Otwórz Panel sterowania Windows
2. Przejdź do System i zabezpieczenia > Zapora systemu Windows Defender > Ustawienia zaawansowane
3. Kliknij prawym przyciskiem myszy na "Reguły przychodzące" i wybierz "Nowa reguła..."
4. Wybierz typ reguły "Port" i kliknij "Dalej"
5. Wybierz "TCP" i "Określone porty lokalne"
6. Wpisz porty zdefiniowane w pliku `configs/app_config.py` oraz port panelu webowego (domyślnie 8000, 8080 i 8002) oddzielone przecinkami
7. Kliknij "Dalej"
8. Wybierz "Zezwalaj na połączenie" i kliknij "Dalej"
9. Zaznacz wszystkie profile sieci (Domena, Prywatna, Publiczna) i kliknij "Dalej"
10. Nadaj regule nazwę (np. "Lista Obecności - Serwer API") i kliknij "Zakończ"

## Sprawdzanie konfiguracji firewalla

Aby sprawdzić, czy reguły zostały poprawnie dodane:

1. Otwórz PowerShell jako administrator
2. Wpisz komendy: 
   - `netsh advfirewall firewall show rule name="Lista Obecnosci Server - Port 8000"`
   - `netsh advfirewall firewall show rule name="Lista Obecnosci Server - Port 8080"`
   - `netsh advfirewall firewall show rule name="Lista Obecnosci Server - Port 8002"`
3. Powinna pojawić się informacja o regule - jeśli nie, oznacza to, że reguła nie została dodana

## Problemy z konfiguracją firewalla

Jeśli nadal występują problemy z konfiguracją firewalla:

1. Upewnij się, że uruchamiasz skrypty jako administrator
2. Sprawdź, czy Windows Defender Firewall jest włączony
3. Spróbuj tymczasowo wyłączyć firewall, aby sprawdzić czy to jest przyczyną problemu (tylko do testów!)
4. Sprawdź logi firewalla w Podglądzie zdarzeń Windows (Dzienniki systemu Windows > Bezpieczeństwo)

## Aktualizacja portów

Jeśli zmienisz porty w pliku konfiguracyjnym `configs/app_config.py`, pamiętaj o ponownym uruchomieniu skryptu konfiguracji firewalla, aby zaktualizować reguły dla nowych portów.
