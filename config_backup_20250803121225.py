# Konfiguracja funkcji aplikacji mobilnej
# Te ustawienia można zmieniać bez przebudowy aplikacji

MOBILE_APP_CONFIG = {
    "timer_enabled": True,
    "daily_stats": True,
    "monthly_stats": True,
    "field_blocking": True,
    "gps_verification": False,
    "widget_support": False,
    "notifications": True,
    "offline_mode": True,
    "debug_mode": True,
    "auto_updates": False,
    "forceUpdate": False,
    "test_timestamp": "20250803120107",
}

# Wersja konfiguracji - zwiększaj przy zmianach
CONFIG_VERSION = "20250803-121205"

# Konfiguracja zaokrąglania czasu pracy
TIME_ROUNDING_CONFIG = {
    "enabled": False,              # Czy zaokrąglanie jest włączone
    "rounding_minutes": 15,        # Co ile minut zaokrąglać (5, 10, 15, 30, 60)
    "rounding_direction": "nearest", # "up" - w górę, "down" - w dół, "nearest" - do najbliższego
    "start_time_rounding": True,   # Zaokrąglaj czas rozpoczęcia pracy
    "end_time_rounding": True,     # Zaokrąglaj czas zakończenia pracy
    "max_early_minutes": 30,       # Maksymalnie ile minut wcześniej można się zalogować
    "max_late_minutes": 30,        # Maksymalnie ile minut później można się zalogować
    "apply_to_breaks": False,      # Czy zaokrąglać też przerwy
}

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
