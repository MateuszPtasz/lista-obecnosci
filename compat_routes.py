"""
Moduł kompatybilności dla starych ścieżek API
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from database import get_db
import models
from work_models import WorkSession
from typing import Dict, Any, List, Optional
import logging

# Konfiguracja logowania
logger = logging.getLogger("compat_api")

router = APIRouter()

@router.post("/api/start")
def start_work_compat(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Kompatybilność wsteczna dla starej ścieżki API rozpoczęcia pracy
    Przekierowuje do nowej funkcji start_work w work_routes.py
    """
    try:
        from work_routes import start_work
        
        # Konwersja danych do formatu nowego API
        employee_id = data.get("worker_id") or data.get("employee_id")
        lat = data.get("lat")
        lon = data.get("lon")
        
        # Sprawdź, czy mamy zagnieżdżony obiekt lokalizacji
        if not lat and "lokalizacja_start" in data:
            lat = data["lokalizacja_start"].get("lat", 0.0)
            lon = data["lokalizacja_start"].get("lon", 0.0)
        
        new_data = {
            "employee_id": str(employee_id),
            "lat": lat,
            "lon": lon
        }
        
        logger.info(f"Kompatybilność /api/start - przekształcone dane: {new_data}")
        
        # Wywołaj nową funkcję z przekształconymi danymi (która nie jest asynchroniczna)
        return start_work(request, new_data, db)
    except Exception as e:
        logger.error(f"Error in compatibility layer for /api/start: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/stop")
def stop_work_compat(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Kompatybilność wsteczna dla starej ścieżki API zakończenia pracy
    Przekierowuje do nowej funkcji end_work w work_routes.py
    """
    try:
        from work_routes import end_work
        
        # Konwersja danych do formatu nowego API
        employee_id = data.get("worker_id") or data.get("employee_id")
        session_id = data.get("session_id")
        lat = data.get("lat")
        lon = data.get("lon")
        
        # Sprawdź, czy mamy zagnieżdżony obiekt lokalizacji
        if not lat and "lokalizacja_stop" in data:
            lat = data["lokalizacja_stop"].get("lat", 0.0)
            lon = data["lokalizacja_stop"].get("lon", 0.0)
        
        # Jeśli nie ma session_id, znajdź aktywną sesję dla pracownika
        if not session_id and employee_id:
            active_session = db.query(WorkSession).filter(
                WorkSession.employee_id == str(employee_id),
                WorkSession.end_time == None
            ).first()
            
            if active_session:
                session_id = active_session.id
        
        new_data = {
            "employee_id": str(employee_id) if employee_id else None,
            "session_id": session_id,
            "lat": lat,
            "lon": lon
        }
        
        logger.info(f"Kompatybilność /api/stop - przekształcone dane: {new_data}")
        
        # Wywołaj nową funkcję z przekształconymi danymi (która nie jest asynchroniczna)
        return end_work(request, new_data, db)
    except Exception as e:
        logger.error(f"Error in compatibility layer for /api/stop: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/workers_status")
def workers_status_compat(request: Request, db: Session = Depends(get_db)):
    """
    Kompatybilność wsteczna dla starej ścieżki API statusu pracowników
    Zwraca listę aktywnych pracowników w formacie dla starego API
    """
    try:
        # Tymczasowo zwracamy pustą listę zamiast próbować używać problematycznej funkcji
        logger.info("Endpoint /api/workers_status - zwracam awaryjnie pustą listę")
        return []
        
        # Poniższy kod jest tymczasowo wyłączony
        """
        from work_routes import get_active_workers
        
        # Wywołaj nową funkcję (która nie jest asynchroniczna)
        return get_active_workers(request, db)
        """
    except Exception as e:
        logger.error(f"Error in compatibility layer for /api/workers_status: {str(e)}")
        # Zwróć pustą listę zamiast błędu 500
        return []
