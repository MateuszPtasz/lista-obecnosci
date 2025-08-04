"""
Moduł do obsługi ewidencji czasu pracy
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from database import get_db
import models
from typing import Optional
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("app")
router = APIRouter()

@router.get("/api/attendance_details")
async def get_attendance_details(
    request: Request, 
    worker_id: Optional[str] = None, 
    date_from: Optional[str] = None, 
    date_to: Optional[str] = None
):
    """Pobiera szczegółowe dane obecności pracownika w zadanym przedziale czasu"""
    print("Pobieranie szczegółowych danych obecności")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        # Sprawdzamy czy parametry są podane
        if not worker_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Brak ID pracownika"}
            )
            
        # Jeśli brak dat, przyjmujemy domyślnie bieżący miesiąc
        if not date_from or not date_to:
            today = datetime.now().date()
            first_day = datetime(today.year, today.month, 1).date()
            last_day = (datetime(today.year, today.month + 1, 1) if today.month < 12 else datetime(today.year + 1, 1, 1)).date() - timedelta(days=1)
            
            date_from = date_from or first_day.isoformat()
            date_to = date_to or last_day.isoformat()
        
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Nieprawidłowy format daty. Używaj formatu: YYYY-MM-DD"}
            )
        
        if date_from_obj > date_to_obj:
            return JSONResponse(
                status_code=400,
                content={"detail": "Data początkowa nie może być późniejsza niż data końcowa"}
            )
        
        db = next(get_db())
        
        # Pobieramy pracownika
        employee = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        if not employee:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Nie znaleziono pracownika o ID: {worker_id}"}
            )
        
        # Pobieramy zmiany pracownika w zadanym okresie
        shifts = db.query(models.Shift).filter(
            models.Shift.employee_id == worker_id,
            models.Shift.start_time >= datetime.combine(date_from_obj, datetime.min.time()),
            models.Shift.start_time <= datetime.combine(date_to_obj, datetime.max.time())
        ).order_by(models.Shift.start_time.desc()).all()
        
        # Przygotowujemy dane do zwrócenia w formacie, którego oczekuje frontend
        # Generujemy wszystkie dni z zakresu
        all_days = []
        current_date = date_from_obj
        while current_date <= date_to_obj:
            all_days.append(current_date.isoformat())
            current_date += timedelta(days=1)
        
        # Przygotowanie pustego wyniku
        result = {
            "logs": [],
            "summary": {
                "worker_id": worker_id,
                "name": employee.name,
                "date_from": date_from,
                "date_to": date_to,
                "total_hours": 0,
                "total_days": 0,
                "total_amount": 0
            }
        }
        
        # Przygotowujemy mapowanie dni do zmian
        shifts_by_date = {}
        total_minutes = 0
        
        for shift in shifts:
            shift_date = shift.start_time.strftime("%Y-%m-%d")
            
            # Obliczanie czasu trwania zmiany
            duration_minutes = 0
            status = "W trakcie"
            
            if shift.stop_time:
                duration = shift.stop_time - shift.start_time
                duration_minutes = int(duration.total_seconds() // 60)
                total_minutes += duration_minutes
                hours = duration_minutes // 60
                minutes = duration_minutes % 60
                status = f"{hours}h {minutes}min"
            
            # Format dla frontendu
            # Określenie typu dnia na podstawie nowych pól
            typ_dnia = "Dzień roboczy"
            if shift.status == "Nieobecny":
                typ_dnia = "Nieobecny"
            elif shift.is_holiday:
                typ_dnia = "Urlop"
            elif shift.is_sick:
                typ_dnia = "Chorobowe"
                
            # Określenie statusu obecności
            is_holiday = "tak" if shift.is_holiday else "nie"
            is_sick = "tak" if shift.is_sick else "nie"
                
            shift_data = {
                "log_id": shift.id,
                "date": shift_date,
                "start": shift.start_time.strftime("%H:%M"),
                "stop": shift.stop_time.strftime("%H:%M") if shift.stop_time else "-",
                "duration": status,
                "name": employee.name,
                "is_holiday": is_holiday,
                "is_sick": is_sick,
                "typ": typ_dnia,
                "kwota": employee.hourly_rate * (duration_minutes / 60) if duration_minutes > 0 else 0,
                "start_lat": shift.start_latitude,
                "start_lon": shift.start_longitude,
                "stop_lat": shift.stop_latitude,
                "stop_lon": shift.stop_longitude
            }
            
            shifts_by_date[shift_date] = shift_data
        
        # Dodajemy wszystkie dni, także te bez zmian
        for day in all_days:
            if day in shifts_by_date:
                result["logs"].append(shifts_by_date[day])
            else:
                # Dodajemy pusty wpis dla dni bez zmian
                dayOfWeek = datetime.strptime(day, "%Y-%m-%d").strftime("%A")
                result["logs"].append({
                    "log_id": 0,
                    "date": day,
                    "start": "08:00",
                    "stop": "16:00",
                    "duration": "0h 0min",
                    "name": employee.name,
                    "is_holiday": "nie",
                    "is_sick": "nie",
                    "typ": "Nieobecny",
                    "kwota": 0,
                    "start_lat": None,
                    "start_lon": None,
                    "stop_lat": None,
                    "stop_lon": None
                })
        
        # Aktualizujemy podsumowanie
        result["summary"]["total_hours"] = total_minutes / 60
        result["summary"]["total_days"] = len([s for s in shifts if s.stop_time is not None])
        result["summary"]["total_amount"] = employee.hourly_rate * (total_minutes / 60)
        
        # Sortujemy logi po dacie
        result["logs"].sort(key=lambda x: x["date"])
        
        return result
    except Exception as e:
        print(f"Błąd podczas pobierania szczegółów obecności: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@router.get("/api/attendance_summary")
async def get_attendance_summary(request: Request, date_from: str, date_to: str):
    """Pobierz podsumowanie obecności w zadanym okresie"""
    print(f"Pobieranie podsumowania obecności od {date_from} do {date_to}")
    user = request.session.get("user")
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Nieautoryzowany dostęp"}
        )
    
    try:
        date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
        date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
        
        if date_from_obj > date_to_obj:
            return JSONResponse(
                status_code=400,
                content={"detail": "Data początkowa nie może być późniejsza niż data końcowa"}
            )
        
        db = next(get_db())
        
        # Pobranie wszystkich pracowników
        employees = db.query(models.Employee).all()
        
        result = []
        for employee in employees:
            # Pobranie logów obecności dla danego pracownika w zadanym okresie z tabeli shifts
            shifts_data = db.query(models.Shift).filter(
                models.Shift.employee_id == employee.id,
                models.Shift.start_time >= datetime.combine(date_from_obj, datetime.min.time()),
                models.Shift.start_time <= datetime.combine(date_to_obj, datetime.max.time())
            ).all()
            
            # Obliczenie łącznego czasu pracy
            total_minutes = 0
            completed_shifts = 0
            
            for shift in shifts_data:
                if shift.stop_time:
                    start = shift.start_time
                    stop = shift.stop_time
                    diff = stop - start
                    total_minutes += diff.seconds // 60
                    completed_shifts += 1
            
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            # Dodajemy dane o dniach pracy, sobotach, niedzielach i świętach
            days_present = len(set([shift.start_time.date() for shift in shifts_data]))
            saturdays = len(set([shift.start_time.date() for shift in shifts_data if shift.start_time.date().weekday() == 5]))
            sundays = len(set([shift.start_time.date() for shift in shifts_data if shift.start_time.date().weekday() == 6]))
            holidays = 0  # Do implementacji później - wymaga listy świąt
            
            # Pobierz stawkę godzinową pracownika
            rate = employee.hourly_rate if hasattr(employee, "hourly_rate") else 0
            
            result.append({
                "id": employee.id,
                "name": employee.name,
                "total_time": f"{hours}h {minutes}min",
                "total_hours": hours + (minutes / 60),
                "completed_shifts": completed_shifts,
                "avg_shift": f"{total_minutes // completed_shifts // 60}h {total_minutes // completed_shifts % 60}min" if completed_shifts > 0 else "0h 0min",
                "days_present": days_present,
                "saturdays": saturdays,
                "sundays": sundays,
                "holidays": holidays,
                "rate": rate
            })
        
        return result
    except Exception as e:
        print(f"Błąd podczas pobierania podsumowania: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

@router.get("/api/attendance_by_date")
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
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        db = next(get_db())
        
        # Pobranie logów obecności z danego dnia
        start_of_day = datetime.combine(date_obj, datetime.min.time())
        end_of_day = datetime.combine(date_obj, datetime.max.time())
        
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

@router.get("/api/active_workers")
async def get_active_workers(request: Request):
    """Pobierz listę aktywnych pracowników"""
    logger.debug("Pobieranie listy aktywnych pracowników...")
    # Zrezygnujmy z wymogu autoryzacji dla tego endpointu
    # user = request.session.get("user")
    # if not user:
    #     return JSONResponse(
    #         status_code=401,
    #         content={"detail": "Nieautoryzowany dostęp"}
    #     )
    
    try:
        db = next(get_db())
        try:
            # Pobierz pracowników którzy rozpoczęli pracę i nie zakończyli jej jeszcze
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # Debug - wypisz czas początkowy dzisiaj
            print(f"DEBUG: Szukam pracowników aktywnych od {today_start}")
            
            # Pokaż wszystkie aktywne zmiany (nie tylko z dzisiaj)
            shifts = db.query(models.Shift).filter(
                models.Shift.stop_time == None            ).all()
            
            print(f"DEBUG: Znalazłem {len(shifts)} aktywnych zmian")
            
            active_workers = []
            for shift in shifts:
                employee = db.query(models.Employee).filter(models.Employee.id == shift.employee_id).first()
                if employee:
                    active_workers.append({
                        "id": employee.id,
                        "name": employee.name,
                        "start_time": shift.start_time.strftime("%H:%M") if shift.start_time else "-",
                        "shift_id": shift.id,
                        "location": shift.start_location or "Nieznana",
                        "status": "online",  # Dodany status online
                        "coordinates": {
                            "lat": shift.start_latitude,
                            "lon": shift.start_longitude
                        } if shift.start_latitude and shift.start_longitude else None
                    })
            
            # Jeśli brak aktywnych pracowników, zwróć pustą listę
            if not active_workers:
                return []
            
            return active_workers
        finally:
            # Zawsze zamknij połączenie
            db.close()
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania aktywnych pracowników: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Przekierowania dla starych endpointów
@router.get("/attendance_by_date")
async def get_attendance_by_date_redirect(request: Request, date: str):
    """Przekierowanie dla endpointu /attendance_by_date"""
    print(f"Przekierowuję /attendance_by_date do /api/attendance_by_date dla daty {date}")
    return await get_attendance_by_date(request, date)

@router.get("/attendance_details")
async def get_attendance_details_redirect(request: Request, worker_id: str, date_from: str, date_to: str):
    """Przekierowanie dla endpointu /attendance_details"""
    print(f"Przekierowuję /attendance_details do /api/attendance_details dla pracownika {worker_id}, okres {date_from} - {date_to}")
    return await get_attendance_details(request, worker_id, date_from, date_to)

@router.get("/attendance_summary")
async def get_attendance_summary_redirect(request: Request, date_from: str, date_to: str):
    """Przekierowanie dla endpointu /attendance_summary"""
    print(f"Przekierowuję /attendance_summary do /api/attendance_summary dla okresu {date_from} - {date_to}")
    return await get_attendance_summary(request, date_from, date_to)

@router.get("/active_workers")
async def get_active_workers_redirect(request: Request):
    """Przekierowanie dla endpointu /active_workers"""
    print("Przekierowuję /active_workers do /api/active_workers")
    return await get_active_workers(request)
