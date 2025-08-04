"""
Skrypt do naprawy problemu z widokiem aktywnych pracowników.
Problem: Pracownicy z aktywnymi zmianami nie są widoczni jako aktywni.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from database import get_db
import models
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("app")

def get_fixed_active_workers():
    """Poprawiona funkcja pobierająca aktywnych pracowników"""
    try:
        db = next(get_db())
        try:
            # Pokaż wszystkie aktywne zmiany (nie tylko z dzisiaj)
            shifts = db.query(models.Shift).filter(
                models.Shift.stop_time == None
            ).all()
            
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
                        "status": "online",  # Dodaję jawnie status "online"
                        "coordinates": {
                            "lat": shift.start_latitude,
                            "lon": shift.start_longitude
                        } if shift.start_latitude and shift.start_longitude else None
                    })
                else:
                    # Jeśli nie znaleziono pracownika, wyświetl ID jako nazwę
                    active_workers.append({
                        "id": shift.employee_id,
                        "name": f"Pracownik {shift.employee_id}",
                        "start_time": shift.start_time.strftime("%H:%M") if shift.start_time else "-",
                        "shift_id": shift.id,
                        "location": shift.start_location or "Nieznana",
                        "status": "online",  # Dodaję jawnie status "online"
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
        raise e

def main():
    """Funkcja główna sprawdzająca stan aktywnych pracowników"""
    try:
        active_workers = get_fixed_active_workers()
        print("\nLista aktywnych pracowników (poprawiona):")
        for worker in active_workers:
            print(f"ID: {worker['id']}, Nazwa: {worker['name']}, Start: {worker['start_time']}, Status: {worker['status']}")
        
        # Sprawdź bazę danych bezpośrednio
        db = next(get_db())
        try:
            shifts = db.query(models.Shift).filter(
                models.Shift.stop_time == None
            ).all()
            
            print("\nAktywne zmiany (bezpośrednio z bazy):")
            for shift in shifts:
                employee = db.query(models.Employee).filter(models.Employee.id == shift.employee_id).first()
                employee_name = employee.name if employee else f"Nieznany ({shift.employee_id})"
                print(f"Zmiana ID: {shift.id}, Pracownik: {employee_name} (ID: {shift.employee_id}), Start: {shift.start_time}")
        finally:
            db.close()
    except Exception as e:
        print(f"Błąd: {str(e)}")

if __name__ == "__main__":
    main()
