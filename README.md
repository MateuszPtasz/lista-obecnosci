# Lista obecności

System zarządzania obecnością pracowników z aplikacją webową i mobilną.

## Struktura projektu

Pełna dokumentacja struktury projektu znajduje się w pliku [docs/STRUKTURA_KATALOGOW.md](docs/STRUKTURA_KATALOGOW.md).

## Uruchomienie systemu

### Wymagania

- Python 3.10 lub nowszy
- Flutter (dla rozwoju aplikacji mobilnej)
- SQLite

### Szczegółowe instrukcje uruchomienia

Szczegółowa instrukcja ręcznego uruchomienia systemu znajduje się w pliku:
[docs/INSTRUKCJA_URUCHOMIENIA_SYSTEMU.md](docs/INSTRUKCJA_URUCHOMIENIA_SYSTEMU.md)

### Szybkie uruchomienie (w środowisku wirtualnym)

1. Aktywuj środowisko wirtualne:
```powershell
.\venv\Scripts\activate
```

2. Uruchom główny serwer API:
```powershell
.\venv\Scripts\python.exe main.py --port 8000
```

3. W drugim terminalu uruchom zapasowy serwer API:
```powershell
.\venv\Scripts\activate
.\venv\Scripts\python.exe main.py --port 8002
```

### Konfiguracja aplikacji mobilnej

1. Zainstaluj aplikację z katalogu `releases/mobile/`
2. Adres serwera ustawiony jest na `192.168.1.30:8000` w pliku `mobile_app/lib/api.dart`

## Porty komunikacyjne

| Komponent | Port | Uwagi |
|-----------|------|-------|
| API dla aplikacji mobilnej | 8000 | Główny port API |
| Panel webowy | 8002 | Port panelu administratora |
| Port alternatywny | 8080 | Używany w przypadku blokady portu 8000 |

## Dokumentacja

Pełna dokumentacja projektu znajduje się w katalogu [docs/](docs/).

## Status projektu

Aktualne informacje o statusie projektu i zaleceniach znajdują się w pliku [docs/BIEZACE_PRACE.md](docs/BIEZACE_PRACE.md).
