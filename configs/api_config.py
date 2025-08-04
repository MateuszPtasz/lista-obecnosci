# Konfiguracja portów dla różnych interfejsów API
# Autor: GitHub Copilot, 2025-08-02

# Port 8000 - API dla aplikacji mobilnej
API_MOBILE_PORT = 8000

# Port 8002 - API dla panelu webowego
API_WEB_PORT = 8002

# Logowanie dla każdego interfejsu
API_MOBILE_LOG = "mobile_api.log"
API_WEB_LOG = "web_api.log"

# Parametry HTTP
MAX_REQUESTS = 100
TIMEOUT_SECONDS = 60

# Włączenie lub wyłączenie poszczególnych interfejsów
ENABLE_MOBILE_API = True
ENABLE_WEB_API = True

# Ustawienia CORS
CORS_ALLOW_ORIGINS = ["*"]
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
