"""
Skrypt do testowania i debugowania widoku aktywnych pracowników.
Symuluje wywołanie endpointu /api/active_workers bezpośrednio w kodzie.
"""
from datetime import datetime, timedelta
import models
from database import get_db

def test_get_active_workers():
    """Testowa implementacja funkcji get_active_workers"""
    try:
        db = next(get_db())
        try:
            # Pokaż wszystkie aktywne zmiany
            shifts = db.query(models.Shift).filter(
                models.Shift.stop_time == None
            ).all()
            
            print(f"DEBUG: Znalazłem {len(shifts)} aktywnych zmian")
            
            active_workers = []
            for shift in shifts:
                employee = db.query(models.Employee).filter(models.Employee.id == shift.employee_id).first()
                if employee:
                    # Oryginalna wersja (bez statusu)
                    active_worker_orig = {
                        "id": employee.id,
                        "name": employee.name,
                        "start_time": shift.start_time.strftime("%H:%M") if shift.start_time else "-",
                        "shift_id": shift.id,
                        "location": shift.start_location or "Nieznana",
                        "coordinates": {
                            "lat": shift.start_latitude,
                            "lon": shift.start_longitude
                        } if shift.start_latitude and shift.start_longitude else None
                    }
                    
                    # Nowa wersja (z jawnym statusem)
                    active_worker_new = {
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
                    }
                    
                    active_workers.append((active_worker_orig, active_worker_new))
                else:
                    print(f"UWAGA: Nie znaleziono pracownika o ID {shift.employee_id}")
            
            return active_workers
        finally:
            db.close()
    except Exception as e:
        print(f"Błąd: {str(e)}")
        return []

def main():
    print(f"=== Test widoku aktywnych pracowników - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    active_workers = test_get_active_workers()
    
    print(f"Znaleziono {len(active_workers)} aktywnych pracowników\n")
    
    for i, (worker_orig, worker_new) in enumerate(active_workers, 1):
        print(f"=== Pracownik {i} ===")
        print("ORYGINALNA WERSJA (bez statusu):")
        for key, value in worker_orig.items():
            print(f"  {key}: {value}")
        
        print("\nNOWA WERSJA (z jawnym statusem):")
        for key, value in worker_new.items():
            print(f"  {key}: {value}")
        
        print("\n")

if __name__ == "__main__":
    main()
