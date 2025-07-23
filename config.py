# Konfiguracja funkcji aplikacji mobilnej
# Te ustawienia można zmieniać bez przebudowy aplikacji

MOBILE_APP_CONFIG = {
    "timer_enabled": True,
    "daily_stats": False,
    "monthly_stats": False,
    "field_blocking": True,
    "gps_verification": True,
    "widget_support": False,
    "notifications": False,
    "offline_mode": True,
    "debug_mode": True,
    "auto_updates": False,
    "forceUpdate": False,
}

# Wersja konfiguracji - zwiększaj przy zmianach
CONFIG_VERSION = "1.1"

# Konfiguracja email
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",  # Zmień na swój serwer SMTP
    "smtp_port": 587,
    "smtp_username": "",  # Uzupełnij swój email
    "smtp_password": "",  # Uzupełnij hasło aplikacji (nie zwykłe hasło!)
    "sender_email": "",   # Email nadawcy
    "sender_name": "System Lista Obecności",
    "enabled": False      # Ustaw True aby włączyć wysyłanie emaili
}

# Informacje o aktualnej wersji aplikacji mobilnej
APP_VERSION_INFO = {
    "current_version": "1.0.0",  # Aktualna wersja w Play Store
    "minimum_version": "1.0.0",  # Minimalna wymagana wersja
    "update_required": False,    # Czy aktualizacja jest wymagana
    "update_message": "Dostępna nowa wersja aplikacji z ulepszeniami!",
    "play_store_url": "https://play.google.com/store/apps/details?id=com.example.lista_obecnosci",  # ZMIEŃ NA PRAWDZIWY LINK
    "update_features": [
        "Nowy system konfiguracji zdalnej",
        "Ulepszony timer pracy",
        "Poprawki błędów i optymalizacja"
    ]
}
