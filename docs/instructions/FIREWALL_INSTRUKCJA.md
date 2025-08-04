# INSTRUKCJA: Jak rozwiązać problem z połączeniem aplikacji mobilnej

## Problem
Aplikacja mobilna nie może połączyć się z serwerem z powodu blokady Windows Firewall.

## Rozwiązanie 1: Automatyczne (Najłatwiejsze)
1. Kliknij prawym przyciskiem na plik `add_firewall_rule.ps1` w folderze projektu
2. Wybierz "Uruchom w programie PowerShell"
3. Gdy pojawi się prośba UAC, kliknij "Tak"
4. Poczekaj na komunikat "SUCCESS"
5. Przetestuj aplikację mobilną

## Rozwiązanie 2: Ręczne
1. Naciśnij Windows + R
2. Wpisz: `wf.msc` i naciśnij Enter
3. Kliknij "Inbound Rules" (Reguły przychodzące)
4. Kliknij "New Rule..." (Nowa reguła)
5. Wybierz "Port" → Next
6. Wybierz "TCP" → "Specific local ports" → wpisz: 8000
7. Wybierz "Allow the connection" → Next
8. Zaznacz wszystkie profile (Domain, Private, Public) → Next
9. Nazwa: "Lista Obecnosci Server" → Finish

## Rozwiązanie 3: Przez PowerShell (Administrator)
Uruchom PowerShell jako Administrator i wykonaj:
```
netsh advfirewall firewall add rule name="Lista Obecnosci Server" dir=in action=allow protocol=TCP localport=8000
```

## Sprawdzenie czy działa:
1. Uruchom aplikację mobilną
2. Kliknij przycisk "🔧 TEST POŁĄCZENIA Z SERWEREM"
3. Powinien pojawić się komunikat "✅ Połączenie OK!"

## W razie problemów:
- Upewnij się, że telefon i komputer są w tej samej sieci WiFi
- Sprawdź IP komputera: `ipconfig` w cmd (powinno być 192.168.1.30)
- Sprawdź czy serwer działa: otwórz http://localhost:8000/workers w przeglądarce
