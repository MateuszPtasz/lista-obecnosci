#!/usr/bin/env python
# check_active_shifts.py - skrypt sprawdzający aktywne zmiany

import os
import sys
import datetime as dt

# Dodaj ścieżkę projektu do sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importy
try:
    import models
    from database import get_db
except ImportError as e:
    print(f"Błąd importu: {e}")
    sys.exit(1)

def main():
    try:
        db = next(get_db())
        active_shifts = db.query(models.Shift).filter(
            models.Shift.stop_time == None
        ).all()
        
        print(f"Aktywne zmiany: {len(active_shifts)}")
        
        for shift in active_shifts:
            # Znajdź pracownika
            employee = db.query(models.Employee).filter(
                models.Employee.id == shift.employee_id
            ).first()
            
            employee_name = employee.name if employee else "Nieznany"
            
            # Oblicz czas trwania
            duration = dt.datetime.now() - shift.start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            print(f"  ID: {shift.id}, Pracownik: {shift.employee_id} ({employee_name})")
            print(f"    Start: {shift.start_time}")
            print(f"    Czas trwania: {hours}h {minutes}min")
            print(f"    Lokalizacja: {shift.start_location}")
    
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    main()
