from fastapi import FastAPI, Request, status, Depends, HTTPException, Form, File, UploadFile, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from database import get_db
from auth import verify_password, get_password_hash
import models
from typing import List, Dict, Optional
import secrets
import json
import datetime as dt
from datetime import timedelta
from config import TIME_ROUNDING_CONFIG
import logging
import os

# Konfiguracja logowania
LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)
logger = logging.getLogger("app")

def round_time(time_obj: dt.datetime, rounding_minutes: int, direction: str = "nearest") -> dt.datetime:
    """Zaokrąglanie czasu"""
    if not TIME_ROUNDING_CONFIG.get("enabled", False):
        return time_obj
    
    seconds_since_midnight = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    minutes_since_midnight = seconds_since_midnight / 60
    
    if direction == "up":
        rounded_minutes = ((minutes_since_midnight + rounding_minutes - 1) // rounding_minutes) * rounding_minutes
    elif direction == "down":
        rounded_minutes = (minutes_since_midnight // rounding_minutes) * rounding_minutes
    else:  # nearest
        rounded_minutes = round(minutes_since_midnight / rounding_minutes) * rounding_minutes
    
    rounded_hours = int(rounded_minutes // 60)
    rounded_mins = int(rounded_minutes % 60)
    
    if rounded_hours >= 24:
        rounded_hours = 23
        rounded_mins = 59
    
    return time_obj.replace(hour=rounded_hours, minute=rounded_mins, second=0, microsecond=0)

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Lista Obecności API",
    description="API do obsługi systemu listy obecności",
    version="1.0.0",
    default_response_class=JSONResponse,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Konfiguracja szablonów
templates = Jinja2Templates(directory="templates")

# Generuj tajny klucz dla sesji
SECRET_KEY = secrets.token_urlsafe(32)

# Lepsze logowanie dla sesji
print(f"Inicjalizuję sesje z kluczem SECRET_KEY (pierwsze 5 znaków): {SECRET_KEY[:5]}...")

# Konfiguracja middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="lista_obecnosci_session",
    max_age=7200  # Zwiększenie czasu życia sesji z 1h do 2h
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Endpoint do awaryjnego zakończenia pracy przez administratora
@app.post("/api/admin/force-stop")
async def force_stop_work(request: Request):
    """Awaryjne zakończenie pracy pracownika przez administratora"""
    print("Otrzymano żądanie awaryjnego zakończenia pracy")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        worker_id = data.get("worker_id")
        reason = data.get("reason", "Awaryjne zakończenie przez administratora")
        
        if not worker_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak ID pracownika"}
            )
        
        db = next(get_db())
        
        # Sprawdź czy pracownik istnieje
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Pracownik o ID {worker_id} nie istnieje"}
            )
        
        # Znajdź aktywną zmianę pracownika
        active_shift = db.query(models.Shift).filter(
            models.Shift.employee_id == worker_id,
            models.Shift.stop_time == None
        ).first()
        
        if not active_shift:
            # Jeśli nie znaleziono aktywnej zmiany, sprawdź, czy w ogóle pracownik miał jakieś zmiany
            any_shifts = db.query(models.Shift).filter(
                models.Shift.employee_id == worker_id
            ).order_by(models.Shift.start_time.desc()).first()
            
            if any_shifts:
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": f"Nie znaleziono aktywnej zmiany dla pracownika {worker_id}. " +
                                 f"Ostatnia zmiana zakończyła się {any_shifts.stop_time.strftime('%Y-%m-%d %H:%M:%S') if any_shifts.stop_time else 'nigdy'}"
                    }
                )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"Pracownik {worker_id} nie ma żadnych zarejestrowanych zmian"}
                )
        
        # Aktualizuj zmianę
        stop_time = dt.datetime.now()
        active_shift.stop_time = stop_time
        active_shift.stop_location = "Awaryjnie zakończone przez administratora"
        
        # Oblicz czas trwania w minutach
        duration = stop_time - active_shift.start_time
        duration_minutes = duration.total_seconds() // 60
        active_shift.duration_min = int(duration_minutes)
        
        # Dodaj log administracyjny
        try:
            admin_log = models.AdminLog(
                action_type="FORCE_STOP",
                admin_id=user.get("username", "admin"),
                target_id=str(worker_id),
                notes=f"Awaryjne zakończenie zmiany. Powód: {reason}. Shift ID: {active_shift.id}, Duration: {duration_minutes} min"
            )
            
            db.add(admin_log)
        except Exception as log_error:
            print(f"Ostrzeżenie: Nie udało się dodać logu administracyjnego: {log_error}")
            # Kontynuuj mimo błędu logu - ważniejsze jest zakończenie zmiany
        
        db.commit()
        
        # Przygotuj odpowiedź
        duration_str = f"{int(duration_minutes // 60)}h {int(duration_minutes % 60)}min"
        
        return {
            "status": "success",
            "message": f"Awaryjnie zakończono pracę pracownika {worker_id}",
            "duration": duration_str,
            "duration_min": int(duration_minutes)
        }
    except Exception as e:
        print(f"Błąd podczas awaryjnego kończenia pracy: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# WAŻNE: Najpierw definiujemy API endpoints, POTEM montujemy pliki statyczne

# Importy dla modularyzacji
from attendance import router as attendance_router
from logs import router as logs_router
from employees import router as employees_router

# Podłączenie routerów do aplikacji
app.include_router(attendance_router)
app.include_router(logs_router)
app.include_router(employees_router)

# Endpoint do sprawdzenia statusu pracownika
@app.get("/api/worker/{worker_id}/status")
async def get_worker_status(worker_id: str, request: Request):
    """Sprawdza status aktywnej zmiany pracownika"""
    try:
        db = next(get_db())
        
        # Sprawdź czy pracownik istnieje
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": "Pracownik nie istnieje"}
            )
        
        # Sprawdź aktywne zmiany
        active_shift = db.query(models.Shift).filter(
            models.Shift.employee_id == worker_id,
            models.Shift.stop_time == None
        ).first()
        
        result = {
            "worker_id": worker_id,
            "name": employee.name,
            "is_active": active_shift is not None
        }
        
        if active_shift:
            # Oblicz czas trwania zmiany
            duration = dt.datetime.now() - active_shift.start_time
            duration_minutes = duration.total_seconds() // 60
            duration_str = f"{int(duration_minutes // 60)}h {int(duration_minutes % 60)}min"
            
            result.update({
                "shift_id": active_shift.id,
                "start_time": active_shift.start_time.isoformat(),
                "duration": duration_str,
                "duration_minutes": int(duration_minutes),
                "start_location": active_shift.start_location
            })
        
        return result
    except Exception as e:
        print(f"Błąd podczas sprawdzania statusu pracownika: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Endpoint do pobierania statusu wszystkich pracowników
@app.get("/api/workers/status")
async def get_all_workers_status(request: Request):
    """Zwraca status wszystkich pracowników z informacją o aktywnych zmianach"""
    try:
        db = next(get_db())
        
        # Pobierz wszystkich pracowników
        employees = db.query(models.Employee).all()
        
        # Pobierz wszystkie aktywne zmiany
        active_shifts = db.query(models.Shift).filter(
            models.Shift.stop_time == None
        ).all()
        
        # Utwórz słownik z aktywnymi zmianami dla szybkiego dostępu
        active_shifts_dict = {shift.employee_id: shift for shift in active_shifts}
        
        result = []
        for employee in employees:
            worker_data = {
                "worker_id": employee.id,
                "name": employee.name,
                "is_active": employee.id in active_shifts_dict
            }
            
            # Dodaj szczegóły zmiany, jeśli pracownik jest aktywny
            if employee.id in active_shifts_dict:
                active_shift = active_shifts_dict[employee.id]
                duration = dt.datetime.now() - active_shift.start_time
                duration_minutes = duration.total_seconds() // 60
                duration_str = f"{int(duration_minutes // 60)}h {int(duration_minutes % 60)}min"
                
                worker_data.update({
                    "shift_id": active_shift.id,
                    "start_time": active_shift.start_time.isoformat(),
                    "duration": duration_str,
                    "duration_minutes": int(duration_minutes),
                    "start_location": active_shift.start_location
                })
            
            result.append(worker_data)
        
        # Posortuj wyniki - aktywni pracownicy na górze
        result.sort(key=lambda x: (not x["is_active"], x["name"]))
        
        return {"workers": result, "total": len(result), "active": len(active_shifts)}
    except Exception as e:
        print(f"Błąd podczas pobierania statusu pracowników: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Root endpoint
@app.get("/")
async def root():
    return RedirectResponse(url="/frontend")

@app.get("/admin")
async def admin_panel():
    return FileResponse("frontend/admin_panel.html")

@app.get("/api")
async def api_root():
    return {
        "message": "Lista Obecności API",
        "version": "1.0",
        "status": "running"
    }

# Przekierowania dla starych endpointów (bez prefiksu /api)
@app.get("/workers")
async def get_workers_redirect(request: Request):
    """Przekierowanie dla endpointu /workers"""
    print("Przekierowuję /workers do /api/workers")
    return await get_workers(request)

@app.get("/attendance_by_date")
async def get_attendance_by_date_redirect(request: Request, date: str):
    """Przekierowanie dla endpointu /attendance_by_date"""
    print(f"Przekierowuję /attendance_by_date do /api/attendance_by_date dla daty {date}")
    return RedirectResponse(url=f"/api/attendance_by_date?date={date}", status_code=307)

@app.get("/attendance_details")
async def get_attendance_details_redirect(request: Request, worker_id: str, date_from: str, date_to: str):
    """Przekierowanie dla endpointu /attendance_details"""
    print(f"Przekierowuję /attendance_details do /api/attendance_details dla pracownika {worker_id}, okres {date_from} - {date_to}")
    return RedirectResponse(url=f"/api/attendance_details?worker_id={worker_id}&date_from={date_from}&date_to={date_to}", status_code=307)

@app.get("/attendance_summary")
async def get_attendance_summary_redirect(request: Request, date_from: str, date_to: str):
    """Przekierowanie dla endpointu /attendance_summary"""
    print(f"Przekierowuję /attendance_summary do /api/attendance_summary dla okresu {date_from} - {date_to}")
    return RedirectResponse(url=f"/api/attendance_summary?date_from={date_from}&date_to={date_to}", status_code=307)

@app.get("/mobile-config")
async def get_mobile_config_redirect(request: Request):
    """Przekierowanie dla endpointu /mobile-config"""
    print("Przekierowuję /mobile-config do /api/mobile-config")
    return await get_mobile_config(request)

@app.post("/mobile-config")
async def update_mobile_config_endpoint(request: Request):
    """Aktualizacja konfiguracji aplikacji mobilnej z interfejsu administratora"""
    try:
        # Sprawdzanie uprawnień administratora
        user = request.session.get("user")
        if not user or user.get("role") != "admin":
            return JSONResponse(
                status_code=401,
                content={"detail": "Nieautoryzowany dostęp - wymagane uprawnienia administratora"}
            )
            
        # Parsowanie danych JSON z żądania
        data = await request.json()
        print(f"Otrzymano dane konfiguracyjne: {data}")
        
        if "APP_VERSION_INFO" not in data:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak wymaganych danych konfiguracyjnych (APP_VERSION_INFO)"}
            )
            
        # Aktualizacja plików konfiguracyjnych
        import os
        import re
        from datetime import datetime
        
        # Generowanie nowej wersji konfiguracji
        now = datetime.now()
        new_config_version = now.strftime("%Y%m%d-%H%M%S")
        
        # Ścieżki do plików konfiguracyjnych
        config_path = "config.py"
        central_config_path = "configs/app_config.py"
        
        # Sprawdzenie czy plik centralnej konfiguracji istnieje
        central_config_exists = os.path.exists(central_config_path)
        
        # Odczyt aktualnego pliku config.py
        if not os.path.exists(config_path):
            return JSONResponse(
                status_code=500,
                content={"detail": f"Nie znaleziono pliku konfiguracyjnego: {config_path}"}
            )
            
        # Najpierw aktualizujemy centralną konfigurację jeśli istnieje
        if central_config_exists:
            try:
                print(f"CONFIG: Aktualizacja centralnej konfiguracji {central_config_path}...")
                with open(central_config_path, "r", encoding="utf-8") as f:
                    central_config_content = f.read()
                    
                # Tworzenie kopii zapasowej centralnej konfiguracji
                central_backup_path = f"configs/app_config_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
                with open(central_backup_path, "w", encoding="utf-8") as f:
                    f.write(central_config_content)
                print(f"CONFIG: Utworzono kopię zapasową centralnej konfiguracji: {central_backup_path}")
                    
                # Aktualizacja zmiennej WEB_PANEL_URL w centralnej konfiguracji
                if "MOBILE_APP_CONFIG" in data:
                    web_panel_port = data["MOBILE_APP_CONFIG"].get("web_panel_port", 8002)
                    # Aktualizujemy wartość WEB_PANEL_PORT jeśli istnieje
                    if "WEB_PANEL_PORT =" in central_config_content:
                        central_config_content = re.sub(
                            r'WEB_PANEL_PORT\s*=\s*\d+', 
                            f'WEB_PANEL_PORT = {web_panel_port}', 
                            central_config_content
                        )
                
                # Zapisanie zaktualizowanej centralnej konfiguracji
                with open(central_config_path, "w", encoding="utf-8") as f:
                    f.write(central_config_content)
                print(f"CONFIG: Zaktualizowano centralną konfigurację {central_config_path}")
            except Exception as e:
                print(f"CONFIG: Błąd aktualizacji centralnej konfiguracji: {e}")
                import traceback
                print(traceback.format_exc())
            
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
        
        # Dodaj dodatkowe logowanie
        print(f"Generowanie nowej wersji konfiguracji: {new_config_version}")
        print(f"Długość oryginalnego pliku konfiguracyjnego: {len(config_content)} znaków")
        
        # Aktualizacja wersji konfiguracji
        config_content = re.sub(
            r'CONFIG_VERSION = "[^"]+"', 
            f'CONFIG_VERSION = "{new_config_version}"', 
            config_content
        )
        
        # Aktualizacja danych APP_VERSION_INFO
        new_version_info = data["APP_VERSION_INFO"]
        version_info_str = "APP_VERSION_INFO = {\n"
        version_info_str += f'    "current_version": "{new_version_info["current_version"]}",\n'
        version_info_str += f'    "minimum_version": "{new_version_info["minimum_version"]}",\n'
        version_info_str += f'    "update_required": {str(new_version_info["update_required"])},\n'
        version_info_str += f'    "update_message": "{new_version_info["update_message"]}",\n'
        version_info_str += f'    "play_store_url": "{new_version_info["play_store_url"]}",\n'
        
        # Dodanie funkcji
        features = new_version_info["update_features"]
        version_info_str += "    \"update_features\": [\n"
        for feature in features:
            version_info_str += f'        "{feature}",\n'
        version_info_str += "    ]\n}"
        
        # Aktualizacja konfiguracji aplikacji mobilnej, jeśli została dostarczona
        if "MOBILE_APP_CONFIG" in data:
            print("Aktualizowanie MOBILE_APP_CONFIG...")
            mobile_config = data["MOBILE_APP_CONFIG"]
            mobile_config_str = "MOBILE_APP_CONFIG = {\n"
            
            for key, value in mobile_config.items():
                # Konwersja wartości na odpowiedni format Pythona
                if isinstance(value, bool):
                    mobile_config_str += f'    "{key}": {str(value)},\n'
                elif isinstance(value, (int, float)):
                    mobile_config_str += f'    "{key}": {value},\n'
                else:
                    mobile_config_str += f'    "{key}": "{str(value)}",\n'
            
            mobile_config_str += "}"
            
            # Zastąpienie starej konfiguracji mobilnej
            config_content = re.sub(
                r'MOBILE_APP_CONFIG = \{[\s\S]*?\}',
                mobile_config_str,
                config_content
            )
        
        # Zastąp sekcję APP_VERSION_INFO w pliku
        config_content = re.sub(
            r'APP_VERSION_INFO = \{[\s\S]*?\}',
            version_info_str,
            config_content
        )
        
        # Sprawdź czy zmiany zostały zastosowane
        print(f"CONFIG: Sprawdzam czy APP_VERSION_INFO zostało zmienione...")
        if version_info_str.replace(" ", "").replace("\n", "") not in config_content.replace(" ", "").replace("\n", ""):
            print("CONFIG: UWAGA! Wyrażenie regularne nie zadziałało poprawnie dla APP_VERSION_INFO!")
            # Alternatywne podejście z użyciem indeksowania
            start_idx = config_content.find("APP_VERSION_INFO = {")
            if start_idx >= 0:
                end_idx = config_content.find("}", start_idx)
                if end_idx >= 0:
                    end_idx = config_content.find("}", end_idx + 1) + 1  # Znajdź koniec całej struktury
                    config_content = config_content[:start_idx] + version_info_str + config_content[end_idx+1:]
                    print("CONFIG: Zastosowano alternatywne podejście do aktualizacji APP_VERSION_INFO")
        
        # Utwórz kopię zapasową pliku konfiguracyjnego
        import time
        backup_path = f"config_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
        try:
            import shutil
            shutil.copy(config_path, backup_path)
            print(f"CONFIG: Utworzono kopię zapasową konfiguracji: {backup_path}")
        except Exception as backup_error:
            print(f"CONFIG: Ostrzeżenie: Nie można utworzyć kopii zapasowej: {backup_error}")
        
        # Wygeneruj unikalne tymczasowe hasło do weryfikacji
        verify_code = f"CONFIG_VERIFY_{int(time.time())}"
        config_content += f"\n\n# Kod weryfikacyjny: {verify_code}\n"
        
        # Zapisz zaktualizowany plik
        try:
            # Najpierw zapisz do pliku tymczasowego
            temp_config_path = f"config_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
            with open(temp_config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            print(f"CONFIG: Zapisano tymczasowy plik konfiguracyjny: {temp_config_path}")
            
            # Sprawdź czy plik tymczasowy został poprawnie zapisany
            if os.path.exists(temp_config_path):
                with open(temp_config_path, "r", encoding="utf-8") as verify_file:
                    verify_content = verify_file.read()
                if verify_code in verify_content and new_config_version in verify_content:
                    print(f"CONFIG: Weryfikacja pliku tymczasowego OK")
                    # Skopiuj plik tymczasowy do właściwego pliku konfiguracyjnego
                    shutil.copy(temp_config_path, config_path)
                    print(f"CONFIG: Zaktualizowano plik konfiguracyjny: {config_path}")
                    # Usuń plik tymczasowy
                    os.remove(temp_config_path)
                else:
                    print("CONFIG: BŁĄD - Plik tymczasowy nie zawiera oczekiwanych zmian!")
            else:
                print("CONFIG: BŁĄD - Nie udało się utworzyć pliku tymczasowego!")
                
            # Weryfikacja czy plik konfiguracyjny został poprawnie zapisany
            print(f"CONFIG: Weryfikacja zapisu pliku konfiguracyjnego...")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as verify_file:
                    verify_content = verify_file.read()
                if new_config_version in verify_content:
                    print(f"CONFIG: Weryfikacja OK - nowa wersja konfiguracji ({new_config_version}) znajduje się w pliku")
                    print(f"CONFIG: Zapisano nową konfigurację. Nowa wersja: {new_config_version}")
                else:
                    print("CONFIG: BŁĄD - Nowa wersja nie została znaleziona w zapisanym pliku!")
            else:
                print("CONFIG: BŁĄD - Plik konfiguracyjny nie istnieje po zapisie!")
        except Exception as save_error:
            print(f"CONFIG: BŁĄD zapisu pliku: {save_error}")
            raise save_error
        
        return {
            "status": "success",
            "message": "Konfiguracja aplikacji mobilnej została zaktualizowana",
            "config_version": new_config_version,
            "timestamp": str(datetime.now())
        }
        
    except Exception as e:
        import traceback
        print(f"ERROR: Błąd aktualizacji konfiguracji mobilnej: {e}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": f"Błąd aktualizacji konfiguracji: {str(e)}"
            }
        )

@app.get("/time-rounding-config")
async def get_time_rounding_config_redirect(request: Request):
    """Przekierowanie dla endpointu /time-rounding-config"""
    print("Przekierowuję /time-rounding-config do /api/time-rounding-config")
    return await get_time_rounding_config(request)

@app.get("/app-version")
async def get_app_version_redirect(request: Request):
    """Przekierowanie dla endpointu /app-version"""
    print("Przekierowuję /app-version do /api/app-version")
    return await get_app_version(request)

@app.get("/active_workers")
async def get_active_workers_redirect(request: Request):
    """Przekierowanie dla endpointu /active_workers"""
    print("Przekierowuję /active_workers do /api/active_workers")
    return RedirectResponse(url="/api/active_workers", status_code=307)

@app.post("/start")
async def start_work_redirect(request: Request):
    """Przekierowanie dla endpointu /start"""
    print("Przekierowuję /start do /api/start")
    return await start_work(request)

@app.post("/stop")
async def stop_work_redirect(request: Request):
    """Przekierowanie dla endpointu /stop"""
    print("Przekierowuję /stop do /api/stop")
    return await stop_work(request)

@app.post("/import_employees_csv")
async def import_employees_csv_redirect(request: Request):
    """Przekierowanie dla endpointu /import_employees_csv"""
    print("Przekierowuję /import_employees_csv do /api/import_employees_csv")
    return await import_employees_csv(request)

@app.post("/logs")
async def logs_redirect(request: Request):
    """Przekierowanie dla endpointu /logs"""
    print("Przekierowuję /logs do /api/logs")
    return await save_logs(request)

@app.post("/workers/batch")
async def batch_operations_redirect(request: Request):
    """Przekierowanie dla endpointu /workers/batch"""
    print("Przekierowuję /workers/batch do /api/workers/batch")
    return await batch_operations(request)

@app.get("/worker/{worker_id}")
async def get_worker_redirect(worker_id: str):
    """Przekierowanie dla endpointu /worker/{worker_id}"""
    print(f"Przekierowuję /worker/{worker_id} do /api/worker/{worker_id}")
    return RedirectResponse(url=f"/api/worker/{worker_id}", status_code=307)

@app.put("/worker/{worker_id}")
async def update_worker_redirect(worker_id: str):
    """Przekierowanie dla endpointu /worker/{worker_id} (PUT)"""
    print(f"Przekierowuję /worker/{worker_id} (PUT) do /api/worker/{worker_id}")
    return RedirectResponse(url=f"/api/worker/{worker_id}", status_code=307)

@app.post("/time-rounding-config")
async def update_time_rounding_config_redirect(request: Request):
    """Przekierowanie dla endpointu /time-rounding-config (POST)"""
    print("Przekierowuję /time-rounding-config (POST) do /api/time-rounding-config")
    return await update_time_rounding_config(request)

# API endpoints
@app.get("/api/session")
async def get_session(request: Request):
    """Sprawdź status sesji"""
    print("Sprawdzanie sesji...")
    user = request.session.get("user")
    if user:
        return {"authenticated": True, "user": user}
    return {"authenticated": False}

@app.post("/api/login")
async def api_login(request: Request):
    """Obsługa logowania przez API"""
    print("Otrzymano żądanie logowania")
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        print(f"Próba logowania dla użytkownika: {username}")
        
        # Dodajemy dokładniejsze logowanie dla celów diagnostycznych
        print(f"Dane logowania: username={username}, password={'*' * (len(password) if password else 0)}")
        
        db = next(get_db())
        
        # Zabezpieczenie przed None/pustymi wartościami
        if not username or not password:
            print("Brak nazwy użytkownika lub hasła")
            return JSONResponse(
                status_code=400,
                content={"detail": "Nazwa użytkownika i hasło są wymagane"}
            )
        
        # Szukamy użytkownika
        try:
            user = db.query(models.Employee).filter(models.Employee.id == username).first()
            print(f"Wynik zapytania o użytkownika: {user}")
        except Exception as db_err:
            print(f"Błąd podczas zapytania do bazy danych: {str(db_err)}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Problem z bazą danych: {str(db_err)}"}
            )
        
        if not user:
            print(f"Nie znaleziono użytkownika: {username}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Nieprawidłowy ID lub hasło"}
            )
            
        # Sprawdzamy czy użytkownik ma hash hasła
        if not user.password_hash:
            print(f"Użytkownik {username} nie ma ustawionego hasła (password_hash jest pusty)")
            return JSONResponse(
                status_code=401,
                content={"detail": "Konto nie zostało prawidłowo skonfigurowane. Skontaktuj się z administratorem."}
            )
        
        # Weryfikacja hasła
        try:
            is_valid = verify_password(password, user.password_hash)
            print(f"Weryfikacja hasła: {is_valid}")
        except Exception as pwd_err:
            print(f"Błąd podczas weryfikacji hasła: {str(pwd_err)}")
            return JSONResponse(
                status_code=500, 
                content={"detail": "Błąd weryfikacji hasła"}
            )
        
        if not is_valid:
            print("Nieprawidłowe hasło")
            return JSONResponse(
                status_code=401,
                content={"detail": "Nieprawidłowy ID lub hasło"}
            )
        
        print(f"Logowanie udane dla użytkownika: {username}")
        request.session["user"] = {
            "id": user.id,
            "name": user.name,
            "role": "admin" if user.is_admin else "employee"
        }
        
        return {"status": "success", "redirect": "/frontend/index.html"}
        
    except Exception as e:
        print(f"Błąd podczas logowania: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.post("/api/logs")
async def save_logs(request: Request):
    """Zapisuje logi z aplikacji"""
    print("Otrzymano żądanie zapisania logów")
    try:
        data = await request.json()
        
        # Tutaj możemy zapisać logi do pliku lub bazy danych
        log_type = data.get("type", "unknown")
        log_message = data.get("message", "")
        log_device = data.get("device", "")
        log_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[LOG] [{log_type}] [{log_timestamp}] [{log_device}]: {log_message}")
        
        # Opcjonalnie: zapis do bazy danych lub pliku
        with open("app_client_logs.log", "a", encoding="utf-8") as f:
            f.write(f"[{log_timestamp}] [{log_type}] [{log_device}]: {log_message}\n")
        
        return {"status": "success", "message": "Log zapisany"}
    except Exception as e:
        print(f"Błąd podczas zapisywania logów: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.post("/api/logout")
async def api_logout(request: Request):
    """Wylogowanie użytkownika"""
    print("Wylogowywanie użytkownika")
    request.session.clear()
    return {"status": "success"}

@app.post("/api/start")
async def start_work(request: Request):
    """Rozpoczęcie pracy przez pracownika"""
    print("Otrzymano żądanie rozpoczęcia pracy")
    
    # Sprawdź sesję
    user = request.session.get("user")
    
    # Jeśli nie ma sesji, sprawdź nagłówki - pozwalamy na dostęp z aplikacji mobilnej
    if not user:
        print("Brak sesji użytkownika, sprawdzam autoryzację mobilną...")
        # Dla aplikacji mobilnych pozwalamy na dostęp bez sesji
        try:
            # Dla aplikacji mobilnej uwierzytelnianie nie jest wymagane
            pass
        except Exception as e:
            print(f"Błąd autoryzacji mobilnej: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Nieautoryzowany dostęp"}
            )
    
    try:
        data = await request.json()
        worker_id = data.get("worker_id") or data.get("employee_id")
        if not worker_id and user:
            worker_id = user.get("id")
        if not worker_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak identyfikatora pracownika"}
            )
        location = data.get("location", "Nieznana") or data.get("lokalizacja_start", "Nieznana")
        start_lat = data.get("lat", None) 
        start_lon = data.get("lon", None)
        
        # Obsługa przypadku gdy lokalizacja jest w zagnieżdżonym obiekcie
        if not start_lat and not start_lon and isinstance(data.get("lokalizacja_start"), dict):
            loc_data = data.get("lokalizacja_start")
            start_lat = loc_data.get("lat")
            start_lon = loc_data.get("lon")
        
        print(f"Rozpoczęcie pracy dla {worker_id}, lokalizacja: {location}, lat: {start_lat}, lon: {start_lon}")
        
        db = next(get_db())
        
        # Sprawdź, czy pracownik już rozpoczął pracę dzisiaj i nie zakończył
        today = dt.datetime.now().date()
        active_shift = db.query(models.Shift).filter(
            models.Shift.employee_id == worker_id,
            models.Shift.start_time >= dt.datetime.combine(today, dt.datetime.min.time()),
            models.Shift.stop_time == None
        ).first()
        
        if active_shift:
            return JSONResponse(
                status_code=400,
                content={"detail": "Pracownik już rozpoczął pracę i jej nie zakończył"}
            )
        
        # Utwórz nowy wpis w tabeli shifts
        new_shift = models.Shift(
            employee_id=worker_id,
            start_time=dt.datetime.now(),
            start_location=location,
            start_latitude=start_lat,
            start_longitude=start_lon
        )
        
        db.add(new_shift)
        db.commit()
        
        return {"status": "success", "message": "Rozpoczęto pracę", "shift_id": new_shift.id}
        
    except Exception as e:
        print(f"Błąd podczas rozpoczynania pracy: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.post("/api/stop")
async def stop_work(request: Request):
    """Zakończenie pracy przez pracownika"""
    print("Otrzymano żądanie zakończenia pracy")
    
    # Sprawdź sesję
    user = request.session.get("user")
    
    # Jeśli nie ma sesji, sprawdź nagłówki - pozwalamy na dostęp z aplikacji mobilnej
    if not user:
        print("Brak sesji użytkownika, sprawdzam autoryzację mobilną...")
        # Dla aplikacji mobilnych pozwalamy na dostęp bez sesji
        try:
            # Dla aplikacji mobilnej uwierzytelnianie nie jest wymagane
            print("Dostęp z aplikacji mobilnej dozwolony")
        except Exception as e:
            print(f"Błąd autoryzacji mobilnej: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Nieautoryzowany dostęp"}
            )
    
    try:
        data = await request.json()
        print(f"Otrzymane dane: {data}")
        
        # Obsługa ID pracownika
        worker_id = data.get("worker_id") or data.get("employee_id")
        if not worker_id and user:
            worker_id = user.get("id")
        if not worker_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak identyfikatora pracownika"}
            )
        
        # Obsługa lokalizacji - wsparcie zarówno dla formatu z panelu jak i z aplikacji mobilnej
        location = "Nieznana"
        stop_lat = None
        stop_lon = None
        
        # Sprawdź, czy lokalizacja jest w głównym obiekcie
        if "location" in data:
            location = data.get("location")
            
        # Sprawdź, czy lat/lon są w głównym obiekcie
        if "lat" in data and "lon" in data:
            stop_lat = data.get("lat")
            stop_lon = data.get("lon")
            
        # Sprawdź, czy jest zagnieżdżony obiekt lokalizacja_stop
        if isinstance(data.get("lokalizacja_stop"), dict):
            loc_data = data.get("lokalizacja_stop")
            
            # Jeśli nie ustawiono jeszcze lokalizacji, ustaw lokalizacja_stop jako string
            if location == "Nieznana" and "text" in loc_data:
                location = loc_data.get("text", "Nieznana")
                
            # Jeśli nie ustawiono jeszcze lat/lon, pobierz je z lokalizacja_stop
            if not stop_lat and not stop_lon:
                stop_lat = loc_data.get("lat")
                stop_lon = loc_data.get("lon")
        
        # Jeśli lokalizacja_stop jest stringiem, użyj go jako lokalizacji
        elif isinstance(data.get("lokalizacja_stop"), str) and location == "Nieznana":
            location = data.get("lokalizacja_stop")
        
        print(f"Zakończenie pracy dla {worker_id}, lokalizacja: {location}, lat: {stop_lat}, lon: {stop_lon}")
        
        db = next(get_db())
        
        # Znajdź aktywną zmianę pracownika
        today = dt.datetime.now().date()
        print(f"Szukam aktywnej zmiany dla {worker_id} od {today}")
        
        try:
            active_shift = db.query(models.Shift).filter(
                models.Shift.employee_id == worker_id,
                models.Shift.start_time >= dt.datetime.combine(today, dt.datetime.min.time()),
                models.Shift.stop_time == None
            ).first()
            
            if active_shift:
                print(f"Znaleziono aktywną zmianę dla {worker_id}, rozpoczętą o {active_shift.start_time}")
            else:
                print(f"Nie znaleziono aktywnej zmiany dla {worker_id} od {today}")
                # Spróbujmy znaleźć jakąkolwiek aktywną zmianę, może została rozpoczęta wczoraj
                any_active_shift = db.query(models.Shift).filter(
                    models.Shift.employee_id == worker_id,
                    models.Shift.stop_time == None
                ).first()
                
                if any_active_shift:
                    print(f"Znaleziono wcześniejszą aktywną zmianę od {any_active_shift.start_time}")
                    active_shift = any_active_shift
                else:
                    print(f"Nie znaleziono żadnej aktywnej zmiany dla {worker_id}")
        except Exception as e:
            print(f"Błąd podczas wyszukiwania aktywnej zmiany: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Błąd serwera podczas wyszukiwania aktywnej zmiany: {str(e)}"}
            )
        
        if not active_shift:
            return JSONResponse(
                status_code=400,
                content={"detail": "Nie znaleziono aktywnej zmiany dla tego pracownika"}
            )
        
        # Aktualizuj wpis w tabeli shifts
        stop_time = dt.datetime.now()
        active_shift.stop_time = stop_time
        active_shift.stop_location = location
        active_shift.stop_latitude = stop_lat
        active_shift.stop_longitude = stop_lon
        
        # Oblicz czas trwania w minutach
        duration = stop_time - active_shift.start_time
        duration_minutes = duration.total_seconds() // 60
        active_shift.duration_min = int(duration_minutes)
        
        db.commit()
        
        # Przygotuj odpowiedź
        duration_str = f"{int(duration_minutes // 60)}h {int(duration_minutes % 60)}min"
        
        return {
            "status": "success", 
            "message": "Zakończono pracę", 
            "duration": duration_str,
            "duration_min": int(duration_minutes)  # To pole jest używane przez starszą wersję frontendu
        }
        
    except Exception as e:
        print(f"Błąd podczas zakończenia pracy: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )



@app.post("/api/logout")
async def logout(request: Request):
    """Wylogowanie użytkownika"""
    print("Wylogowywanie użytkownika...")
    request.session.clear()
    return {"message": "Wylogowano pomyślnie"}

# Przekierowanie ze starej ścieżki do nowej
@app.post("/logout")
async def logout_redirect():
    """Przekierowanie starego endpointu wylogowania"""
    return RedirectResponse(url="/api/logout", status_code=307)

@app.post("/api/workers")
async def add_worker(request: Request):
    """Dodawanie nowego pracownika"""
    print("Dodawanie nowego pracownika...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        db = next(get_db())
        
        # Sprawdź czy pracownik o takim ID już istnieje
        existing = db.query(models.Employee).filter(models.Employee.id == data["id"]).first()
        if existing:
            return JSONResponse(
                status_code=400,
                content={"detail": f"Pracownik o ID {data['id']} już istnieje"}
            )
        
        # Tworzymy nowego pracownika
        new_employee = models.Employee(
            id=data["id"],
            name=f"{data['first_name']} {data['last_name']}",
            pin=data.get("pin"),
            password_hash=get_password_hash(data.get("pin", "")),
            hourly_rate=float(data.get("hourly_rate", 0)),
            rate_saturday=float(data.get("rate_saturday", 0)),
            rate_sunday=float(data.get("rate_sunday", 0)),
            rate_night=float(data.get("rate_night", 0)),
            rate_overtime=float(data.get("rate_overtime", 0)),
            is_admin=bool(data.get("is_admin", False))
        )
        
        db.add(new_employee)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Pracownik {data['id']} został dodany"
        }
    except Exception as e:
        print(f"Błąd podczas dodawania pracownika: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Przekierowanie ze starej ścieżki do nowej
@app.post("/workers")
async def add_worker_redirect():
    """Przekierowanie starego endpointu dodawania pracownika"""
    return RedirectResponse(url="/api/workers", status_code=307)

@app.get("/api/workers")
async def get_workers(request: Request):
    """Pobierz listę wszystkich pracowników"""
    print("Pobieranie listy pracowników...")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        db = next(get_db())
        employees = db.query(models.Employee).all()
        
        result = []
        for employee in employees:
            result.append({
                "id": employee.id,
                "name": employee.name,
                "hourly_rate": employee.hourly_rate,
                "is_admin": employee.is_admin
            })
        
        return result
    except Exception as e:
        print(f"Błąd podczas pobierania pracowników: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.get("/api/worker/{worker_id}")
async def get_worker_detail(request: Request, worker_id: str):
    """Pobierz dane pojedynczego pracownika"""
    print(f"Pobieranie danych pracownika o ID: {worker_id}")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        db = next(get_db())
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono pracownika o ID: {worker_id}"}
            )
        
        # Konwertuj imię i nazwisko z pola name
        name_parts = employee.name.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        result = {
            "id": employee.id,
            "name": employee.name,
            "first_name": first_name,
            "last_name": last_name,
            "pin": employee.pin,
            "hourly_rate": employee.hourly_rate,
            "rate_saturday": employee.rate_saturday,
            "rate_sunday": employee.rate_sunday,
            "rate_night": employee.rate_night,
            "rate_overtime": employee.rate_overtime,
            "is_admin": employee.is_admin
        }
        
        return result
    except Exception as e:
        print(f"Błąd podczas pobierania danych pracownika: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.put("/api/worker/{worker_id}/pin")
async def update_worker_pin(worker_id: int, request: Request):
    """Aktualizacja PIN-u pracownika"""
    print(f"Aktualizacja PIN-u pracownika {worker_id}")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        pin = data.get("pin")
        
        if not pin or not isinstance(pin, str) or len(pin) != 4 or not pin.isdigit():
            return JSONResponse(
                status_code=400,
                content={"detail": "PIN musi być 4-cyfrowym kodem"}
            )
        
        db = next(get_db())
        worker = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        
        if not worker:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono pracownika o ID {worker_id}"}
            )
        
        # Aktualizacja PIN-u
        worker.pin = pin
        db.commit()
        
        return {
            "status": "success",
            "message": f"Zaktualizowano PIN pracownika {worker_id}"
        }
    except Exception as e:
        print(f"Błąd podczas aktualizacji PIN-u: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.put("/api/worker/{worker_id}")
async def update_api_worker(worker_id: int, request: Request):
    """Aktualizacja danych pracownika (API)"""
    print(f"Aktualizacja pracownika {worker_id}")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        db = next(get_db())
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono pracownika o ID: {worker_id}"}
            )
        
        # Aktualizacja danych pracownika
        if "first_name" in data or "last_name" in data:
            first_name = data.get("first_name", "").strip()
            last_name = data.get("last_name", "").strip()
            if first_name and last_name:
                employee.name = f"{first_name} {last_name}"
        
        if "pin" in data and data["pin"]:
            pin = data["pin"]
            employee.pin = pin
            employee.password_hash = get_password_hash(pin)  # Aktualizujemy hasło razem z PIN-em
        
        # Obsługa obu wariantów pola - rate i hourly_rate (dla kompatybilności)
        if "hourly_rate" in data and data["hourly_rate"] is not None:
            employee.hourly_rate = float(data["hourly_rate"])
        elif "rate" in data and data["rate"] is not None:
            employee.hourly_rate = float(data["rate"])
        
        if "rate_saturday" in data and data["rate_saturday"] is not None:
            employee.rate_saturday = float(data["rate_saturday"])
        
        if "rate_sunday" in data and data["rate_sunday"] is not None:
            employee.rate_sunday = float(data["rate_sunday"])
        
        if "rate_night" in data and data["rate_night"] is not None:
            employee.rate_night = float(data["rate_night"])
        
        if "rate_overtime" in data and data["rate_overtime"] is not None:
            employee.rate_overtime = float(data["rate_overtime"])
        
        if "is_admin" in data:
            employee.is_admin = bool(data["is_admin"])
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Dane pracownika {worker_id} zostały zaktualizowane"
        }
    except Exception as e:
        print(f"Błąd podczas aktualizacji danych pracownika: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.get("/api/attendance_by_date")
async def get_attendance_by_date(request: Request, date: str):
    """Pobierz obecności na dany dzień"""
    print(f"Pobieranie obecności dla daty: {date}")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        date_obj = dt.datetime.strptime(date, "%Y-%m-%d").date()
        db = next(get_db())
        
        # Pobranie logów obecności z danego dnia
        start_of_day = dt.datetime.combine(date_obj, dt.datetime.min.time())
        end_of_day = dt.datetime.combine(date_obj, dt.datetime.max.time())
        
        # Używamy tabeli shifts zamiast attendance_logs
        shifts = db.query(models.Shift).filter(
            models.Shift.start_time >= start_of_day,
            models.Shift.start_time <= end_of_day
        ).all()
        
        result = []
        for shift in shifts:
            employee = db.query(models.Employee).filter(models.Employee.id == shift.employee_id).first()
            if not employee:
                continue
                
            # Obliczanie czasu trwania zmiany
            duration = "W trakcie"
            if shift.stop_time:
                start = shift.start_time
                stop = shift.stop_time
                diff = stop - start
                hours, remainder = divmod(diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                duration = f"{hours}h {minutes}min"
            
            result.append({
                "id": shift.id,
                "worker_id": shift.employee_id,
                "name": employee.name,
                "start_time": shift.start_time.strftime("%H:%M"),
                "stop_time": shift.stop_time.strftime("%H:%M") if shift.stop_time else "-",
                "duration": duration,
                "is_holiday": False,  # Te pola nie istnieją w tabeli shifts, dodajemy domyślne wartości
                "is_sick": False
            })
        
        return result
    except Exception as e:
        print(f"Błąd podczas pobierania obecności: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.get("/pin_access_logs")
async def get_pin_access_logs(request: Request):
    """Endpoint do pobierania logów dostępu PIN"""
    print("Pobieranie logów dostępu PIN...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
        
    try:
        db = next(get_db())
        
        # Sprawdzamy czy tabela pin_logs istnieje
        try:
            logs = db.execute("""
                SELECT * FROM pin_logs
                ORDER BY created_at DESC
                LIMIT 500
            """).fetchall()
            
            # Konwertujemy wyniki na listę słowników
            result_logs = []
            for log in logs:
                log_dict = dict(log)
                result_logs.append(log_dict)
                
            return {
                "success": True,
                "logs": result_logs
            }
        except Exception as e:
            # Jeśli tabela nie istnieje, zwracamy pustą listę
            print(f"Błąd podczas pobierania logów PIN: {str(e)}")
            return {
                "success": True,
                "logs": [],
                "message": "Tabela pin_logs nie istnieje lub jest pusta"
            }
            
    except Exception as e:
        print(f"Błąd podczas pobierania logów PIN: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Błąd serwera: {str(e)}"}
        )

@app.post("/api/pin_verify")
@app.post("/pin_verify")  # Zachowujemy stary endpoint dla kompatybilności wstecznej
async def verify_pin(request: Request):
    """Endpoint do weryfikacji PIN pracownika"""
    print("Weryfikacja PIN pracownika...")
    try:
        data = await request.json()
        worker_id = data.get("worker_id")
        pin_entered = data.get("pin")
        device_id = data.get("device_id", "unknown")
        location = data.get("location", "")
        device_model = data.get("device_model", "")
        os_version = data.get("os_version", "")
        
        if not worker_id or not pin_entered:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Brakuje ID pracownika lub PIN"}
            )
            
        db = next(get_db())
        
        # Znajdź pracownika
        worker = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        
        # Przygotuj log weryfikacji PIN
        try:
            # Sprawdź czy tabela istnieje
            db.execute("""
                CREATE TABLE IF NOT EXISTS pin_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id TEXT NOT NULL,
                    pin_entered TEXT NOT NULL,
                    pin_correct BOOLEAN NOT NULL,
                    access_granted BOOLEAN NOT NULL,
                    device_id TEXT,
                    location TEXT,
                    device_model TEXT,
                    os_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            pin_correct = False
            access_granted = False
            
            if worker and worker.pin and worker.pin == pin_entered:
                pin_correct = True
                access_granted = True
            
            # Zapisz log weryfikacji
            db.execute("""
                INSERT INTO pin_logs (
                    worker_id, pin_entered, pin_correct, access_granted,
                    device_id, location, device_model, os_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                worker_id, pin_entered, pin_correct, access_granted,
                device_id, location, device_model, os_version
            ))
            db.commit()
        except Exception as e:
            print(f"Błąd podczas zapisywania logu PIN: {str(e)}")
            # Kontynuujemy weryfikację nawet jeśli nie udało się zapisać logu
            pass
            
        if not worker:
            return {
                "success": False, 
                "error": "Nieprawidłowy ID pracownika",
                "pin_correct": False,
                "access_granted": False
            }
                
        if not worker.pin:
            return {
                "success": False, 
                "error": "Pracownik nie ma ustawionego PIN-u",
                "pin_correct": False,
                "access_granted": False
            }
                
        if worker.pin != pin_entered:
            return {
                "success": False, 
                "error": "Nieprawidłowy PIN",
                "pin_correct": False,
                "access_granted": False
            }
                
        # PIN jest prawidłowy
        # Ekstrakcja imienia i nazwiska z pola name
        name_parts = worker.name.split(' ', 1) if worker.name else ["", ""]
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        return {
            "success": True,
            "message": "Weryfikacja PIN poprawna",
            "worker": {
                "id": worker.id,
                "first_name": first_name,
                "last_name": last_name,
                "name": worker.name
            },
            "pin_correct": True,
            "access_granted": True
        }
    except Exception as e:
        print(f"Błąd podczas weryfikacji PIN: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Błąd serwera: {str(e)}"}
        )


        

    except Exception as e:
        print(f"Błąd podczas pobierania podsumowania: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# import datetime już jest na górze jako dt

@app.get("/api/connection-test")
async def test_connection(request: Request):
    """Testowy endpoint do sprawdzania połączenia"""
    try:
        return {
            "status": "ok",
            "message": "Połączenie z API działa poprawnie",
            "timestamp": str(dt.datetime.now()),
            "server": "Lista ObecnoÅci API",
            "version": "1.0.0"
        }
    except Exception as e:
        logging.error(f"Błąd podczas testu połączenia: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/mobile-config")
async def get_mobile_config(request: Request):
    """Pobierz konfigurację aplikacji mobilnej"""
    # Format zgodny z oczekiwaniami aplikacji mobilnej
    try:
        # Próba importu z centralnej konfiguracji
        try:
            from configs.app_config import WEB_PANEL_URL, MOBILE_API_URL, APP_DEFAULT_IP
            central_config_available = True
            print("DEBUG: Pobrano centralną konfigurację z configs/app_config.py")
        except ImportError:
            central_config_available = False
            print("DEBUG: Nie można zaimportować centralnej konfiguracji, używam wartości domyślnych")
        
        # Próba importu konfiguracji mobilnej z wymuszonym przeładowaniem modułu
        try:
            import sys
            import importlib
            
            # Usunięcie modułu z pamięci podręcznej, jeśli istnieje
            if 'config' in sys.modules:
                print("DEBUG: Usuwam moduł config z pamięci podręcznej")
                del sys.modules['config']
            
            # Przeładowanie modułu konfiguracyjnego
            import config
            importlib.reload(config)
            MOBILE_APP_CONFIG = config.MOBILE_APP_CONFIG
            CONFIG_VERSION = getattr(config, 'CONFIG_VERSION', 'unknown')
            print("DEBUG: Przeładowano konfigurację mobilną z config.py")
        except ImportError:
            # Awaryjne wartości domyślne
            print("DEBUG: Nie można zaimportować config.py, używam wartości domyślnych")
            MOBILE_APP_CONFIG = {
                "timer_enabled": True,
                "daily_stats": True,
                "monthly_stats": True,
                "gps_verification": False,
                "offline_mode": True,
                "notifications": False,
                "debug_mode": True
            }
            CONFIG_VERSION = "unknown"
            
        # Tworzenie odpowiedzi z uwzględnieniem centralnej konfiguracji
        config_data = {
            "config": {
                "enable_location": MOBILE_APP_CONFIG.get("gps_verification", True),
                "location_interval_seconds": 60,
                "enable_pin_security": True, 
                "require_device_verification": True,
                "offline_mode_enabled": MOBILE_APP_CONFIG.get("offline_mode", True),
                "sync_interval_minutes": 15,
                "battery_saving_mode": False,
                "notify_on_success": MOBILE_APP_CONFIG.get("notifications", True),
                "debug_mode": MOBILE_APP_CONFIG.get("debug_mode", True),
                "timer_enabled": MOBILE_APP_CONFIG.get("timer_enabled", True),
                "daily_stats": MOBILE_APP_CONFIG.get("daily_stats", True),
                "monthly_stats": MOBILE_APP_CONFIG.get("monthly_stats", True),
                "field_blocking": MOBILE_APP_CONFIG.get("field_blocking", False),
            },
            "version": CONFIG_VERSION,
            "config_version": CONFIG_VERSION,
            "timestamp": str(dt.datetime.now())
        }
        
        # Dodanie informacji o serwerach jeśli dostępna centralna konfiguracja
        if central_config_available:
            config_data["config"]["main_server_url"] = MOBILE_API_URL
            config_data["config"]["web_panel_url"] = WEB_PANEL_URL
            config_data["config"]["server_ip"] = APP_DEFAULT_IP
        print(f"DEBUG: Wysyłam konfigurację: {config_data}")
        return config_data
    except Exception as e:
        import traceback
        print(f"ERROR in mobile-config: {str(e)}")
        print(traceback.format_exc())
        # Bezpieczna konfiguracja awaryjnie
        return {
            "config": {
                "enable_location": False,
                "location_interval_seconds": 300,
                "enable_pin_security": False,
                "require_device_verification": False,
                "offline_mode_enabled": True,
                "sync_interval_minutes": 60,
                "battery_saving_mode": True,
                "notify_on_success": False,
                "debug_mode": True,
                "timer_enabled": True,
                "daily_stats": True,
                "monthly_stats": True,
            },
            "version": "1.0.0-fallback",
            "config_version": "1.0.0-fallback",
            "timestamp": str(dt.datetime.now()),
            "error": "Konfiguracja awaryjna"
        }
@app.get("/api/mobile-config-backup")
async def get_mobile_config_backup(request: Request):
    """Zapasowy endpoint konfiguracji mobilnej"""
    return {
        "config": {
            "enable_location": False,
            "offline_mode_enabled": True,
            "location_interval_seconds": 300,
            "enable_pin_security": False,
            "sync_interval_minutes": 60,
            "battery_saving_mode": True,
            "notify_on_success": False
        },
        "version": "1.0.0-backup",
        "timestamp": str(dt.datetime.now()),
        "note": "Endpoint zapasowy"
    }

@app.post("/api/mobile-config")
async def update_mobile_config(request: Request):
    """Aktualizuj konfigurację aplikacji mobilnej"""
    try:
        logging.info("Aktualizacja konfiguracji aplikacji mobilnej...")
        data = await request.json()
        
        # Sprawdzenie autoryzacji - tylko admin może aktualizować konfigurację
        user = request.session.get("user")
        if not user or user.get("role") != "admin":
            logging.warning("Próba aktualizacji konfiguracji bez uprawnień administratora!")
            return JSONResponse(
                status_code=401,
                content={"detail": "Nieautoryzowany dostęp - wymagane uprawnienia administratora"}
            )
        
        # Aktualizacja pliku konfiguracyjnego
        import os
        import re
        from datetime import datetime
        
        # Generowanie nowej wersji konfiguracji
        now = datetime.now()
        new_config_version = now.strftime("%Y%m%d-%H%M%S")
        
        # Odczyt aktualnego pliku config.py
        config_path = "config.py"
        if not os.path.exists(config_path):
            logging.error(f"Nie znaleziono pliku konfiguracyjnego: {config_path}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Nie znaleziono pliku konfiguracyjnego: {config_path}"}
            )
        
        logging.info(f"Aktualizacja pliku konfiguracyjnego {config_path}...")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
        
        logging.info(f"Odczytano {len(config_content)} bajtów z pliku konfiguracyjnego")
            
        # Aktualizacja wersji konfiguracji
        config_content = re.sub(
            r'CONFIG_VERSION = "[^"]+"', 
            f'CONFIG_VERSION = "{new_config_version}"', 
            config_content
        )
        
        # Aktualizacja konfiguracji aplikacji mobilnej
        if "MOBILE_APP_CONFIG" in data:
            logging.info("Aktualizacja MOBILE_APP_CONFIG...")
            mobile_config = data["MOBILE_APP_CONFIG"]
            
            # Tworzenie nowego bloku konfiguracji
            mobile_config_str = "MOBILE_APP_CONFIG = {\n"
            for key, value in mobile_config.items():
                # Konwersja wartości na odpowiedni format Pythona
                if isinstance(value, bool):
                    mobile_config_str += f'    "{key}": {str(value)},\n'
                elif isinstance(value, (int, float)):
                    mobile_config_str += f'    "{key}": {value},\n'
                else:
                    mobile_config_str += f'    "{key}": "{str(value)}",\n'
            mobile_config_str += "}\n"
            
            # Zastąp istniejący blok konfiguracji
            pattern = r'MOBILE_APP_CONFIG = \{[\s\S]*?\}'
            if re.search(pattern, config_content):
                config_content = re.sub(pattern, mobile_config_str.rstrip(), config_content)
                logging.info("Zaktualizowano blok MOBILE_APP_CONFIG")
            else:
                logging.warning("Nie znaleziono bloku MOBILE_APP_CONFIG do aktualizacji!")
        
        # Utwórz kopię zapasową pliku konfiguracyjnego
        backup_path = f"config_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
        try:
            import shutil
            shutil.copy(config_path, backup_path)
            logging.info(f"Utworzono kopię zapasową konfiguracji: {backup_path}")
        except Exception as backup_error:
            logging.warning(f"Nie można utworzyć kopii zapasowej: {backup_error}")
        
        # Zapisz zaktualizowany plik
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            logging.info(f"Zapisano zaktualizowaną konfigurację do {config_path}")
            
            # Weryfikacja zapisu
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as verify_file:
                    verify_content = verify_file.read()
                if new_config_version in verify_content:
                    logging.info(f"Weryfikacja OK - nowa wersja konfiguracji ({new_config_version}) zapisana")
                else:
                    logging.error("Weryfikacja NIEUDANA - nowa wersja nie została zapisana!")
            else:
                logging.error("Weryfikacja NIEUDANA - plik konfiguracyjny nie istnieje po zapisie!")
        except Exception as save_error:
            logging.error(f"Błąd zapisu pliku konfiguracyjnego: {save_error}")
            raise save_error
        
        now = dt.datetime.now()  # Używamy zaimportowanego modułu dt
        return {
            "status": "success",
            "message": "Konfiguracja zaktualizowana pomyślnie",
            "config_version": new_config_version,
            "timestamp": str(now)
        }
    except Exception as e:
        logging.error(f"Błąd podczas aktualizacji konfiguracji mobilnej: {e}")
        now = dt.datetime.now()  # Używamy zaimportowanego modułu dt
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Błąd podczas aktualizacji konfiguracji: {str(e)}",
                "timestamp": str(now)
            }
        )

