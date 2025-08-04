"""
Tworzy endpoint do obsługi zapisu danych obecności pracownika
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from database import get_db
import models
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("app")
router = APIRouter()

@router.post("/api/logs")
async def add_log_entry(request: Request):
    """Dodaje nowy wpis do dziennika obecności pracownika"""
    print("Dodawanie nowego wpisu do dziennika obecności...")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        worker_id = data.get("worker_id")
        start_time_str = data.get("start_time")
        stop_time_str = data.get("stop_time")
        start_location = data.get("start_location", "Dodane ręcznie")
        stop_location = data.get("stop_location", "Dodane ręcznie")
        start_lat = data.get("start_lat")
        start_lon = data.get("start_lon")
        stop_lat = data.get("stop_lat")
        stop_lon = data.get("stop_lon")
        
        if not worker_id or not start_time_str or not stop_time_str:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brakuje wymaganych danych (worker_id, start_time, stop_time)"}
            )
        
        # Konwersja stringów czasu na obiekty datetime
        try:
            start_time = datetime.fromisoformat(start_time_str)
            stop_time = datetime.fromisoformat(stop_time_str)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Nieprawidłowy format czasu. Wymagany format: YYYY-MM-DDThh:mm:ss"}
            )
        
        # Walidacja: czas rozpoczęcia musi być wcześniejszy niż czas zakończenia
        if start_time >= stop_time:
            return JSONResponse(
                status_code=400,
                content={"detail": "Czas rozpoczęcia musi być wcześniejszy niż czas zakończenia"}
            )
        
        # Oblicz czas trwania w minutach
        duration = stop_time - start_time
        duration_minutes = int(duration.total_seconds() // 60)
        
        db = next(get_db())
        
        # Znajdź pracownika
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono pracownika o ID: {worker_id}"}
            )
        
        # Utwórz nowy wpis w tabeli shifts
        new_shift = models.Shift(
            employee_id=worker_id,
            start_time=start_time,
            stop_time=stop_time,
            start_location=start_location,
            stop_location=stop_location,
            start_latitude=start_lat,
            start_longitude=start_lon,
            stop_latitude=stop_lat,
            stop_longitude=stop_lon,
            duration_min=duration_minutes
        )
        
        db.add(new_shift)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Dodano wpis do dziennika obecności pracownika {worker_id}",
            "shift_id": new_shift.id
        }
    except Exception as e:
        print(f"Błąd podczas dodawania wpisu do dziennika obecności: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@router.post("/api/logs/batch")
async def add_batch_logs(request: Request):
    """Dodaje wiele wpisów do dziennika obecności"""
    print("Dodawanie wielu wpisów do dziennika obecności...")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        logs_data = await request.json()
        
        if not isinstance(logs_data, list) or len(logs_data) == 0:
            return JSONResponse(
                status_code=400,
                content={"detail": "Oczekiwano tablicy z danymi logów"}
            )
        
        db = next(get_db())
        added_count = 0
        
        for log_entry in logs_data:
            employee_id = log_entry.get("employee_id")
            date_str = log_entry.get("date")
            
            if not employee_id or not date_str:
                continue
            
            # Sprawdź czy pracownik istnieje
            employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
            if not employee:
                continue
            
            # Przyjmij domyślne godziny pracy: 8:00 - 16:00
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                start_time = datetime.combine(date_obj, datetime.strptime("08:00", "%H:%M").time())
                stop_time = datetime.combine(date_obj, datetime.strptime("16:00", "%H:%M").time())
                
                # Oblicz czas trwania w minutach
                duration_minutes = 8 * 60  # 8 godzin
                
                # Utwórz nowy wpis w tabeli shifts
                new_shift = models.Shift(
                    employee_id=employee_id,
                    start_time=start_time,
                    stop_time=stop_time,
                    start_location="Dodane ręcznie (batch)",
                    stop_location="Dodane ręcznie (batch)",
                    duration_min=duration_minutes
                )
                
                db.add(new_shift)
                added_count += 1
            except Exception as e:
                print(f"Błąd dodawania wpisu dla pracownika {employee_id}, data {date_str}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Dodano {added_count} wpisów do dziennika obecności",
            "added_count": added_count
        }
    except Exception as e:
        print(f"Błąd podczas dodawania wielu wpisów: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@router.patch("/api/logs/{log_id}")
async def update_log_entry(log_id: int, request: Request):
    """Aktualizuje istniejący wpis w dzienniku obecności pracownika"""
    print(f"Aktualizacja wpisu o ID: {log_id}")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        data = await request.json()
        start_time_str = data.get("start_time")
        stop_time_str = data.get("stop_time")
        is_holiday = data.get("is_holiday", "nie")
        is_sick = data.get("is_sick", "nie")
        is_present = data.get("is_present", True)
        
        db = next(get_db())
        shift = db.query(models.Shift).filter(models.Shift.id == log_id).first()
        
        if not shift:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono wpisu o ID: {log_id}"}
            )
        
        # Jeśli jest nieobecny, ustawiamy specjalne wartości
        if is_present is False:
            # Dla nieobecności ustawiamy godziny 00:00-00:00 i typ jako "Nieobecny"
            shift.start_time = datetime.fromisoformat(start_time_str.split('T')[0] + "T00:00:00")
            shift.stop_time = datetime.fromisoformat(stop_time_str.split('T')[0] + "T00:00:00")
            shift.status = "Nieobecny"
            shift.duration_min = 0
        else:
            # Dla obecności normalne wartości
            shift.start_time = datetime.fromisoformat(start_time_str)
            shift.stop_time = datetime.fromisoformat(stop_time_str)
            shift.status = "Obecny"
            
            # Obliczanie czasu trwania w minutach
            duration = shift.stop_time - shift.start_time
            duration_minutes = int(duration.total_seconds() // 60)
            shift.duration_min = duration_minutes
        
        # Aktualizacja pól urlop/chorobowe
        if is_holiday == "tak":
            shift.is_holiday = True
        else:
            shift.is_holiday = False
            
        if is_sick == "tak":
            shift.is_sick = True
        else:
            shift.is_sick = False
            
        db.commit()
        
        return {"success": True, "message": "Wpis zaktualizowany"}
        
    except Exception as e:
        print(f"Błąd podczas aktualizacji wpisu: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@router.delete("/api/logs/{log_id}")
async def delete_log_entry(log_id: int, request: Request):
    """Usuwa wpis z dziennika obecności"""
    print(f"Usuwanie wpisu o ID: {log_id}")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        db = next(get_db())
        shift = db.query(models.Shift).filter(models.Shift.id == log_id).first()
        
        if not shift:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono wpisu o ID: {log_id}"}
            )
        
        db.delete(shift)
        db.commit()
        
        return {"success": True, "message": "Wpis usunięty"}
        
    except Exception as e:
        print(f"Błąd podczas usuwania wpisu: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Przekierowania dla starych endpointów
@router.post("/logs")
async def add_log_entry_redirect(request: Request):
    """Przekierowanie dla endpointu /logs"""
    print("Przekierowuję /logs do /api/logs")
    return await add_log_entry(request)

@router.patch("/logs/{log_id}")
async def update_log_entry_redirect(log_id: int, request: Request):
    """Przekierowanie dla endpointu /logs/{log_id}"""
    print(f"Przekierowuję /logs/{log_id} do /api/logs/{log_id}")
    return await update_log_entry(log_id, request)
    
@router.delete("/logs/{log_id}")
async def delete_log_entry_redirect(log_id: int, request: Request):
    """Przekierowanie dla endpointu /logs/{log_id}"""
    print(f"Przekierowuję /logs/{log_id} (DELETE) do /api/logs/{log_id}")
    return await delete_log_entry(log_id, request)

@router.post("/logs/batch")
async def add_batch_logs_redirect(request: Request):
    """Przekierowanie dla endpointu /logs/batch"""
    print("Przekierowuję /logs/batch do /api/logs/batch")
    return await add_batch_logs(request)
