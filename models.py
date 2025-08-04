# models.py

# Tutaj będą modele ORM

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
import datetime as dt

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True)  # Zmienione z Integer na String, aby obsługiwać ID jak JAN001
    start_time = Column(DateTime, default=dt.datetime.utcnow)
    stop_time = Column(DateTime, nullable=True)
    start_location = Column(String, nullable=True)
    stop_location = Column(String, nullable=True)
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    stop_latitude = Column(Float, nullable=True)
    stop_longitude = Column(Float, nullable=True)
    duration_min = Column(Integer, nullable=True)
    status = Column(String, nullable=True, default="Obecny")   # Obecny/Nieobecny/itp.
    is_holiday = Column(Boolean, nullable=True, default=False) # Czy to urlop
    is_sick = Column(Boolean, nullable=True, default=False)    # Czy to zwolnienie lekarskie

class Rate(Base):
    __tablename__ = "rates"

    employee_id = Column(Integer, primary_key=True, index=True)
    regular_rate = Column(Float, default=25.0)
    saturday_rate = Column(Float, default=37.5)
    sunday_rate = Column(Float, default=50.0)

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, index=True)
    start_time = Column(DateTime)
    start_lat = Column(Float)
    start_lon = Column(Float)
    stop_time = Column(DateTime, nullable=True)
    stop_lat = Column(Float, nullable=True)
    stop_lon = Column(Float, nullable=True)
    is_holiday = Column(String, default="nie")  # urlop: tak/nie
    is_sick = Column(String, default="nie")     # chorobowe: tak/nie/zus

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)  # Akceptuje litery i cyfry
    name = Column(String)
    pin = Column(String, nullable=False, index=True)  # PIN do logowania
    password_hash = Column(String, nullable=True)     # Hash hasła do panelu admina
    is_admin = Column(Boolean, default=False)         # Czy użytkownik jest adminem
    hourly_rate = Column(Float)
    rate_saturday = Column(Float, default=0.0)
    rate_sunday = Column(Float, default=0.0)
    rate_night = Column(Float, default=0.0)
    rate_overtime = Column(Float, default=0.0)

class DeviceLog(Base):
    __tablename__ = "device_logs"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, index=True)  # ID pracownika
    device_id = Column(String, index=True)  # Unikalny ID urządzenia 
    device_model = Column(String)           # np. "Samsung Galaxy S21"
    os_version = Column(String)             # np. "Android 13"
    app_version = Column(String)            # Wersja aplikacji
    location = Column(String, nullable=True)  # Lokalizacja tekstowa
    
    # Status bezpieczeństwa
    is_approved = Column(Boolean, default=False)   # Czy urządzenie jest zatwierdzone
    is_suspicious = Column(Boolean, default=False) # Czy jest podejrzane
    user_rejected = Column(Boolean, default=False) # Czy użytkownik kliknął "NIE" w popup
    
    # Znaczniki czasu
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)

class StatisticsAccessLog(Base):
    __tablename__ = "statistics_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, index=True)          # ID pracownika
    device_id = Column(String, index=True)          # Unikalny ID urządzenia
    device_model = Column(String)                   # Model urządzenia
    pin_entered = Column(String)                    # Wprowadzony PIN
    pin_correct = Column(Boolean)                   # Czy PIN był poprawny
    access_granted = Column(Boolean, default=False) # Czy udzielono dostępu
    ip_address = Column(String, nullable=True)      # Adres IP
    
    # Dane lokalizacyjne
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_text = Column(String, nullable=True)
    
    # Znaczniki czasu
    attempted_at = Column(DateTime, default=dt.datetime.utcnow)

class DeviceSecurityAlert(Base):
    __tablename__ = "device_security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, index=True)          # ID pracownika
    old_device_id = Column(String)                  # Poprzednie urządzenie
    new_device_id = Column(String)                  # Nowe urządzenie
    old_device_model = Column(String, nullable=True)
    new_device_model = Column(String, nullable=True)
    alert_type = Column(String)                     # "DEVICE_CHANGE", "SUSPICIOUS_ACCESS"
    is_resolved = Column(Boolean, default=False)    # Czy alert został rozwiązany
    admin_notes = Column(String, nullable=True)     # Notatki administratora
    
    # Znaczniki czasu
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String)                    # Typ akcji, np. FORCE_STOP, DELETE_USER, itp.
    admin_id = Column(String, index=True)           # ID administratora
    target_id = Column(String, nullable=True)       # ID docelowego pracownika/obiektu
    notes = Column(String, nullable=True)           # Dodatkowe notatki
    ip_address = Column(String, nullable=True)      # Adres IP administratora
    
    # Znaczniki czasu
    created_at = Column(DateTime, default=dt.datetime.utcnow)
