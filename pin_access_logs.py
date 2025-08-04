"""
Moduł obsługujący dostęp do logów PIN
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from database import get_db
import models
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.get("/api/pin_access_logs")
async def get_pin_access_logs(
    request: Request, 
    worker_id: Optional[str] = None, 
    date_from: Optional[str] = None, 
    date_to: Optional[str] = None, 
    limit: int = 100
):
    """Pobiera logi dostępu PIN pracowników"""
    print("Pobieranie logów dostępu PIN")
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Nieautoryzowany dostęp")
        
    try:
        db = next(get_db())
        query = """
            SELECT * FROM pin_logs
            WHERE 1=1
        """
        params = []
        
        if worker_id:
            query += " AND worker_id = ?"
            params.append(worker_id)
            
        if date_from:
            query += " AND datetime(created_at) >= datetime(?)"
            params.append(date_from)
            
        if date_to:
            query += " AND datetime(created_at) <= datetime(?)"
            params.append(date_to)
            
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        try:
            logs = db.execute(query, params).fetchall()
            
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
            # Jeśli tabela nie istnieje lub inny błąd
            print(f"Błąd podczas pobierania logów dostępu PIN: {str(e)}")
            return {
                "success": False,
                "error": f"Błąd serwera: {str(e)}",
                "logs": []
            }
            
    except Exception as e:
        print(f"Błąd podczas pobierania logów dostępu PIN: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")
