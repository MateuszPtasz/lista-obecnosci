# Konfiguracja portów komunikacyjnych - Aplikacja "Lista obecności"

Na podstawie analizy kodu źródłowego zidentyfikowano następujące porty używane przez system:

## Porty komunikacyjne

| Komponent | Port | Plik konfiguracyjny | Uwagi |
|-----------|------|---------------------|-------|
| API dla aplikacji mobilnej | **8000** | `main.py` + `start_api_servers.py` | Główny port API używany przez aplikację mobilną |
| Panel webowy | **8002** | `start_api_servers.py` | Port używany przez panel webowy |
| Port alternatywny | **8080** | `server_alt_port.py` | Port alternatywny używany w przypadku blokowania portu 8000 |

## Konfiguracja adresu w aplikacji mobilnej

Obecna konfiguracja w pliku `mobile_app/lib/api.dart` wskazuje na:
```dart
String get baseUrl {
  return 'http://192.168.1.30:8000'; // IP komputera w sieci WiFi
}
```

## Jak działa komunikacja

1. **Aplikacja mobilna → Serwer**:
   - Aplikacja mobilna łączy się z adresem IP `192.168.1.30` na porcie `8000`
   - Ten port jest obsługiwany przez główny plik `main.py` (uruchamiany przez `start_api_servers.py`)

2. **Panel webowy**:
   - Panel webowy korzysta z portu `8002`
   - Ten port jest obsługiwany przez `server_alt_port.py` (uruchamiany przez `start_api_servers.py`)

3. **Port alternatywny**:
   - W przypadku problemów z komunikacją na porcie `8000`, można uruchomić serwer na porcie `8080` za pomocą `server_alt_port.py`
   - Ten port alternatywny został wprowadzony w celu obejścia ewentualnych blokad zapory Windows

## Uwagi dotyczące konfiguracji

1. **Zalecenie bezpieczeństwa**: 
   - Obecna konfiguracja CORS pozwala na dostęp z dowolnego źródła (`allow_origins=["*"]`), co może być ryzykowne. 
   - Zalecane jest ograniczenie dostępu tylko do niezbędnych źródeł.

2. **Konfiguracja adresu IP**:
   - Adres IP `192.168.1.30` jest zakodowany na stałe w aplikacji mobilnej
   - W przypadku zmiany konfiguracji sieci konieczna może być aktualizacja aplikacji mobilnej

3. **Zarządzanie wieloma instancjami**:
   - Skrypt `start_api_servers.py` umożliwia uruchomienie obu serwerów jednocześnie i zarządzanie nimi
   - Serwery uruchamiane są jako osobne procesy, co zapewnia niezależność działania

## Zalecenia

1. **Zewnętrzna konfiguracja portów**:
   - Zaleca się przeniesienie konfiguracji portów do zewnętrznego pliku konfiguracyjnego (np. `config.py` lub `.env`)
   - Pozwoli to na łatwiejszą zmianę portów bez konieczności modyfikacji kodu źródłowego

2. **Dynamiczna konfiguracja adresu w aplikacji mobilnej**:
   - Zaleca się wprowadzenie ekranu konfiguracyjnego w aplikacji mobilnej
   - Umożliwi to użytkownikom zmianę adresu IP i portu bez konieczności rekompilacji aplikacji

3. **Zabezpieczenie API**:
   - Zaleca się ograniczenie dostępu CORS tylko do niezbędnych źródeł
   - Zaleca się wprowadzenie mechanizmu autentykacji API (np. tokeny JWT)

4. **Monitorowanie portów**:
   - Zaleca się dodanie funkcji monitorującej dostępność portów przed uruchomieniem serwera
   - Pozwoli to na wcześniejsze wykrycie konfliktów portów i automatyczne wybranie portu alternatywnego
