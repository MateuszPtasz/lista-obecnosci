# schemas.py

# Tutaj będą schematy Pydantic

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Location(BaseModel):
    lat: float
    lon: float

class StartShift(BaseModel):
    employee_id: str
    czas_start: datetime
    lokalizacja_start: Location

class StopShift(BaseModel):
    employee_id: str
    czas_stop: datetime
    lokalizacja_stop: Location

class ShiftStart(BaseModel):
    employee_id: int
    start_location: Optional[str] = None

class ShiftStop(BaseModel):
    employee_id: int
    stop_location: Optional[str] = None

class Pracownik(BaseModel):
    numer: str
    imie: str
    nazwisko: str
    stawka: float
    sobota_bonus: float = 0.5
    niedziela_bonus: float = 1.0

class EmployeeUpdate(BaseModel):
    first_name: str
    last_name: str
    pin: str  # PIN do logowania (4-6 cyfr)
    rate: float
    rate_saturday: float = 0.0
    rate_sunday: float = 0.0
    rate_night: float = 0.0
    rate_overtime: float = 0.0

class EmployeeCreate(BaseModel):
    id: str  # ID może zawierać litery i cyfry
    name: str
    pin: str  # PIN do logowania
    hourly_rate: float
    rate_saturday: float = 0.0
    rate_sunday: float = 0.0
    rate_night: float = 0.0
    rate_overtime: float = 0.0

class EmployeeLogin(BaseModel):
    employee_id: str  # ID lub PIN
    pin: str  # PIN do weryfikacji

class AttendanceLogCreate(BaseModel):
    worker_id: str
    start_time: datetime
    stop_time: datetime
    start_lat: float
    start_lon: float
    stop_lat: float
    stop_lon: float
    is_holiday: str = "nie"  # urlop: tak/nie
    is_sick: str = "nie"     # chorobowe: tak/nie/zus

class AttendanceLogUpdate(BaseModel):
    start_time: Optional[str] = None
    stop_time: Optional[str] = None
    is_holiday: Optional[str] = None
    is_sick: Optional[str] = None

class EmailReport(BaseModel):
    to_email: str
    subject: str
    report_type: str  # "pdf" lub "excel"
    report_data: str  # Base64 encoded data
    employee_name: str = None
    date_range: str = None

class DeviceInfo(BaseModel):
    device_id: str           # Unikalny ID urządzenia
    device_model: str        # np. "Samsung Galaxy S21"
    os_version: str          # np. "Android 13"
    app_version: str         # Wersja aplikacji
    location: Optional[str] = None  # Lokalizacja tekstowa

class DeviceRegistration(BaseModel):
    worker_id: str
    device_info: DeviceInfo
    user_action: str  # "approved", "rejected" - czy użytkownik kliknął TAK/NIE

class DeviceResponse(BaseModel):
    is_new_device: bool
    requires_confirmation: bool
    device_registered: bool
    message: str
    status: str  # "approved", "rejected", "pending"