@app.get("/api/time-rounding-config")
async def get_time_rounding_config(request: Request):
    """Pobiera aktualną konfigurację zaokrąglania czasu pracy"""
    print("Pobieranie konfiguracji zaokrąglania czasu pracy...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    return TIME_ROUNDING_CONFIG

@app.post("/api/time-rounding-config")
async def update_time_rounding_config(request: Request):
    """Aktualizuje konfigurację zaokrąglania czasu pracy"""
    print("Aktualizacja konfiguracji zaokrąglania czasu pracy...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        
        # Aktualizacja globalnej konfiguracji
        TIME_ROUNDING_CONFIG["enabled"] = data.get("enabled", False)
        TIME_ROUNDING_CONFIG["interval_minutes"] = data.get("interval_minutes", 15)
        TIME_ROUNDING_CONFIG["direction"] = data.get("direction", "nearest")
        
        # Zapisz konfigurację do pliku (opcjonalnie)
        with open("time_rounding_config.json", "w") as f:
            import json
            json.dump(TIME_ROUNDING_CONFIG, f, indent=4)
        
        return {"success": True, "message": "Konfiguracja zaktualizowana", "config": TIME_ROUNDING_CONFIG}
    except Exception as e:
        print(f"Błąd podczas aktualizacji konfiguracji zaokrąglania czasu: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.get("/api/app-version")
async def get_app_version(request: Request):
    """Pobiera informacje o aktualnej wersji aplikacji mobilnej"""
    print("Pobieranie informacji o wersji aplikacji...")
    
    # Importuj konfigurację z pliku config.py
    try:
        from config import APP_VERSION_INFO, CONFIG_VERSION
        
        # Logowanie dla diagnostyki
        print(f"CONFIG: Wersja konfiguracji: {CONFIG_VERSION}")
        print(f"CONFIG: Wersja aplikacji: {APP_VERSION_INFO['current_version']}")
        
        # Format zgodny z oczekiwaniami frontendu
        result = {
            "version_info": APP_VERSION_INFO,
            "server_time": str(dt.datetime.now()),
            "config_version": CONFIG_VERSION,
            "timestamp": str(dt.datetime.now())
        }
        print(f"CONFIG: Wysyłam dane wersji: {result}")
        return result
    except ImportError:
        print("Błąd importu konfiguracji z pliku config.py")
        # Awaryjne dane wersji aplikacji
        version_data = {
            "version_info": {
                "current_version": "1.2.5",
                "minimum_version": "1.0.0",
                "update_required": False,
                "update_message": "Dostępna nowa wersja aplikacji",
                "play_store_url": "https://lista-obecnosci.pl/downloads/app-v1.2.5.apk",
                "update_features": [
                    "Naprawiono błędy z logowaniem PIN",
                    "Poprawiono synchronizację offline",
                    "Dodano powiadomienia o rozpoczęciu i zakończeniu pracy"
                ]
            },
            "server_time": str(dt.datetime.now()),
            "config_version": "20250802-000000"  # Wersja awaryjna
        }
        
        return version_data

@app.get("/api/connection-test")
async def connection_test(request: Request):
    """Prosty endpoint do testowania połączenia z API"""
    print("Test połączenia API...")
    
    try:
        import api_config
        from platform import python_version
        import socket
        
        # Pobierz listę dostępnych endpointów z konfiguracji
        endpoints = [endpoint["path"] for endpoint in api_config.ACTIVE_ENDPOINTS]
        
        # Informacje o serwerze i statusie
        info = {
            "status": "ok",
            "message": "API działa poprawnie",
            "timestamp": str(dt.datetime.now()),
            "hostname": socket.gethostname(),
            "server_info": {
                "api_version": api_config.API_CONFIG["version"],
                "python_version": python_version(),
                "endpoints_available": endpoints
            }
        }
        
        # Loguj informację o teście połączenia
        if api_config.ENABLE_DIAGNOSTICS:
            api_config.log_diagnostic(f"Test połączenia z IP: {request.client.host}", "INFO")
        
        return info
    
    except ImportError:
        # Jeśli nie można zaimportować api_config, użyj domyślnych informacji
        info = {
            "status": "ok",
            "message": "API działa poprawnie",
            "timestamp": str(dt.datetime.now()),
            "server_info": {
                "api_version": "1.0.0",
                "python_version": "3.10.x",
                "endpoints_available": [
                    "/api/workers",
                    "/api/mobile-config",
                    "/api/app-version"
                ]
            }
        }
        
        return info



@app.get("/api/time-rounding-config")
async def get_time_rounding_config(request: Request):
    """Pobierz konfigurację zaokrąglania czasu"""
    print("Pobieranie konfiguracji zaokrąglania czasu...")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    # Używamy konfiguracji z config.py
    return TIME_ROUNDING_CONFIG

@app.post("/api/time-rounding-config")
async def update_time_rounding_config(request: Request):
    """Aktualizacja konfiguracji zaokrąglania czasu"""
    print("Aktualizacja konfiguracji zaokrąglania czasu...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        # W normalnej sytuacji zapisalibyśmy to do bazy danych lub pliku konfiguracyjnego
        # Tutaj tylko symulujemy aktualizację
        
        # Aktualizacja konfiguracji w pamięci
        global TIME_ROUNDING_CONFIG
        TIME_ROUNDING_CONFIG.update(data)
        
        return {"status": "success", "config": TIME_ROUNDING_CONFIG}
    except Exception as e:
        print(f"Błąd podczas aktualizacji konfiguracji: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        ),


@app.post("/api/import_employees_csv")
async def import_employees_csv(request: Request):
    """Import pracowników z pliku CSV"""
    print("Importowanie pracowników z CSV...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        employees_data = data.get("employees", [])
        
        if not employees_data:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak danych do importu"}
            )
        
        db = next(get_db())
        imported = 0
        errors = []
        
        for idx, emp in enumerate(employees_data):
            try:
                # Tworzenie ID pracownika na podstawie imienia i nazwiska
                first_name = emp.get("first_name", "").strip()
                last_name = emp.get("last_name", "").strip()
                
                if not first_name or not last_name:
                    errors.append({"row": idx + 1, "error": "Brak imienia lub nazwiska"})
                    continue
                
                # ID to pierwsza litera imienia + nazwisko, wszystko małymi literami
                emp_id = (first_name[0] + last_name).lower()
                # Usuń polskie znaki
                emp_id = emp_id.replace("ą", "a").replace("ć", "c").replace("ę", "e") \
                               .replace("ł", "l").replace("ń", "n").replace("ó", "o") \
                               .replace("ś", "s").replace("ż", "z").replace("ź", "z")
                # Usuń spacje i inne niestandardowe znaki
                emp_id = "".join(c for c in emp_id if c.isalnum())
                
                # Sprawdź czy pracownik już istnieje
                existing = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
                if existing:
                    errors.append({"row": idx + 1, "error": f"Pracownik o ID {emp_id} już istnieje"})
                    continue
                
                # Przygotuj dane pracownika
                pin = emp.get("pin", "")
                hourly_rate = float(emp.get("hourly_rate", 0))
                
                # Utwórz nowego pracownika
                new_employee = models.Employee(
                    id=emp_id,
                    name=f"{first_name} {last_name}",
                    pin=pin,
                    password_hash=get_password_hash(pin),  # Domyślnie hasło = PIN
                    hourly_rate=hourly_rate,
                    is_admin=False
                )
                
                db.add(new_employee)
                db.commit()
                imported += 1
                
            except Exception as e:
                errors.append({"row": idx + 1, "error": str(e)})
                db.rollback()
        
        return {
            "status": "success",
            "imported": imported,
            "errors": errors,
            "total": len(employees_data)
        }
        
    except Exception as e:
        print(f"Błąd podczas importu pracowników: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.post("/api/shift")
async def add_shift(request: Request):
    """Ręczne dodanie zmiany pracownika"""
    print("Dodawanie ręcznej zmiany pracownika...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        worker_id = data.get("worker_id")
        date = data.get("date")
        start_time = data.get("start_time")
        stop_time = data.get("stop_time")
        start_location = data.get("start_location", "Dodane ręcznie")
        stop_location = data.get("stop_location", "Dodane ręcznie")
        
        if not worker_id or not date or not start_time or not stop_time:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brakujące dane: wymagane worker_id, date, start_time i stop_time"}
            )
        
        db = next(get_db())
        
        # Sprawdzamy czy pracownik istnieje
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono pracownika o ID: {worker_id}"}
            )
        
        # Konwertujemy stringi na obiekty datetime
        try:
            date_obj = dt.datetime.strptime(date, "%Y-%m-%d").date()
            start_time_obj = dt.datetime.strptime(start_time, "%H:%M").time()
            stop_time_obj = dt.datetime.strptime(stop_time, "%H:%M").time()
            
            # Łączymy datę i czas
            start_datetime = dt.datetime.combine(date_obj, start_time_obj)
            stop_datetime = dt.datetime.combine(date_obj, stop_time_obj)
            
            # Jeśli czas zakończenia jest wcześniejszy niż rozpoczęcia, zakładamy że zmiana przeszła na następny dzień
            if stop_datetime <= start_datetime:
                stop_datetime = dt.datetime.combine(date_obj + timedelta(days=1), stop_time_obj)
            
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={"detail": f"Nieprawidłowy format daty lub czasu: {str(e)}"}
            )
        
        # Oblicz czas trwania
        duration = stop_datetime - start_datetime
        duration_minutes = int(duration.total_seconds() // 60)
        
        # Tworzymy nową zmianę
        new_shift = models.Shift(
            employee_id=worker_id,
            start_time=start_datetime,
            stop_time=stop_datetime,
            start_location=start_location,
            stop_location=stop_location,
            duration_min=duration_minutes
        )
        
        db.add(new_shift)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Dodano zmianę dla pracownika {worker_id}",
            "shift_id": new_shift.id
        }
    except Exception as e:
        print(f"Błąd podczas dodawania zmiany: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@app.post("/api/workers/batch")
async def batch_operations(request: Request):
    """Operacje wsadowe na pracownikach"""
    print("Wykonywanie operacji wsadowych na pracownikach...")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        operation = data.get("operation")
        worker_ids = data.get("worker_ids", [])
        
        if not operation or not worker_ids:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak danych do operacji wsadowej"}
            )
        
        db = next(get_db())
        affected = 0
        
        if operation == "delete":
            for emp_id in worker_ids:
                employee = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
                if employee:
                    db.delete(employee)
                    affected += 1
            
            db.commit()
            return {
                "status": "success",
                "message": f"Usunięto {affected} pracowników",
                "affected": affected
            }
        
        elif operation == "set_rate":
            hourly_rate = data.get("hourly_rate")
            if hourly_rate is None:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Brak stawki godzinowej"}
                )
            
            for emp_id in worker_ids:
                employee = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
                if employee:
                    employee.hourly_rate = float(hourly_rate)
                    affected += 1
            
            db.commit()
            return {
                "status": "success",
                "message": f"Zmieniono stawkę dla {affected} pracowników",
                "affected": affected
            }
        
        else:
            return JSONResponse(
                status_code=400,
                content={"detail": f"Nieobsługiwana operacja: {operation}"}
            )
        
    except Exception as e:
        print(f"Błąd podczas operacji wsadowej: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Montowanie plików statycznych - na końcu
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Dodaj routery
from pin_access_logs import router as pin_logs_router
app.include_router(pin_logs_router)

# Dodaj router do obsługi ewidencji czasu pracy
from attendance import router as attendance_router
app.include_router(attendance_router)

# Endpoint awaryjnego zakończenia zmiany dla administratorów
@app.post("/api/admin/force-stop")
async def admin_force_stop(request: Request):
    """Awaryjne zakończenie pracy przez administratora"""
    print("Otrzymano żądanie awaryjnego zakończenia pracy")
    
    # Sprawdź, czy użytkownik ma uprawnienia administratora
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse(
            status_code=401,
            content={"detail": "Wymagane uprawnienia administratora"}
        )
    
    try:
        data = await request.json()
        worker_id = data.get("worker_id")
        reason = data.get("reason", "Zakończenie awaryjne przez administratora")
        
        if not worker_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak identyfikatora pracownika"}
            )
        
        db = next(get_db())
        
        # Znajdź aktywną zmianę pracownika
        today = dt.datetime.now().date()
        active_shift = db.query(models.Shift).filter(
            models.Shift.employee_id == worker_id,
            models.Shift.start_time >= dt.datetime.combine(today, dt.datetime.min.time()),
            models.Shift.stop_time == None
        ).first()
        
        if not active_shift:
            return JSONResponse(
                status_code=400,
                content={"detail": "Nie znaleziono aktywnej zmiany dla tego pracownika"}
            )
        
        # Aktualizuj wpis w tabeli shifts
        stop_time = dt.datetime.now()
        active_shift.stop_time = stop_time
        active_shift.stop_location = f"Zakończono awaryjnie: {reason}"
        active_shift.stop_latitude = 0.0
        active_shift.stop_longitude = 0.0
        
        # Oblicz czas trwania w minutach
        duration = stop_time - active_shift.start_time
        duration_minutes = duration.total_seconds() // 60
        active_shift.duration_min = int(duration_minutes)
        
        # Dodaj wpis do logu administracyjnego
        admin_log = models.AdminLog(
            action_type="FORCE_STOP",
            admin_id=user.get("id"),
            target_id=worker_id,
            notes=f"Awaryjne zakończenie zmiany. Powód: {reason}"
        )
        db.add(admin_log)
        
        db.commit()
        
        # Przygotuj odpowiedź
        duration_str = f"{int(duration_minutes // 60)}h {int(duration_minutes % 60)}min"
        
        return {
            "status": "success", 
            "message": f"Awaryjnie zakończono pracę dla {worker_id}", 
            "duration": duration_str,
            "admin_id": user.get("id"),
            "timestamp": stop_time.isoformat()
        }
        
    except Exception as e:
        print(f"Błąd podczas awaryjnego zakończenia pracy: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Endpoint do sprawdzenia statusu pracownika
@app.get("/api/worker/{worker_id}/status")
async def get_worker_status(worker_id: str, request: Request):
    """Sprawdza status aktywnej zmiany pracownika"""
    try:
        db = next(get_db())
        
        # Sprawdź czy pracownik istnieje
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": "Pracownik nie istnieje"}
            )
        
        # Sprawdź aktywne zmiany
        active_shift = db.query(models.Shift).filter(
            models.Shift.employee_id == worker_id,
            models.Shift.stop_time == None
        ).first()
        
        result = {
            "worker_id": worker_id,
            "name": employee.name,
            "is_active": active_shift is not None
        }
        
        if active_shift:
            # Oblicz czas trwania zmiany
            duration = dt.datetime.now() - active_shift.start_time
            duration_minutes = duration.total_seconds() // 60
            duration_str = f"{int(duration_minutes // 60)}h {int(duration_minutes % 60)}min"
            
            result.update({
                "shift_id": active_shift.id,
                "start_time": active_shift.start_time.isoformat(),
                "duration": duration_str,
                "duration_minutes": int(duration_minutes),
                "start_location": active_shift.start_location
            })
        
        return result
    except Exception as e:
        print(f"Błąd podczas sprawdzania statusu pracownika: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Endpoint do weryfikacji PIN dla statystyk
@app.post("/statistics/verify-pin")
def verify_pin_for_statistics(data: dict = Body(...), db: Session = Depends(get_db)):
    """Weryfikuje PIN pracownika dla dostępu do statystyk"""
    try:
        worker_id = data.get("worker_id")
        pin = data.get("pin")
        device_info = data.get("device_info", {})
        location_info = data.get("location", {})
        period_type = data.get("period_type", "month")  # day, week, month, custom
        start_date = data.get("start_date")  # dla custom
        end_date = data.get("end_date")  # dla custom
        
        if not worker_id or not pin:
            return {"success": False, "message": "Brak ID pracownika lub PIN"}
        
        # Sprawdź czy pracownik istnieje
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        if not employee:
            # Loguj próbę dostępu z nieistniejącym ID
            access_log = models.StatisticsAccessLog(
                worker_id=worker_id,
                device_id=device_info.get("device_id", "unknown"),
                device_model=device_info.get("device_model", "unknown"),
                pin_entered=pin,
                pin_correct=False,
                access_granted=False,
                latitude=location_info.get("latitude"),
                longitude=location_info.get("longitude"),
                location_text=location_info.get("location_text")
            )
            db.add(access_log)
            db.commit()
            
            return {"success": False, "message": "Niepoprawny PIN lub ID pracownika"}
        
        # Sprawdź czy PIN jest poprawny
        pin_correct = employee.pin == pin
        
        # Sprawdź czy urządzenie się zmieniło
        device_changed = False
        if device_info.get("device_id"):
            last_device = db.query(models.DeviceLog).filter(
                models.DeviceLog.worker_id == worker_id,
                models.DeviceLog.is_approved == True
            ).order_by(models.DeviceLog.created_at.desc()).first()
            
            if last_device and last_device.device_id != device_info.get("device_id"):
                device_changed = True
                # Utwórz alert bezpieczeństwa
                security_alert = models.DeviceSecurityAlert(
                    worker_id=worker_id,
                    old_device_id=last_device.device_id,
                    new_device_id=device_info.get("device_id"),
                    old_device_model=last_device.device_model,
                    new_device_model=device_info.get("device_model"),
                    alert_type="DEVICE_CHANGE"
                )
                db.add(security_alert)
        
        # Loguj próbę dostępu
        access_log = models.StatisticsAccessLog(
            worker_id=worker_id,
            device_id=device_info.get("device_id", "unknown"),
            device_model=device_info.get("device_model", "unknown"),
            pin_entered=pin,
            pin_correct=pin_correct,
            access_granted=pin_correct,
            latitude=location_info.get("latitude"),
            longitude=location_info.get("longitude"),
            location_text=location_info.get("location_text")
        )
        db.add(access_log)
        db.commit()
        
        if not pin_correct:
            return {
                "success": False, 
                "message": "Niepoprawny PIN. Próba dostępu została zarejestrowana.",
                "attempts_logged": True
            }
        
        # PIN poprawny - pobierz i zwróć statystyki
        try:
            from datetime import datetime, timedelta
            
            # Określ zakres dat na podstawie period_type
            end_date_parsed = datetime.now()
            start_date_parsed = None
            
            if period_type == "day":
                start_date_parsed = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                period_name = "Dzisiaj"
            elif period_type == "week":
                start_date_parsed = datetime.now() - timedelta(days=7)
                period_name = "Ostatnie 7 dni"
            elif period_type == "month":
                start_date_parsed = datetime.now() - timedelta(days=30)
                period_name = "Ostatnie 30 dni"
            elif period_type == "custom" and start_date and end_date:
                try:
                    start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
                    end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                    period_name = f"Od {start_date} do {end_date}"
                except ValueError:
                    return {"success": False, "message": "Niepoprawny format daty (wymagany: YYYY-MM-DD)"}
            else:
                start_date_parsed = datetime.now() - timedelta(days=30)
                period_name = "Ostatnie 30 dni"
            
            # Pobierz statystyki pracownika dla określonego okresu
            query = db.query(models.AttendanceLog).filter(
                models.AttendanceLog.worker_id == worker_id,
                models.AttendanceLog.stop_time != None
            )
            
            if start_date_parsed:
                query = query.filter(models.AttendanceLog.start_time >= start_date_parsed)
            if end_date_parsed:
                query = query.filter(models.AttendanceLog.start_time <= end_date_parsed)
                
            logs = query.order_by(models.AttendanceLog.start_time.desc()).all()
            
            total_hours = 0
            recent_shifts = []
            days_worked = set()
            
            for log in logs:
                if log.start_time and log.stop_time:
                    duration = log.stop_time - log.start_time
                    hours = duration.total_seconds() / 3600
                    total_hours += hours
                    
                    # Dodaj dzień do zbioru przepracowanych dni
                    days_worked.add(log.start_time.strftime("%Y-%m-%d"))
                    
                    recent_shifts.append({
                        "date": log.start_time.strftime("%Y-%m-%d"),
                        "start": log.start_time.strftime("%H:%M"),
                        "stop": log.stop_time.strftime("%H:%M"),
                        "hours": round(hours, 2)
                    })
            
            # Oblicz średnią ilość godzin na dzień
            total_days_worked = len(days_worked)
            average_hours = round(total_hours / total_days_worked, 2) if total_days_worked > 0 else 0
            
            statistics_data = {
                "worker_id": worker_id,
                "worker_name": employee.name,
                "period_type": period_type,
                "period_name": period_name,
                "start_date": start_date_parsed.strftime("%Y-%m-%d") if start_date_parsed else None,
                "end_date": end_date_parsed.strftime("%Y-%m-%d") if end_date_parsed else None,
                "total_hours": round(total_hours, 2),
                "total_days": total_days_worked,
                "total_shifts": len(logs),
                "average_hours_per_day": average_hours,
                "recent_shifts": recent_shifts[:20]  # Ostatnie 20 zmian
            }
            
            return {
                "success": True,
                "message": "Dostęp autoryzowany",
                "device_changed": device_changed,
                "worker_name": employee.name,
                "statistics": statistics_data
            }
        except Exception as stats_error:
            # Jeśli błąd statystyk, ale PIN poprawny - zwróć podstawowe dane
            return {
                "success": True,
                "message": "Dostęp autoryzowany",
                "device_changed": device_changed,
                "worker_name": employee.name,
                "statistics": {
                    "worker_id": worker_id,
                    "worker_name": employee.name,
                    "total_hours": 0,
                    "total_days": 0,
                    "average_hours_per_day": 0,
                    "recent_shifts": [],
                    "error": f"Błąd pobierania statystyk: {str(stats_error)}"
                }
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Błąd weryfikacji PIN: {str(e)}"
        }

# Endpointy dla terminala diagnostycznego (dostępne z poziomu przeglądarki)

@app.get("/api/system-status")
def get_system_status(db: Session = Depends(get_db)):
    """Zwraca status systemu dla diagnostyki"""
    try:
        # Sprawdź połączenie z bazą danych
        workers_count = db.query(models.Worker).count()
        active_sessions = db.query(models.Shift).filter(models.Shift.end_time.is_(None)).count()
        
        # Czas uruchomienia serwera
        import psutil
        import time
        from datetime import datetime
        
        current_process = psutil.Process(os.getpid())
        start_time = datetime.fromtimestamp(current_process.create_time())
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        
        # Formatowanie uptime
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m"
        elif hours > 0:
            uptime_str = f"{int(hours)}h {int(minutes)}m"
        else:
            uptime_str = f"{int(minutes)}m {int(seconds)}s"
        
        # Dzisiejsze wejścia/wyjścia
        today = datetime.now().date()
        today_entries = db.query(models.Shift).filter(
            func.date(models.Shift.start_time) == today
        ).count()
        
        today_exits = db.query(models.Shift).filter(
            func.date(models.Shift.end_time) == today
        ).count()
        
        # Ostatnie logowanie do systemu
        last_login = db.query(models.AccessLog).order_by(
            models.AccessLog.timestamp.desc()
        ).first()
        
        last_login_str = "Brak"
        if last_login:
            last_login_time = last_login.timestamp
            if (datetime.now() - last_login_time).days == 0:
                last_login_str = f"Dziś, {last_login_time.strftime('%H:%M:%S')}"
            else:
                last_login_str = last_login_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "status": "ok",
            "api_status": True,
            "database_status": True,
            "version": "2.0.1",
            "active_sessions": active_sessions,
            "total_workers": workers_count,
            "uptime": uptime_str,
            "today_entries": today_entries,
            "today_exits": today_exits,
            "last_login": last_login_str
        }
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statusu systemu: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.get("/api/ping")
def ping_api():
    """Prosty endpoint do sprawdzenia, czy API działa"""
    import platform
    import datetime as dt
    import psutil
    
    try:
        # Dane o systemie
        system_info = platform.system()
        cpu_usage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        memory_usage = f"{memory.percent}%"
        
        # Pobierz czas działania systemu jeśli to możliwe
        uptime = ""
        try:
            boot_time = dt.datetime.fromtimestamp(psutil.boot_time())
            uptime_delta = dt.datetime.now() - boot_time
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{days}d {hours}h {minutes}m"
        except:
            uptime = "Niedostępne"
        
        return {
            "status": "ok",
            "server_status": "Działający",
            "system": system_info,
            "load": f"{cpu_usage}%",
            "memory": memory_usage,
            "uptime": uptime,
            "timestamp": str(dt.datetime.now())
        }
    except ImportError:
        # W przypadku braku modułu psutil zwróć podstawowe informacje
        return {
            "status": "ok",
            "server_status": "Działający",
            "message": "Moduł psutil nie jest dostępny - ograniczone informacje",
            "timestamp": str(dt.datetime.now())
        }
    except Exception as e:
        logger.error(f"Błąd podczas pingowania API: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.get("/api/employees")
def get_employees(db: Session = Depends(get_db)):
    """Pobiera listę wszystkich pracowników"""
    try:
        # Użyjmy tylko podstawowych kolumn, które na pewno istnieją
        workers = db.query(
            models.Employee.id, 
            models.Employee.name, 
            models.Employee.is_admin
        ).all()
        
        # Sprawdź, którzy pracownicy są obecnie obecni
        current_shifts = db.query(models.Shift).filter(
            models.Shift.stop_time.is_(None)
        ).all()
        active_worker_ids = [shift.employee_id for shift in current_shifts]
        
        # Logging dla diagnostyki
        logger.info(f"Pobrano {len(workers)} pracowników, {len(active_worker_ids)} jest aktywnych")
        print(f"Pobrano {len(workers)} pracowników, {len(active_worker_ids)} jest aktywnych")
        
        # Przygotuj dane
        employees_data = []
        for worker in workers:
            # Bardziej ogólne podejście do pobierania danych pracownika
            worker_name = worker.name if hasattr(worker, 'name') else f"Pracownik #{worker.id}"
                
            # Tworzenie podstawowego słownika danych
            worker_data = {
                "id": worker.id,
                "worker_id": worker.id,  # Dla kompatybilności z różnymi wersjami kodu
                "name": worker_name,
                "department": "Ogólny",  # Wartość domyślna
                "active": worker.id in active_worker_ids,
                "position": None  # Wartość domyślna
            }
            
            # Próbujemy dodać dodatkowe informacje, jeśli są dostępne
            try:
                # Logowanie diagnostyczne
                print(f"Przetwarzam pracownika: {worker.id}, {worker_name}")
                
                # Próba pobrania departamentu
                if hasattr(worker, 'department') and worker.department:
                    worker_data["department"] = worker.department
                    
                # Próba pobrania stanowiska
                if hasattr(worker, 'position') and worker.position:
                    worker_data["position"] = worker.position
                    
            except Exception as e:
                print(f"Ostrzeżenie przy przetwarzaniu pracownika {worker.id}: {str(e)}")
                
            employees_data.append(worker_data)
        
        # Dodajemy szczegółowe logowanie dla diagnostyki
        logger.info(f"API /employees: Zwracam dane o {len(employees_data)} pracownikach")
        print(f"API /employees: Zwracam dane o {len(employees_data)} pracownikach")
        # Logowanie pierwszego pracownika dla diagnostyki (jeśli istnieje)
        if employees_data and len(employees_data) > 0:
            print(f"Przykładowy rekord pracownika: {employees_data[0]}")
        
        return {"status": "ok", "employees": employees_data}
    except Exception as e:
        logger.error(f"Błąd podczas pobierania listy pracowników: {str(e)}")
        print(f"BŁĄD API /employees: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.get("/api/active-sessions")
def get_active_sessions(db: Session = Depends(get_db)):
    """Pobiera informacje o aktywnych sesjach (niezakończonych zmianach)"""
    try:
        active_shifts = db.query(models.Shift).join(
            models.Worker, models.Worker.id == models.Shift.worker_id
        ).filter(
            models.Shift.end_time.is_(None)
        ).all()
        
        sessions_data = []
        for shift in active_shifts:
            worker = db.query(models.Worker).filter(models.Worker.id == shift.worker_id).first()
            
            if worker:
                sessions_data.append({
                    "id": shift.id,
                    "user_name": f"{worker.first_name} {worker.last_name}",
                    "login_time": shift.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "ip_address": shift.ip_address if hasattr(shift, 'ip_address') else "nieznane"
                })
        
        return {"status": "ok", "sessions": sessions_data}
    except Exception as e:
        logger.error(f"Błąd podczas pobierania aktywnych sesji: {str(e)}")
        return {"status": "error", "message": str(e)}


# Usunięto zduplikowany endpoint fix-active-sessions
# Ten endpoint był zduplikowany - używamy teraz bardziej zaawansowanej wersji poniżej
# która obsługuje więcej opcji, w tym naprawę pojedynczych sesji
        
        # Zapisz informację o działaniu w logach
        logger.info(f"Naprawiono {fixed_count} zawieszonych sesji przez terminal diagnostyczny")
        
        return {"success": True, "fixed_count": fixed_count, "message": f"Naprawiono {fixed_count} zawieszonych sesji"}
    except Exception as e:
        db.rollback()
        logger.error(f"Błąd podczas naprawiania zawieszonych sesji: {str(e)}")
        return {"success": False, "message": str(e)}
        return {
            "api_status": True,
            "database_status": False,
            "version": "2.0.1",
            "error": str(e)
        }

# Usunięto duplikat endpointu /api/ping - korzystamy z pełnej implementacji powyżej

@app.get("/api/active-shifts")
def get_active_shifts(db: Session = Depends(get_db)):
    """Zwraca listę aktywnych sesji dla terminala diagnostycznego"""
    try:
        # Pobierz aktywne zmiany
        active_shifts = db.query(models.Shift).filter(models.Shift.end_time.is_(None)).all()
        
        result = []
        for shift in active_shifts:
            # Pobierz dane pracownika
            worker = db.query(models.Worker).filter(models.Worker.id == shift.worker_id).first()
            worker_name = f"{worker.first_name} {worker.last_name}" if worker else "Nieznany pracownik"
            
            result.append({
                "id": shift.id,
                "worker_id": shift.worker_id,
                "worker_name": worker_name,
                "start_time": shift.start_time.isoformat(),
                "duration_minutes": int((dt.datetime.now() - shift.start_time).total_seconds() / 60)
            })
        
        return result
    except Exception as e:
        logger.error(f"Błąd podczas pobierania aktywnych sesji: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fix-active-sessions")
def fix_active_sessions(request: Dict = Body(...), db: Session = Depends(get_db)):
    """Naprawia problematyczne aktywne sesje"""
    try:
        fix_all = request.get('fix_all', False)
        session_id = request.get('session_id', None)
        
        if fix_all:
            # Napraw wszystkie aktywne sesje
            now = dt.datetime.now()
            
            # Pobierz wszystkie aktywne sesje
            active_shifts = db.query(models.Shift).filter(models.Shift.end_time.is_(None)).all()
            
            for shift in active_shifts:
                shift.end_time = now
                shift.notes = f"{shift.notes or ''} [AUTO-FIXED: {now.strftime('%Y-%m-%d %H:%M')}]"
            
            db.commit()
            return {
                "success": True, 
                "message": "Wszystkie problematyczne sesje zostały zakończone.",
                "fixed_count": len(active_shifts)
            }
        elif session_id:
            # Napraw konkretną sesję
            shift = db.query(models.Shift).filter(models.Shift.id == session_id, models.Shift.end_time.is_(None)).first()
            
            if not shift:
                return {"success": False, "message": "Nie znaleziono aktywnej sesji o podanym ID."}
                
            shift.end_time = dt.datetime.now()
            shift.notes = f"{shift.notes or ''} [AUTO-FIXED]"
            db.commit()
            
            return {"success": True, "message": f"Sesja ID {session_id} została zakończona."}
        else:
            return {"success": False, "message": "Nie podano ID sesji ani opcji naprawy wszystkich sesji."}
    
    except Exception as e:
        logger.error(f"Błąd podczas naprawiania sesji: {str(e)}")
        return {"success": False, "message": f"Wystąpił błąd: {str(e)}"}

@app.get("/api/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Zwraca podstawowe statystyki systemu dla terminala diagnostycznego"""
    try:
        # Liczba pracowników
        total_workers = db.query(models.Worker).count()
        
        # Aktywne sesje
        active_sessions = db.query(models.Shift).filter(models.Shift.end_time.is_(None)).count()
        
        # Dzisiejsze logowania
        today = dt.datetime.now().date()
        today_start = dt.datetime.combine(today, dt.time.min)
        today_end = dt.datetime.combine(today, dt.time.max)
        
        today_logins = db.query(models.Shift).filter(
            models.Shift.start_time >= today_start,
            models.Shift.start_time <= today_end
        ).count()
        
        # Średni i łączny czas pracy dzisiaj
        completed_shifts_today = db.query(models.Shift).filter(
            models.Shift.start_time >= today_start,
            models.Shift.start_time <= today_end,
            models.Shift.end_time.isnot(None)
        ).all()
        
        total_minutes = 0
        for shift in completed_shifts_today:
            duration = (shift.end_time - shift.start_time).total_seconds() / 60
            total_minutes += duration
            
        avg_work_time = "0h 0m"
        total_work_time = "0h 0m"
        
        if completed_shifts_today:
            avg_minutes = total_minutes / len(completed_shifts_today)
            avg_hours = int(avg_minutes // 60)
            avg_mins = int(avg_minutes % 60)
            avg_work_time = f"{avg_hours}h {avg_mins}m"
            
            total_hours = int(total_minutes // 60)
            total_mins = int(total_minutes % 60)
            total_work_time = f"{total_hours}h {total_mins}m"
        
        return {
            "total_workers": total_workers,
            "active_sessions": active_sessions,
            "today_logins": today_logins,
            "avg_work_time": avg_work_time,
            "total_work_time": total_work_time
        }
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statystyk: {str(e)}")
        return {"error": str(e)}

@app.get("/api/employees/search")
def search_employees(query: str, db: Session = Depends(get_db)):
    """Wyszukuje pracowników po nazwie"""
    try:
        search_term = f"%{query}%"
        employees = db.query(models.Worker).filter(
            (models.Worker.first_name.ilike(search_term)) | 
            (models.Worker.last_name.ilike(search_term))
        ).all()
        
        return [
            {
                "id": emp.id,
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "pin": "****"  # Maskujemy PIN dla bezpieczeństwa
            } 
            for emp in employees
        ]
    except Exception as e:
        logger.error(f"Błąd podczas wyszukiwania pracowników: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Uruchom aplikację bezpośrednio, jeśli ten skrypt jest wykonywany
if __name__ == "__main__":
    import uvicorn
    import argparse
    import sys
    
    # Spróbuj zaimportować centralną konfigurację
    try:
        sys.path.append('.')  # Dodaj bieżący katalog do ścieżki importu
        from configs.app_config import APP_PORT_MAIN, LISTEN_ALL_IP
        default_port = APP_PORT_MAIN
        default_host = LISTEN_ALL_IP
        print(f"Wczytano centralną konfigurację: port={APP_PORT_MAIN}, host={LISTEN_ALL_IP}")
    except ImportError:
        print("UWAGA: Nie można zaimportować centralnej konfiguracji z configs/app_config.py")
        print("Używam domyślnych wartości 0.0.0.0:8000")
        default_port = 8000
        default_host = "0.0.0.0"
    
    # Parsowanie argumentów wiersza poleceń
    parser = argparse.ArgumentParser(description='Uruchom serwer API Lista Obecności')
    parser.add_argument('--host', type=str, default=default_host,
                        help=f'Host do nasłuchiwania (domyślnie: {default_host})')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Port do nasłuchiwania (domyślnie: {default_port})')
    parser.add_argument('--reload', action='store_true', help='Włącz automatyczne przeładowanie')
    
    args = parser.parse_args()
    
    print(f"Uruchamiam serwer na {args.host}:{args.port}")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)
