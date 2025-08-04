# Centralny plik konfiguracyjny dla portów i adresów IP
# Używaj tego pliku zamiast hardkodowania wartości w kodzie

# Konfiguracja portów API
APP_PORT_MAIN = 8000        # Port dla aplikacji mobilnej (główny)
APP_PORT_ALT = 8080         # Zapasowy port (np. gdy 8000 jest zajęty)
WEB_PANEL_PORT = 8002       # Port dla panelu webowego

# Konfiguracja adresów IP
APP_DEFAULT_IP = "192.168.1.35"  # Główny adres IP serwera (zmień na swój lokalny adres)
LOOPBACK_IP = "127.0.0.1"        # Adres localhost
LISTEN_ALL_IP = "0.0.0.0"        # Nasłuchiwanie na wszystkich interfejsach

# Konfiguracja URL-i
MOBILE_API_URL = f"http://{APP_DEFAULT_IP}:{APP_PORT_MAIN}"
WEB_PANEL_URL = f"http://{APP_DEFAULT_IP}:{WEB_PANEL_PORT}"
ALTERNATIVE_URL = f"http://{APP_DEFAULT_IP}:{APP_PORT_ALT}"

# Lista wszystkich URL-i do testów
API_URLS = [
    f"http://{APP_DEFAULT_IP}:{APP_PORT_MAIN}",
    f"http://{LOOPBACK_IP}:{APP_PORT_MAIN}",
    f"http://{APP_DEFAULT_IP}:{WEB_PANEL_PORT}",
    f"http://{LOOPBACK_IP}:{WEB_PANEL_PORT}",
    f"http://{APP_DEFAULT_IP}:{APP_PORT_ALT}",
]

# Ustawienia timeout-ów
API_TIMEOUT_SECONDS = 10    # Timeout dla zapytań API
CONNECTION_RETRY_COUNT = 3  # Liczba prób połączenia przy błędzie
