from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from work_models import WorkSession
import logging

# Konfiguracja logowania
logger = logging.getLogger("debug_api")

router = APIRouter()

@router.get("/api/debug/active_sessions")
def debug_active_sessions(db: Session = Depends(get_db)):
    """Endpoint diagnostyczny - lista wszystkich aktywnych sesji"""
    try:
        # Pobierz wszystkie aktywne sesje pracy
        active_sessions = db.query(WorkSession).filter(
            WorkSession.end_time == None
        ).all()
        
        result = []
        for session in active_sessions:
            result.append({
                "id": session.id,
                "employee_id": session.employee_id,
                "start_time": session.start_time.isoformat() if session.start_time else None,
            })
        
        return result
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return {"error": str(e)}

@router.get("/api/debug/employees")
def debug_employees(db: Session = Depends(get_db)):
    """Endpoint diagnostyczny - lista wszystkich pracowników"""
    try:
        # Pobierz wszystkich pracowników
        employees = db.query(models.Employee).all()
        
        result = []
        for employee in employees:
            result.append({
                "id": employee.id,
                "name": f"{employee.first_name} {employee.last_name}" if hasattr(employee, 'first_name') else employee.name,
                "user_id": employee.user_id if hasattr(employee, 'user_id') else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return {"error": str(e)}

@router.get("/api/debug/check_employee/{employee_id}")
def debug_check_employee(employee_id: str, db: Session = Depends(get_db)):
    """Endpoint diagnostyczny - sprawdź pracownika po ID"""
    try:
        # Najpierw sprawdź, czy taki pracownik istnieje
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        
        if not employee:
            return {"exists": False, "error": f"Pracownik o ID {employee_id} nie istnieje"}
        
        # Jeśli istnieje, pobierz jego dane
        result = {
            "exists": True,
            "id": employee.id,
            "name": f"{employee.first_name} {employee.last_name}" if hasattr(employee, 'first_name') and employee.first_name else employee.name,
            "user_id": employee.user_id if hasattr(employee, 'user_id') else None,
            "attributes": {}
        }
        
        # Dodaj wszystkie dostępne atrybuty
        for attr in dir(employee):
            if not attr.startswith('_') and attr != 'metadata' and attr != 'registry':
                try:
                    value = getattr(employee, attr)
                    if not callable(value):
                        result["attributes"][attr] = str(value)
                except Exception as attr_err:
                    result["attributes"][attr] = f"Error: {str(attr_err)}"
        
        return result
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return {"error": str(e)}
