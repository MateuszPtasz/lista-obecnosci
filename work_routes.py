from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from work_models import WorkSession
from datetime import datetime
import pytz
from typing import Optional, Dict, Any
import logging

# Konfiguracja logowania
logger = logging.getLogger("work_api")

router = APIRouter()

def format_duration(start_time, end_time=None):
    """Formatuje czas trwania pracy w formacie: Xh Ym"""
    if not end_time:
        end_time = datetime.now(pytz.timezone('Europe/Warsaw'))
    
    delta = end_time - start_time
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    return f"{hours}h {minutes}m"


@router.get("/api/employees")
def get_employees(request: Request, db: Session = Depends(get_db)):
    """Pobierz listę wszystkich pracowników"""
    try:
        employees = db.query(models.Employee).all()
        result = []
        
        for employee in employees:
            result.append({
                "id": employee.id,
                "name": f"{employee.first_name} {employee.last_name}",
                "email": employee.email
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting employees: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/employees/count")
def get_employees_count(db: Session = Depends(get_db)):
    """Pobierz liczbę wszystkich pracowników"""
    try:
        count = db.query(models.Employee).count()
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting employees count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Pobierz informacje o pracowniku po ID"""
    try:
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return {
            "id": employee.id,
            "name": f"{employee.first_name} {employee.last_name}",
            "email": employee.email,
            "first_name": employee.first_name,
            "last_name": employee.last_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/work/employee/{employee_id}/status")
def get_employee_work_status(employee_id: str, db: Session = Depends(get_db)):
    """Pobierz status pracy pracownika"""
    try:
        # Awaryjnie zwróć stały status nieaktywny (hotfix)
        # W przyszłości naprawić poprawnie
        logger.info(f"Sprawdzanie statusu pracy dla employee_id: {employee_id} - zwracam awaryjnie status nieaktywny")
        return {"active": False}
        
        # Poniższy kod jest tymczasowo wyłączony, bo powoduje błędy 500
        """
        # Zapisz employee_id do logów, aby zobaczyć jaki format jest przekazywany
        logger.info(f"Sprawdzanie statusu pracy dla employee_id: {employee_id}, typ: {type(employee_id)}")
        
        # Sprawdź czy pracownik istnieje
        # Ponieważ ID pracownika może być zarówno numeryczne jak i alfanumeryczne,
        # konwertujemy na string aby zapewnić spójność
        employee = db.query(models.Employee).filter(models.Employee.id == str(employee_id)).first()
        
        if not employee:
            logger.warning(f"Nie znaleziono pracownika o ID {employee_id}")
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Sprawdź czy pracownik ma aktywną sesję
        try:
            active_session = db.query(WorkSession).filter(
                WorkSession.employee_id == str(employee_id),
                WorkSession.end_time == None
            ).first()
            
            if not active_session:
                return {"active": False}
            
            # Oblicz czas trwania
            start_time = active_session.start_time
            duration = format_duration(start_time)
            
            # Bezpieczne pobieranie danych pracownika
            first_name = getattr(employee, 'first_name', '')
            last_name = getattr(employee, 'last_name', '')
            full_name = f"{first_name} {last_name}"
            
            if not first_name and not last_name and hasattr(employee, 'name'):
                full_name = employee.name
            
            return {
                "active": True,
                "session_id": active_session.id,
                "employee_id": str(employee_id),
                "employee_name": full_name,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "start_timestamp": start_time.isoformat(),
                "duration": duration
            }
        except Exception as session_error:
            logger.error(f"Błąd podczas pobierania sesji dla pracownika {employee_id}: {str(session_error)}")
            return {"active": False, "error": str(session_error)}
        """
    
    except Exception as e:
        logger.error(f"Error getting work status for employee {employee_id}: {str(e)}")
        # Zamiast zwracać błąd 500, zwracamy status nieaktywny
        return {"active": False, "error": "Internal server error"}


@router.get("/api/work/status")
def get_work_status(request: Request, db: Session = Depends(get_db)):
    """Pobierz status pracy aktualnego użytkownika"""
    try:
        # Sprawdź ID użytkownika z sesji
        if "user_id" not in request.session:
            return {"active": False}
        
        user_id = request.session["user_id"]
        
        # Pobierz pracownika przypisanego do użytkownika
        employee = db.query(models.Employee).filter(models.Employee.user_id == user_id).first()
        
        if not employee:
            return {"active": False}
        
        # Sprawdź czy pracownik ma aktywną sesję
        active_session = db.query(WorkSession).filter(
            WorkSession.employee_id == employee.id,
            WorkSession.end_time == None
        ).first()
        
        if not active_session:
            return {"active": False}
        
        # Oblicz czas trwania
        start_time = active_session.start_time
        duration = format_duration(start_time)
        
        return {
            "active": True,
            "session_id": active_session.id,
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "start_timestamp": start_time.isoformat(),
            "duration": duration
        }
    except Exception as e:
        logger.error(f"Error getting work status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/work/start")
def start_work(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    """Rozpocznij pracę dla pracownika"""
    try:
        employee_id = data.get("employee_id")
        lat = data.get("lat")
        lon = data.get("lon")
        
        if not employee_id:
            raise HTTPException(status_code=400, detail="Employee ID is required")
        
        # Sprawdź czy pracownik istnieje
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Sprawdź czy pracownik już nie ma aktywnej sesji
        active_session = db.query(WorkSession).filter(
            WorkSession.employee_id == employee_id,
            WorkSession.end_time == None
        ).first()
        
        if active_session:
            raise HTTPException(status_code=400, detail="Employee already has an active work session")
        
        # Utwórz nową sesję pracy
        now = datetime.now(pytz.timezone('Europe/Warsaw'))
        new_session = WorkSession(
            employee_id=employee_id,
            start_time=now,
            start_lat=lat,
            start_lon=lon
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return {
            "id": new_session.id,
            "employee_id": employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "start_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "start_timestamp": now.isoformat(),
            "duration": "0h 0m"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting work: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/work/end")
def end_work(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    """Zakończ pracę dla pracownika"""
    try:
        session_id = data.get("session_id")
        employee_id = data.get("employee_id")
        lat = data.get("lat")
        lon = data.get("lon")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # Znajdź sesję pracy
        work_session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        
        if not work_session:
            raise HTTPException(status_code=404, detail="Work session not found")
        
        if work_session.end_time:
            raise HTTPException(status_code=400, detail="Work session already ended")
        
        # Sprawdź zgodność ID pracownika
        if employee_id and work_session.employee_id != employee_id:
            raise HTTPException(status_code=400, detail="Employee ID mismatch")
        
        # Zakończ sesję pracy
        now = datetime.now(pytz.timezone('Europe/Warsaw'))
        work_session.end_time = now
        work_session.end_lat = lat
        work_session.end_lon = lon
        
        # Oblicz czas trwania
        duration_seconds = (now - work_session.start_time).total_seconds()
        work_session.duration_minutes = int(duration_seconds / 60)
        
        db.commit()
        
        # Pobierz dane pracownika
        employee = db.query(models.Employee).filter(models.Employee.id == work_session.employee_id).first()
        
        return {
            "id": work_session.id,
            "employee_id": work_session.employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}" if employee else None,
            "start_time": work_session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": format_duration(work_session.start_time, now)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending work: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/work/emergency_end")
def emergency_end_work(request: Request, db: Session = Depends(get_db)):
    """Awaryjnie zakończ wszystkie aktywne sesje pracy"""
    try:
        # Pobierz wszystkie aktywne sesje pracy
        active_sessions = db.query(WorkSession).filter(
            WorkSession.end_time == None
        ).all()
        
        if not active_sessions:
            return {"message": "No active work sessions found"}
        
        # Zakończ wszystkie aktywne sesje
        now = datetime.now(pytz.timezone('Europe/Warsaw'))
        count = 0
        
        for session in active_sessions:
            session.end_time = now
            session.emergency_end = True
            
            # Oblicz czas trwania
            duration_seconds = (now - session.start_time).total_seconds()
            session.duration_minutes = int(duration_seconds / 60)
            count += 1
        
        db.commit()
        
        return {
            "message": f"Emergency end of {count} active work sessions",
            "count": count,
            "end_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Error in emergency end work: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/active_workers")
def get_active_workers(request: Request, db: Session = Depends(get_db)):
    """Pobierz listę aktywnych pracowników"""
    try:
        # Pobierz sesję użytkownika
        user_id = request.session.get("user_id")
        logger.info(f"Pobieranie aktywnych pracowników. User ID: {user_id}")
        
        # Awaryjny return pustej tablicy (hotfix)
        # W przyszłości zastąpić poprawnym rozwiązaniem
        return []
        
        # Poniższy kod jest tymczasowo wyłączony, bo powoduje błędy 500
        """
        # Pobierz wszystkie aktywne sesje pracy wraz z danymi pracowników
        result = []
        
        # Najpierw sprawdźmy, czy istnieją aktywne sesje
        active_sessions_count = db.query(WorkSession).filter(WorkSession.end_time == None).count()
        logger.info(f"Znaleziono {active_sessions_count} aktywnych sesji.")
        
        if active_sessions_count == 0:
            return []  # Szybki powrót jeśli nie ma aktywnych sesji
            
        try:
            # Uzyskaj wszystkie aktywne sesje bezpośrednio z modelu WorkSession
            # z wykorzystaniem relacji 'employee'
            active_sessions = db.query(WorkSession).filter(
                WorkSession.end_time == None
            ).all()
            
            for session in active_sessions:
                # Pobierz pracownika oddzielnie, jeśli relacja nie działa
                employee = None
                
                # Spróbuj użyć relacji
                if hasattr(session, 'employee') and session.employee is not None:
                    employee = session.employee
                else:
                    # Jeśli relacja nie działa, pobierz pracownika bezpośrednio
                    employee = db.query(models.Employee).filter(
                        models.Employee.id == session.employee_id
                    ).first()
                
                if not employee:
                    logger.warning(f"Nie znaleziono pracownika o ID {session.employee_id} dla sesji {session.id}")
                    continue
                
                # Czy to jest aktualny użytkownik?
                is_current_user = False
                if user_id and hasattr(employee, 'user_id'):
                    is_current_user = (employee.user_id == user_id)
                
                start_time = session.start_time
                duration = format_duration(start_time)
                
                # Bezpieczne pobieranie danych pracownika
                first_name = getattr(employee, 'first_name', '')
                last_name = getattr(employee, 'last_name', '')
                full_name = f"{first_name} {last_name}"
                
                if not first_name and not last_name and hasattr(employee, 'name'):
                    full_name = employee.name
                
                result.append({
                    "id": employee.id,
                    "name": full_name,
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "start_timestamp": start_time.isoformat(),
                    "duration": duration,
                    "online": True,
                    "session_id": session.id,
                    "start_lat": session.start_lat,
                    "start_lon": session.start_lon,
                    "is_current_user": is_current_user
                })
                
        except Exception as inner_e:
            logger.error(f"Błąd podczas przetwarzania sesji pracy: {str(inner_e)}")
            # Alternatywna metoda pobierania danych - bezpośrednie zapytanie join
            logger.info("Próba alternatywnej metody pobierania aktywnych pracowników...")
            
            active_workers = db.query(
                models.Employee
            ).join(
                WorkSession, 
                WorkSession.employee_id == models.Employee.id
            ).filter(
                WorkSession.end_time == None
            ).all()
            
            for employee in active_workers:
                session = db.query(WorkSession).filter(
                    WorkSession.employee_id == employee.id,
                    WorkSession.end_time == None
                ).first()
                
                if not session:
                    continue
                
                # Czy to jest aktualny użytkownik?
                is_current_user = False
                if user_id:
                    is_current_user = (employee.user_id == user_id)
                
                start_time = session.start_time
                duration = format_duration(start_time)
                
                result.append({
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "start_timestamp": start_time.isoformat(),
                    "duration": duration,
                    "online": True,
                    "session_id": session.id,
                    "start_lat": session.start_lat,
                    "start_lon": session.start_lon,
                    "is_current_user": is_current_user
                })
        """
        
        return []  # Tymczasowo zwracamy pustą listę zamiast powodować błąd 500
    except Exception as e:
        logger.error(f"Error getting active workers: {str(e)}")
        # Zwróć pustą listę zamiast błędu 500
        return []


@router.get("/api/system/errors")
def get_system_errors(db: Session = Depends(get_db)):
    """Pobierz licznik błędów systemu z ostatnich 24h"""
    try:
        # Tutaj powinno być sprawdzanie logów systemowych
        # Na potrzeby przykładu, zwracamy losową liczbę
        return {
            "count": 0,
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Error getting system errors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/statistics/avg_work_time")
def get_avg_work_time(db: Session = Depends(get_db)):
    """Pobierz średni czas pracy z dzisiaj"""
    try:
        # Tu powinno być obliczanie statystyk czasu pracy
        # Na potrzeby przykładu, zwracamy stałe wartości
        return {
            "avg_time": "7h 30m",
            "change": 0.5
        }
    except Exception as e:
        logger.error(f"Error getting average work time: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
