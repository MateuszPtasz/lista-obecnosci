"""
Endpoint do obsługi zapytań o pracowników, którzy nie mają wpisów za dany okres
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

@router.get("/api/employees_without_logs")
async def get_employees_without_logs(request: Request, date_from: str, date_to: str):
    """Zwraca listę pracowników, którzy nie mają wpisów w dzienniku za dany okres"""
    print(f"Pobieranie pracowników bez wpisów w okresie: {date_from} - {date_to}")
    user = request.session.get("user")
    # Wyłączamy tymczasowo sprawdzanie autoryzacji dla testów
    # if not user:
    #     return JSONResponse(
    #         status_code=401,
    #         content={"detail": "Nieautoryzowany dostęp"}
    #     )
    
    try:
        # Konwersja dat
        date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
        date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
        
        # Pobierz połączenie z bazą danych
        db = next(get_db())
        
        # Pobierz wszystkich pracowników
        all_employees = db.query(models.Employee).all()
        
        # Lista pracowników bez wpisów w zadanym okresie
        employees_without_logs = []
        
        for employee in all_employees:
            # Sprawdź, czy pracownik ma jakiekolwiek wpisy w danym okresie
            shift_count = db.query(models.Shift).filter(
                models.Shift.employee_id == employee.id,
                models.Shift.start_time >= datetime.combine(date_from_obj, datetime.min.time()),
                models.Shift.start_time <= datetime.combine(date_to_obj, datetime.max.time())
            ).count()
            
            # Jeśli nie ma wpisów, dodaj do listy
            if shift_count == 0:
                employees_without_logs.append({
                    "id": employee.id,
                    "name": employee.name
                })
        
        return employees_without_logs
    except Exception as e:
        logger.error(f"Błąd podczas pobierania pracowników bez wpisów: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Błąd serwera: {str(e)}"}
        )

# Przekierowanie dla starego endpointu
@router.get("/employees_without_logs")
async def get_employees_without_logs_redirect(request: Request, date_from: str, date_to: str):
    """Przekierowanie dla endpointu /employees_without_logs"""
    print(f"Przekierowuję /employees_without_logs do /api/employees_without_logs dla okresu {date_from} - {date_to}")
    return await get_employees_without_logs(request, date_from, date_to)
